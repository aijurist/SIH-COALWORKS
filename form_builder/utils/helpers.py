# form_builder/utils/helpers.py

from typing import Dict, List
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain.pydantic_v1 import BaseModel, Field
class FormDescriptionModel(BaseModel):
    purpose: str = Field(description="The primary purpose of the form")
    description: str = Field(description="A comprehensive description of the form")
    target_audience: str = Field(description="The intended users or target audience for the form")
def generate_form_description(form_data: Dict) -> str:
    """Generate a searchable description from form data if none exists.
    
    Args:
        form_data (Dict): The form template data
        
    Returns:
        str: Generated description
    """
    llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    parser = JsonOutputParser(pydantic_object=FormDescriptionModel)
    
    prompt = PromptTemplate(
        template="""Based on the following form data, generate a comprehensive and searchable description:
        Form Data:
        {form_data}

        Please provide a JSON response with the following structure:
        {format_instructions}

        Generate a description that captures the key purpose, target audience, and main sections of the form.""",
                input_variables=["form_data"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )

    # Create the chain
    chain = prompt | llm | parser
    try:
        description_obj = chain.invoke({"form_data": str(form_data)})
        description = f"{description_obj.get('purpose', '')} {description_obj.get('description', '')}"
        return description.strip()
    
    except Exception as e:
        # Fallback description if generation fails
        return f"Form Description Generation Error: {str(e)}"
    

def validate_template(template_data: Dict) -> List[str]:
    """Validate a form template data structure.
    
    Args:
        template_data (Dict): The form template to validate
        
    Returns:
        List[str]: List of validation errors, empty if valid
    """
    errors = []
    
    # Required fields
    required_fields = ['form_name', 'fields']
    for field in required_fields:
        if field not in template_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate fields array
    fields = template_data.get('fields', [])
    if not isinstance(fields, list):
        errors.append("'fields' must be an array")
    else:
        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                errors.append(f"Field at index {i} must be an object")
            else:
                # Required field properties
                for prop in ['label', 'name', 'type']:
                    if prop not in field:
                        errors.append(f"Field at index {i} missing required property: {prop}")
    
    return errors