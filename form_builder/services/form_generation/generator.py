import os
from pathlib import Path
import json
from typing import Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI

from form_builder.database.vector_store import FormVectorDB
from form_builder.services.form_generation.schemas import FormSchema
from form_builder.config import get_settings, FORM_GENERATION_PROMPT, TEMPLATE_DIR

class FormGenerationService:
    def __init__(
        self, 
        template_dir: str,
        model_name: str = "gemini-1.5-pro"
    ):
        """Initialize the form generation service.
        
        Args:
            template_dir (str): Directory to save generated templates
            model_name (str): Gemini model name to use
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Get API key and prompt from config
        settings = get_settings()
        self.form_generation_prompt = FORM_GENERATION_PROMPT
        
        # Initialize components
        self.vector_db = FormVectorDB()
        self.llm = GoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2
        )
        self.parser = JsonOutputParser(pydantic_type=FormSchema)
        
        # Create the ChatPromptTemplate
        self.prompt = PromptTemplate(
            template='''
            {form_generation_prompt}
            ''',
            input_variables=["query", "similar_templates"],
            partial_variables={"form_generation_prompt": self.form_generation_prompt,
                               "format_instruction": self.parser.get_format_instructions()}
        )

    def generate_form(self, query: str, similar_template: str = None) -> Dict:
        """Generate a form template based on the user query."""
        if similar_template is None:
            template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.json')]
            if template_files:
                with open(os.path.join(TEMPLATE_DIR, template_files[0]), 'r') as file:
                    similar_template = json.load(file)
            else:
                similar_template = {}
        
        form_data = (self.prompt | self.llm | self.parser).invoke({
            "query": query,
            "similar_templates": json.dumps(similar_template)
        })
        print("_"*50, query)
        return form_data

    def save_template(self, form_data: Dict) -> str:
        """Save the generated template and update vector database."""
        safe_name = form_data["form_name"].lower().replace(" ", "_")
        file_path = self.template_dir / f"{safe_name}.json"
        
        with open(file_path, 'w') as f:
            json.dump(form_data, f, indent=2)
            
        self.vector_db.load_templates(str(self.template_dir))
        self.vector_db.build_index()
        
        return str(file_path)