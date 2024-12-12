import re
import traceback
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Literal, Type, TypeVar

import altair as alt
import commentjson
import jsonschema
import pandas as pd
import pydantic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from plotly.graph_objs import Figure
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY is not set. Check your .env file.")

from chatbot.agent.visualization.dataset_description import description
from chatbot.agent.visualization.helper import delete_null_field
from chatbot.agent.visualization.prompts import (
    JSON_TAG,
    error_correction_prompt,
    explanation_prompt,
    system_prompt,
)
from chatbot.agent.visualization.render import draw_plotly, draw_altair
from chatbot.agent.visualization.schema import PlotConfig, ResponseType, get_schema_of_chart_config

_logger = getLogger(__name__)

T = TypeVar("T", bound=pydantic.BaseModel)
ModelDeserializer = Callable[[dict[str, Any]], T]

# These errors are caught within the application.
_APPLICATION_ERRORS = (
    pydantic.ValidationError,
    jsonschema.ValidationError,
    ValueError,
    KeyError,
    AssertionError,
)


@dataclass(frozen=True)
class Plot:
    figure: alt.Chart | Figure | None
    config: PlotConfig | dict[str, Any] | pydantic.BaseModel | None
    response_type: ResponseType
    explanation: str


class Chat2PlotBase:
    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        raise NotImplementedError()

    def __call__(
        self, q: str, config_only: bool = False, show_plot: bool = False
    ) -> Plot:
        return self.query(q, config_only, show_plot)


class Chat2Plot(Chat2PlotBase):
    def __init__(
        self,
        df: pd.DataFrame,
        chart_schema: Literal["simple"] | Type[pydantic.BaseModel],
        *,
        chat: BaseChatModel | None = None,
        language: str | None = None,
        description_strategy: str = "head",
        verbose: bool = False,
        custom_deserializer: ModelDeserializer | None = None,
    ):
        self._target_schema: Type[pydantic.BaseModel] = (
            PlotConfig if chart_schema == "simple" else chart_schema  # type: ignore
        )

        chat_model = _get_or_default_chat_model(chat)

        # Simplified initialization without conversation history
        self._chat = chat_model
        self._df = df
        self._verbose = verbose
        self._custom_deserializer = custom_deserializer
        self._language = language
        self._description_strategy = description_strategy

        # Prepare the initial system prompt
        self._system_prompt = system_prompt(
            "simple", 
            False,  # function_call removed 
            language, 
            self._target_schema
        ).format(
            dataset=description(df, description_strategy)
        )

    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        # Combine system prompt and user query
        full_prompt = f"{self._system_prompt}\n\n{q}"

        try:
            if self._verbose:
                _logger.info(f"request: {q}")

            # Send the full prompt directly
            raw_response = self._chat.invoke(full_prompt).content

            if self._verbose:
                _logger.info(f"first response: {raw_response}")

            return self._parse_response(q, raw_response, config_only, show_plot)
        
        except _APPLICATION_ERRORS as e:
            if self._verbose:
                _logger.warning(traceback.format_exc())
            
            msg = e.message if isinstance(e, jsonschema.ValidationError) else str(e)
            error_correction = error_correction_prompt(False).format(
                error_message=msg,
            )
            
            # Prepare corrected prompt
            corrected_full_prompt = f"{full_prompt}\n\n{error_correction}"

            try:
                corrected_response = self._chat.invoke(corrected_full_prompt).content
                
                if self._verbose:
                    _logger.info(f"retry response: {corrected_response}")

                return self._parse_response(
                    q, corrected_response, config_only, show_plot
                )
            except _APPLICATION_ERRORS as e:
                if self._verbose:
                    _logger.warning(e)
                    _logger.warning(traceback.format_exc())
                
                return Plot(
                    None,
                    None,
                    ResponseType.FAILED_TO_RENDER,
                    "",
                )

    def _parse_response(
        self, q: str, response: str, config_only: bool, show_plot: bool
    ) -> Plot:
        try:
            explanation, json_data = parse_json(response)
        except Exception as e:
            raise ValueError(f"Failed to parse response: {e}")

        try:
            if self._custom_deserializer:
                config = self._custom_deserializer(json_data)
            else:
                config = self._target_schema.parse_obj(json_data)
        except _APPLICATION_ERRORS:
            _logger.warning(traceback.format_exc())
            # To reduce the number of failure cases as much as possible,
            # only check against the json schema when instantiation fails.
            jsonschema.validate(json_data, self._target_schema.schema())
            raise

        if self._verbose:
            _logger.info(config)

        if config_only or not isinstance(config, PlotConfig):
            return Plot(
                None, config, ResponseType.SUCCESS, explanation
            )

        figure = draw_plotly(self._df, config, show_plot)
        return Plot(
            figure, config, ResponseType.SUCCESS, explanation
        )


class Chat2Vega(Chat2PlotBase):
    def __init__(
        self,
        df: pd.DataFrame,
        chat: BaseChatModel | None = None,
        language: str | None = None,
        description_strategy: str = "head",
        verbose: bool = False,
    ):
        self._chat = _get_or_default_chat_model(chat)
        self._system_prompt = system_prompt(
            "vega", False, language, None
        ).format(
            dataset=description(df, description_strategy)
        )
        self._df = df
        self._verbose = verbose

    def query(self, q: str, config_only: bool = False, show_plot: bool = False) -> Plot:
        # Combine system prompt and user query
        full_prompt = f"{self._system_prompt}\n\n{q}"

        res = self._chat.invoke(full_prompt)

        try:
            explanation, config = parse_json(res.content)
            if "data" in config:
                del config["data"]
            if self._verbose:
                _logger.info(config)
        except _APPLICATION_ERRORS:
            _logger.warning(f"failed to parse LLM response: {res}")
            _logger.warning(traceback.format_exc())
            return Plot(
                None, None, ResponseType.UNKNOWN, res.content
            )

        if config_only:
            return Plot(
                None, config, ResponseType.SUCCESS, explanation
            )

        try:
            plot = draw_altair(self._df, config, show_plot)
            return Plot(
                plot, config, ResponseType.SUCCESS, explanation
            )
        except _APPLICATION_ERRORS:
            _logger.warning(traceback.format_exc())
            return Plot(
                None,
                config,
                ResponseType.FAILED_TO_RENDER,
                explanation,
            )


def chat2plot(
    df: pd.DataFrame,
    schema_definition: Literal["simple", "vega"] | Type[pydantic.BaseModel] = "simple",
    chat: BaseChatModel | None = None,
    language: str | None = None,
    description_strategy: str = "head",
    custom_deserializer: ModelDeserializer | None = None,
    verbose: bool = False,
) -> Chat2PlotBase:
    """Create Chat2Plot instance.

    Args:
        df: Data source for visualization.
        schema_definition: Type of json format; "vega" for vega-lite compliant json, "simple" for chat2plot built-in
              data structure. If you want a custom schema definition, pass a type inheriting from pydantic.BaseModel
              as your own chart setting.
        chat: The chat instance for interaction with LLMs.
              If omitted, a default Google Generative AI model will be used.
        language: Language of explanations. If not specified, it will be automatically inferred from user prompts.
        description_strategy: Type of how the information in the dataset is embedded in the prompt.
              Defaults to "head" which embeds the contents of df.head(5) in the prompt.
              "dtypes" sends only columns and types to LLMs and does not send the contents of the dataset,
              which allows for privacy but may reduce accuracy.
        custom_deserializer: A custom function to convert the json returned by the LLM into a object.
        verbose: If `True`, chat2plot will output logs.

    Returns:
        Chat instance.
    """

    if schema_definition == "simple":
        return Chat2Plot(
            df,
            "simple",
            chat=chat,
            language=language,
            description_strategy=description_strategy,
            verbose=verbose,
            custom_deserializer=custom_deserializer,
        )
    if schema_definition == "vega":
        return Chat2Vega(df, chat, language, description_strategy, verbose)
    elif issubclass(schema_definition, pydantic.BaseModel):
        return Chat2Plot(
            df,
            schema_definition,
            chat=chat,
            language=language,
            description_strategy=description_strategy,
            verbose=verbose,
            custom_deserializer=custom_deserializer,
        )
    else:
        raise ValueError(
            f"schema_definition should be one of [simple, vega] or pydantic.BaseClass (given: {schema_definition})"
        )


def _extract_tag_content(s: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*)</{tag}>", s, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1)
    else:
        m = re.search(rf"<{tag}>(.*)<{tag}>", s, re.MULTILINE | re.DOTALL)
        if m:
            return m.group(1)
    return ""


def parse_json(content: str) -> tuple[str, dict[str, Any]]:
    """parse json and split contents by pre-defined tags"""
    json_part = _extract_tag_content(content, "json")  # type: ignore
    if not json_part:
        raise ValueError(f"failed to find {JSON_TAG[0]} and {JSON_TAG[1]} tags")

    explanation_part = _extract_tag_content(content, "explain")
    if not explanation_part:
        explanation_part = _extract_tag_content(content, "explanation")

    # LLM rarely generates JSON with comments, so use the commentjson package instead of json
    return explanation_part.strip(), delete_null_field(commentjson.loads(json_part))


def _get_or_default_chat_model(chat: BaseChatModel | None) -> BaseChatModel:
    if chat is None:
        return ChatGoogleGenerativeAI(
            model="gemini-pro", 
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY
        )
    return chat