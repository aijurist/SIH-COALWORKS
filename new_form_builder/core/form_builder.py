import json
import os
from typing import Dict, Union
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
from new_form_builder.core.query_validator import user_query_validator
from new_form_builder.core.schema import FormSchema
from new_form_builder.core.knowledge import KnowledgeBase

load_dotenv()

class CoalMineFormGenerator:
    def __init__(self, google_api_key):
        """
        Initialize the Dynamic Coal Mine Form Generator
        
        :param google_api_key: Google API key for Gemini model
        """
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=google_api_key
        )
        
        self.knowledge_base = KnowledgeBase(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # JSON Output Parser
        self.parser = JsonOutputParser(pydantic_object=FormSchema)
        
        with open('new_form_builder/template/outsourced/explosive.json', 'r') as file:
            self.example = json.load(file)
            
        # Generic Prompt Template
        self.prompt = PromptTemplate(
            template='''You are an expert form designer specializing in creating comprehensive documentation forms for industrial operations.

            Context:
            - You will design a specialized form for a specific industrial operation
            - The form must be tailored to capture all critical aspects of the operation

            User Query: {user_description}
            
            Knowledge Base Information: {knowledge_base_info}. Use only relevant information from the knowledge base information given.

            Task:
            Design a comprehensive, detailed form that thoroughly documents the specific industrial operation. The form should:
            1. Capture all critical technical, safety, and operational details
            2. Ensure compliance with relevant industry and regulatory standards
            3. Include fields that provide exhaustive documentation of the operation
            4. Consider operational requirements, safety protocols, and detailed process tracking

            Design Guidance:
            - Carefully analyze the operation described in the user query
            - Identify and create fields that comprehensively cover:
            * Technical specifications
            * Safety protocols
            * Personnel involvement
            * Equipment details
            * Regulatory compliance requirements
            * Risk assessment and mitigation
            - Ensure the form provides a complete, multi-dimensional view of the operation
            - Create fields that capture both quantitative and qualitative information
            - Make the form adaptable and thorough
            - Make the form user friendly and try to use variants such as Checkbox, Select, Multi Select, etc

            Your goal is to generate a form that allows for precise, comprehensive documentation of the industrial operation, addressing all critical aspects of the process.
            Here is an example form which you can use to create your forms {example}

            Return the output strictly following this JSON schema:
            {format_instruction}
            ''',
            input_variables=["user_description", "knowledge_base_info"],
            partial_variables={"format_instruction": JsonOutputParser(pydantic_object=FormSchema).get_format_instructions(),
                               "example": self.example}
        )

    # Modify the generate_form method to accept a user description
    def generate_form(self, user_description: str):
        """
        Generate a specialized form based on user's operational description
        
        :param user_description: Detailed description of the industrial operation
        :return: Generated form schema
        """

        validity_result = user_query_validator(user_description)

        # If the query is invalid, return the validity result immediately
        if validity_result and not validity_result.get('query_validity', False):
            return validity_result

        # Load the vector store if it hasn't been loaded yet
        if self.knowledge_base.vector_store is None:
            try:
                print("Loading vector store...")
                self.knowledge_base.load_vector_store("data/vector_db/faiss_index")
                print("Vector store loaded successfully.")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None

        # Query the knowledge base for relevant information
        try:
            knowledge_base_info = self.knowledge_base.query_vector_store(user_description)
            formatted_data = "\n".join([f"- {content}" for content, _ in knowledge_base_info])
            print(formatted_data)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return None

        # Create the chain
        chain = self.prompt | self.llm | self.parser

        try:
            # Invoke the chain with the user's description and knowledge base information
            result = chain.invoke({
                "user_description": user_description,
                "knowledge_base_info": formatted_data
            })
            return result
        except Exception as e:
            print(f"Error generating form for operation: {e}")
            return None
    def save_form_to_json(self, form: Union[Dict, FormSchema], filename: str):
        """
        Save the generated form to a JSON file
        
        :param form: FormSchema instance or dictionary
        :param filename: Output filename
        """
        if form:
            if isinstance(form, dict):
                form_dict = form
            elif hasattr(form, 'dict'):
                form_dict = form.dict()
            else:
                form_dict = dict(form)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(form_dict, f, indent=2)
            print(f"Form saved to {filename}")
        else:
            print("No form to save")