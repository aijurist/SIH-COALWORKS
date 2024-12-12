from typing import List, Optional, Dict
from pydantic import BaseModel, Field, field_validator

class FormField(BaseModel):
    label: str = Field(description="The label displayed for the form field.")
    name: str = Field(description="The technical name or identifier for the form field.")
    type: str = Field(description="The data type of the form field (e.g., Text, Number, Date Picker).")
    description: str = Field(description="A detailed explanation of the field's purpose and what information it captures.")
    placeholder: str = Field(description="The placeholder text shown when the field is empty.")
    required: bool = Field(default=False, description="Indicates whether the field is mandatory.")
    disabled: bool = Field(default=False, description="Indicates whether the field is disabled and cannot be edited.")
    variant: str = Field(description='''The UI element type used for this field (allowed values are ["Checkbox", "Combobox", "Date Picker", "Datetime Picker", "File Input", "Input", "Multi Select", "Password", "Phone", "Select", "Signature Input", "Slider", "Switch", "Textarea"]).''')
    value: Optional[str] = Field(description="The default value pre-filled in the field, if any.")
    checked: bool = Field(description="Indicates the initial state for checkbox or radio fields.")
    rowIndex: int = Field(description="Specifies the position of the field in the form layout. Keep value at 0", )
    options: List[Dict[str, str]] = Field(description="List of dictionaries containing labels and values for fields which requires option such as Checkbox, Select, Multi Select, Combobox. If not an option field, then return none")

    @field_validator("variant")
    def validate_variant(cls, value):
        allowed_variants = [
            "Checkbox", "Combobox", "Date Picker", "Datetime Picker", "File Input",
            "Input", "Multi Select", "Password", "Phone", "Select", "Signature Input",
            "Slider", "Switch", "Textarea"
        ]
        if value not in allowed_variants:
            raise ValueError(f"Invalid variant: {value}. Allowed values are {allowed_variants}.")
        return value
    
    @field_validator('options')
    @classmethod
    def validate_options(cls, options, info):
        variant = info.data.get('variant')
        options_variants = ['Select', 'Combobox', 'Multi Select']
        
        if variant in options_variants and (options is None or len(options) == 0):
            raise ValueError(f"Options cannot be empty when variant is one of {options_variants}")
        
        return options

class FormSection(BaseModel):
    section_name: str = Field(description="The name or title of the form section.")
    section_description: Optional[str] = Field(description="A detailed explanation of the section's purpose.", default=None)
    fields: List[FormField] = Field(description="List of fields belonging to this section.", min_length=4)

class FormSchema(BaseModel):
    form_name: str = Field(description="The title or name of the form.")
    form_description: str = Field(description="A detailed description of the purpose and usage of the form.")
    sections: List[FormSection] = Field(description="Organized sections of the form, each containing related fields.", min_length=4)
    
class FormSectionFromDocument(BaseModel):
    section_name: str = Field(description="The name or title of the form section.")
    section_description: Optional[str] = Field(description="A detailed explanation of the section's purpose.", default=None)
    fields: List[FormField] = Field(description="List of fields belonging to this section.")
    
class FormSchemaFromDocument(BaseModel):
    form_name: str = Field(description="The title or name of the form.")
    form_description: str = Field(description="A detailed description of the purpose and usage of the form.")
    sections: List[FormSectionFromDocument] = Field(description="Organized sections of the form, each containing related fields.")