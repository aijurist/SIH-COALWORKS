from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate

from pydantic import BaseModel, Field
from typing import Union, Dict, Optional
import json
import os 
from dotenv import load_dotenv

# custom modules
from new_form_builder.core.doc_reader import document_reader, authenticate_account
from new_form_builder.core.schema import FormSchemaFromDocument
from new_form_builder.core.knowledge import KnowledgeBase


class DocToForm:
    def __init__(self, google_api_key):
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=google_api_key
        )
        
        self.knowledge_base = KnowledgeBase(api_key=google_api_key or os.getenv('GOOGLE_API_KEY'))
        self.parser = JsonOutputParser(pydantic_object=FormSchemaFromDocument)
        
        with open('new_form_builder/template/outsourced/explosive.json', 'r') as file:
            self.example = json.load(file)
            
        self.prompt = PromptTemplate(
            template='''You are an advanced form builder tasked with generating a structured, clean, and user-friendly form based on extracted PDF text with the following critical considerations:
                Extracted PDF Text: {input_text}
                
                Input Context:
                - Source: Extracted PDF text
                - Potential Challenges:
                2. Unstructured or inconsistent text formatting
                3. Possible multilingual content
                4. Potential OCR or extraction artifacts

                Form Generation Guidelines:
                1. Text Preprocessing:
                - Remove unprintable characters
                - Normalize whitespace
                - Clean up any extraction artifacts
                - Translate to target language if necessary (default: English)
                - Do not assume fields which could be there because the operation is related to coal mines

                2. Field Extraction Criteria:
                - Identify key information fields
                - Standardize field names
                - Determine appropriate input types (text, number, date, dropdown, etc.)
                - Remove sensitive or irrelevant information
                
                Example form structure: {example}. Give the output as JSON and strictly give fields which is there in the form. All the extracted pdf details should be
                used to generate the form. I do not want partially created form. Generate it fully. Do not leave it{format_instructions}''',
                input_variables=['input_text'],
                partial_variables={'format_instructions': self.parser.get_format_instructions(),
                                   'example': self.example}    
        )
        
        self.chain = self.prompt | self.llm | self.parser
        
        # Creds for Google Cloud Document AI
        self.SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT')
        self.PROJECT_ID = os.getenv('PROJECT_ID')
        self.LOCATION = os.getenv('LOCATION')
        self.PROCESSOR_ID = os.getenv('PROCESSOR_ID')
        self.MIME_TYPE = "application/pdf"
        
    def doc2form(self, file_path):
        
        # shift_data = data_requester("http://192.168.173.223:3000/api/v1/shift")
        # if self.knowledge_base.vector_store is None:
        #     try:
        #         print("Loading vector store...")
        #         self.knowledge_base.load_vector_store("data/vector_db/faiss_index")
        #         print("Vector store loaded successfully.")
        #     except Exception as e:
        #         print(f"Error loading vector store: {e}")
        #         return None
        # try:
        #     knowledge_base_info = self.knowledge_base.query_vector_store()
        #     formatted_data = "\n".join([f"- {content}" for content, _ in knowledge_base_info])
        #     formatted_data = formatted_data + json.dumps(shift_data)
        #     print(formatted_data)
        # except ValueError as ve:
        #     print(f"ValueError: {ve}")
        #     return None
        # except Exception as e:
        #     print(f"Error querying knowledge base: {e}")
        #     return None
        
        client = authenticate_account(service_account_file=self.SERVICE_ACCOUNT_FILE)
        extracted_text = document_reader(client, self.PROJECT_ID, self.LOCATION, self.PROCESSOR_ID, file_path=file_path, mime_type=self.MIME_TYPE)
        
        try:
            res = self.chain.invoke({
                "input_text": extracted_text,
                # "knowledge_base_info": formatted_data
            })
            return res
        except Exception as e:
            raise ValueError(f"Error generating form {e}.")