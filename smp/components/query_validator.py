from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, field_validator
from langchain_core.prompts import PromptTemplate
from typing import Dict, Union, Optional
import os
from dotenv import load_dotenv

class QueryValidator(BaseModel):
    query_validity: bool = Field(description="The validity of the user query asked, 1(true) for valid, 0(false) for invalid")
    reason: Optional[str] = Field(description="The reason for the decision of the validity logic")
    
    @field_validator('query_validity')
    def query_validity(cls, value):
        values = [True, False, 0, 1, "true", "false"]
        
        if value not in values:
            raise ValueError("Invalid value has been given for the field query_validity. Expected 'True' or 'False")
        return value
    
def validate_query(user_query):
    llm = GoogleGenerativeAI(model='gemini-1.5-pro', google_api_key=os.getenv('GOOGLE_API_KEY'))
    parser = JsonOutputParser(pydantic_object=QueryValidator)
    
    prompt = PromptTemplate(
        template="""Evaluate the user query for validity in generating a Safety Management Plan (SMP) for a coal mining activity:

        Evaluation Criteria:
        - Must specify a clear coal mining activity or process
        - Must provide sufficient context for safety planning
        - Must demonstrate intent for safety management

        Determine if the query is VALID or INVALID based on:
        - Specificity of the mining activity mentioned
        - Clarity of safety management needs
        - Relevance to coal mine operations

        User Query: {query}

        {format_instructions}""",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
    
    chain = prompt | llm | parser
    
    res = chain.invoke({
        "query": user_query
    })
    
    return res