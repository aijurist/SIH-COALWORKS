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
    rowIndex: int = Field(description="Specifies the position of the field in the form layout.", default=1)
    options: Optional[List[Dict[str, str]]] = Field(description="List of dictionaries containing labels and values for option fields such as Checkbox, Select, Multi Select, Combobox.")

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

class FormSection(BaseModel):
    section_name: str = Field(description="The name or title of the form section.")
    section_description: Optional[str] = Field(description="A detailed explanation of the section's purpose.", default=None)
    fields: List[FormField] = Field(description="List of fields belonging to this section.", min_length=4)

class FormSchema(BaseModel):
    form_name: str = Field(description="The title or name of the form.")
    form_description: str = Field(description="A detailed description of the purpose and usage of the form.")
    sections: List[FormSection] = Field(description="Organized sections of the form, each containing related fields.", min_length=4)