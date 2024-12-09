# form_builder/config.py

from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# Base directories
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "template"
DEPARTMENT_TEMPLATE_DIR = TEMPLATE_DIR / "department"
OUTSOURCED_TEMPLATE_DIR = TEMPLATE_DIR / "outsourced"


# Default system prompt for form generation
FORM_GENERATION_PROMPT = """You are a form generation expert specializing in coal mining operations in India. Your task is to create a comprehensive log form template based on the user's requirements.

The form should include fields relevant to the coal mines industry extracted from the user's query: '{query}'. Note that the user can ask for any type of form related to coal mine including log forms
(forms given to operators) as well as Administrative forms(forms given to supervisors to fill by using log forms). Make sure to be be as detailed as possible for the form fields

Similar templates for reference:
{similar_templates}

Return the output as a JSON object with the following structure:
- form_name: A clear and descriptive name for the form.
- form_description: A detailed purpose of the form.
- fields: An array of form fields with specifications:
  - checked: Always true.
  - label: User-friendly field name.
  - name: Variable name in snake_case.
  - type: Field type (e.g., Text, Select, Date).
  - description: A helpful description of what this field captures.
  - required: Boolean value indicating if this field is mandatory (true or false).
  - rowIndex: always 0.
  - value: Default value as an empty string.
  - disabled: Boolean indicating if the field is disabled (false).
  - placeholder: Optional help text for the field.
  - variant: Can be any of the following values: ["Checkbox", "File Input", "Textarea", "Switch", "Smart Datetime Input", "Slider", "Select", "Phone", "Multi Select", "Combobox", "Location Input", "Input", "Date Picker"].
  
Ensure that the generated form is detailed and relevant to coal mining practices in India. The output must be a well-structured JSON object without any markdown or example templates. Make sure to be detailed as possible and use 
the given template as the basic format. You must always return valid JSON fenced by a markdown code block. Do not return any additional text {format_instruction}"""
# Vector DB settings
VECTOR_DB_CONFIG = {
    "model_name": "all-MiniLM-L6-v2",
    "similarity_threshold": 0.9,
    "max_results": 3
}

# Index storage
INDEX_DIR = BASE_DIR / "database" / "indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Supported form field types
SUPPORTED_FIELD_TYPES = {
    "Text",
    "Number",
    "Date Picker",
    "Time Picker",
    "Select",
    "Combobox",
    "Input"
}

# Supported field variants
SUPPORTED_VARIANTS = {
    "Input",
    "Combobox",
    "Date Picker",
    "Time Picker"
}


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    TEMPLATE_DIR: str = "form_builder/template"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
    # print(f"GOOGLE_API_KEY: {settings.GOOGLE_API_KEY}")
    return settings