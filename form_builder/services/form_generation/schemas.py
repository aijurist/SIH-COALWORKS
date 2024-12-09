from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class FormFieldSchema(BaseModel):
    label: str = Field(description="The label displayed for the form field.")
    name: str = Field(description="The technical name or identifier for the form field.")
    type: str = Field(description="The data type of the form field (e.g., Text, Number, Date Picker).")
    description: Optional[str] = Field(description="A detailed explanation of the field's purpose and what information it captures.")
    placeholder: Optional[str] = Field(description="The placeholder text shown when the field is empty.")
    required: bool = Field(default=False, description="Indicates whether the field is mandatory.")
    disabled: bool = Field(default=False, description="Indicates whether the field is disabled and cannot be edited.")
    variant: Optional[str] = Field(description='''The UI element type used for this field (allowed values are ["Checkbox", "Combobox", "Date Picker", "Datetime Picker", "File Input", 
            "Input", "Multi Select", "Password", "Phone", "Select", "Signature Input", "Slider", "Switch", "Textarea"]).''')
    value: Optional[str] = Field(description="The default value pre-filled in the field, if any.")
    checked: Optional[bool] = Field(description="Indicates the initial state for checkbox or radio fields.")
    rowIndex: Optional[int] = Field(description="Specifies the position of the field in the form layout.")

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

class FormSchema(BaseModel):
    form_name: str = Field(description="The title or name of the form.")
    form_description: str = Field(description="A detailed description of the purpose and usage of the form.")
    fields: List[FormFieldSchema] = Field(description="A list of fields that make up the form.")