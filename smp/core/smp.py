import os
from dotenv import load_dotenv

# Langchain and AI imports
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Vector DB and SMP imports
from smp.core.schema import SMPModel
from smp.data.vector_store import KnowledgeBase
from smp.components.config import EXPOSURE_SCALE, CONSEQUENCE_SCALE, PROBABILITY_SCALE
from smp.utils.data_req import rtd_analyser
# Load environment variables
load_dotenv()

class HazardAnalysisChain:
    def __init__(self, google_api_key):
        
        self.parser = JsonOutputParser(pydantic_object=SMPModel)
        
        self.llm = GoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=google_api_key
        )
        
        self.knowledge_base = KnowledgeBase(api_key=google_api_key)
        self.prompt = PromptTemplate(
            template='''Context Information:

            Hazard Analysis Task:
            Given the activity "{activity_name}" related to coal mining, perform a detailed and comprehensive 
            hazard analysis. Utilize the provided context information and input, if available, to ensure accuracy.
            The user has given you additional information: {input_info}. Use this information if it is clear and relevant to the analysis. 
            
            Knowledge Base Information: {knowledge_base_info}. Use only relevant information from the knowledge base information given.
            Real time data information in concise version: {iot_data}, {shift_data}, {user_data}, {smp_data}
            Follow these instructions for the hazard analysis:
            
            1. Incorporate insights from the context information and input provided.
            2. Identify and list specific hazards or environmental aspects associated with the activity in coal mining.
            3. For each identified hazard:
            - Describe in detail the potential outcomes and consequences of the hazard.
            - Analyze existing control measures, their effectiveness, and any gaps.
            - Determine the potential risk factors, including likelihood, severity, and exposure.
            - Propose practical and actionable mitigation measures, including technological, procedural, or administrative controls.
            - Specify responsible parties for implementing each mitigation step.
            - Assess the potential residual impact and suggest monitoring or review mechanisms for ongoing safety.
            4. Tailor the analysis to the coal mining context, addressing specific challenges such as underground operations, equipment use, environmental risks, worker safety, and regulatory compliance.

            Return the output as JSON in the following format:
            {format_instruction}
            ''',
            input_variables=["activity_name", "knowledge_base_info", "input_info", "iot_data", "shift_data", "user_data", "smp_data"],
            partial_variables={"format_instruction": self.parser.get_format_instructions()},
        )

    
        self.chain = self.prompt | self.llm | self.parser
    
    def perform_hazard_analysis(self, activity_name, input_info=None, top_k=3):
        """
        Perform hazard analysis using activity name as context query
        
        :param activity_name: Name of the mining activity
        :param top_k: Number of top context results to retrieve
        :return: Hazard analysis results
        """
        if self.knowledge_base.vector_store is None:
            try:
                print("Loading vector store...")
                self.knowledge_base.load_vector_store("data/vector_db/faiss_index")
                print("Vector store loaded successfully.")
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return None
                                                      
        try:
            knowledge_base_info = self.knowledge_base.query_vector_store(activity_name)
            formatted_data = "\n".join([f"- {content}" for content, _ in knowledge_base_info])
            print(formatted_data)
        except ValueError as ve:
            print(f"ValueError: {ve}")
            return None
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return None

        rtd_data = rtd_analyser(activity_name)
        result = self.chain.invoke({
            "activity_name": activity_name,
            "knowledge_base_info": formatted_data,
            "input_info": input_info,
            "iot_data":{},
            "shift_data": rtd_data["shift"],
            "user_data":rtd_data["user"],
            "smp_data": rtd_data["smp"],
            
        })
        
        return result
            
            