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
from new_form_builder.utils.helper import data_requester, query_json

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
        self.parser = JsonOutputParser(pydantic_object=FormSchema)
        
        with open('new_form_builder/template/outsourced/explosive.json', 'r') as file:
            self.example = json.load(file)
        self.prompt_log = PromptTemplate(
            template='''You are an expert form designer specializing in creating comprehensive safety and operational control plan forms for coal mining operations. 

                Objective: Design an intricate, multi-section digital form that provides a thorough assessment of safety, operational readiness, environmental considerations, and risk management for coal mining activities.

                Context Details:
                - User Operational Description: {user_description}
                - Existing Safety Management Information: {knowledge_base_info}
                - Specific Activity/Hazard Information: {activity_info}

                Form Design Requirements:
                Comprehensive Safety Assessment Sections:
                - Pre-Shift Safety Inspection Checklist
                - Personal Protective Equipment (PPE) Verification
                - Equipment Operational Readiness
                - Emergency Response Preparedness
                - Environmental Monitoring
                - Specific Hazard Mitigation Protocols


                3. Key Assessment Areas:
                a) Geological Stability Assessment
                    - Ground support status
                    - Roof and wall integrity
                    - Potential rock burst risks
                    - Ventilation shaft stability

                b) Equipment and Machinery Inspection
                    - Mechanical condition checks
                    - Electrical system integrity
                    - Hydraulic and pneumatic system assessment
                    - Wear and tear evaluation
                    - Calibration and maintenance records

                c) Safety Systems Verification
                    - Gas detection system functionality
                    - Fire suppression system readiness
                    - Communication equipment status
                    - Emergency escape route assessment


                d) Risk Management
                    - Identified potential hazards
                    - Mitigation strategy effectiveness
                    - Incident prevention measures
                    - Real-time risk scoring mechanism

                5. Submission Requirements:
                - Mandatory field completion
                - Timestamps for each section
                - Automatic data validation
                - Cross-referencing with historical safety data

                Generate a highly structured, comprehensive digital form that transforms safety management from a checklist to a sophisticated risk assessment and prevention tool.

            Return the output strictly following this JSON schema:
            {format_instruction}
            ''',
            input_variables=["user_description", "knowledge_base_info"],
            partial_variables={"format_instruction": self.parser.get_format_instructions(),
                               "example": self.example}
        )
        
        self.prompt_controlPlan = PromptTemplate(
            template='''You are a form design expert specializing in creating detailed safety and operational assessment forms for coal mining operations.

                Objective:
                Create a multi-section digital form to evaluate safety, operational readiness, environmental impact, and risk management in coal mining activities.

                Context:
                - User Description: {user_description}
                - Existing Safety Information: {knowledge_base_info}
                - Activity or Hazard Details: {activity_info}

                Sample example form: {example}
                Form Design Requirements:
                Include sections for:
                1. Pre-Shift Safety Inspection
                2. PPE (Personal Protective Equipment) Verification
                3. Equipment Readiness
                4. Emergency Response Preparedness
                5. Environmental Monitoring
                6. Specific Hazard Mitigation Protocols. {format_instructions}'''
        ,
        input_variables=["user_description", "knowledge_base_info", "activity_info"],
        partial_variables={"format_instructions": self.parser.get_format_instructions(),
                           "example": self.example}
        )

    def generate_form(self, user_description: str, form_type: str, activity_info: str = None):
        """
        Generate a specialized form based on user's operational description
        
        Parameters:
        user_description: Detailed description of the industrial operation
        form_type: type of form. Values can either be 'shift_handover_log' or 'control_plan'
        
        Returns a form generated for ShadCN using the Formschema class
        """

        validity_result = user_query_validator(user_description)
        if validity_result and not validity_result.get('query_validity', False):
            return validity_result
        
        shift_data = data_requester("http://192.168.173.223:3000/api/v1/shift")
        if self.knowledge_base.vector_store is None:
            try:
                print("Loading vector store...")
                self.knowledge_base.load_vector_store("data/vector_db/faiss_index")
                print("Vector store loaded successfully.")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None
        try:
            knowledge_base_info = self.knowledge_base.query_vector_store(user_description)
            formatted_data = "\n".join([f"- {content}" for content, _ in knowledge_base_info])
            formatted_data = formatted_data + json.dumps(shift_data)
            print(formatted_data)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return None


        if form_type not in ['shift_handover_log', 'control_plan']:
            raise ValueError("Not a valid form type. Options are 'control_plan', 'shift_handover_log'")
        if form_type == 'shift_handover_log':
            chain = self.prompt_log | self.llm | self.parser
        elif form_type == 'control_plan':
            chain = self.prompt_controlPlan | self.llm | self.parser
        

        try:
            if form_type == 'shift_handover_log':
                result = chain.invoke({
                    "user_description": user_description,
                    "knowledge_base_info": formatted_data
                })
                return result
            else:
                result = chain.invoke({
                    "user_description": user_description,
                    "knowledge_base_info": formatted_data,
                    "activity_info": activity_info
                })
                return result
        except Exception as e:
            raise ValueError(f"Error generating form for operation: {e}")
            return None
    def save_form_to_json(self, form: Union[Dict, FormSchema], filename: str):
        """
        Save the generated form to a JSON file
        
        Parameters:
        form: FormSchema instance or dictionary
        filename: Output filename
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