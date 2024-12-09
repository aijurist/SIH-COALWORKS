from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the output schema
class QueryModel(BaseModel):
    query_validity: bool = Field(description="Validity of the query asked. True is Valid, False is Invalid.")
    reason: str = Field(description="Explanation of why the query is valid or invalid.")

def user_query_validator(user_query: str):
    # Initialize JSON Output Parser
    parser = JsonOutputParser(pydantic_object=QueryModel)

    # Initialize the LLM
    llm = GoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))

    # Define the Prompt
    prompt = PromptTemplate(
        template="""You are a domain expert in coal mine operations and form design. Your task is to evaluate the validity of a given query related to generating a form for coal mine operations. 

            Criteria for Evaluation:
            1. Validity of Query:
            - If the query lacks sufficient information about the operation or process, mark it as invalid.
            - If the query is unrelated to coal mine operations, mark it as invalid.
            - Otherwise, mark the query as valid.

            2. Guidelines:
            - A valid query should include details about coal mine operations, such as specific tasks, processes, or safety standards.
            - An invalid query may be too vague (e.g., "Generate a form") or unrelated (e.g., "Form for grocery store operations").

            Query: {query}

            {format_instructions}""",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Create the LLM Chain
    chain = prompt | llm | parser
    
    try:
        response = chain.invoke({"query": user_query})
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
