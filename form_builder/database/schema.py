# form_builder/database/schema.py

from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class FormField:
    label: str
    name: str
    type: str
    description: Optional[str] = None
    placeholder: Optional[str] = None
    required: bool = False
    disabled: bool = False
    variant: Optional[str] = None
    value: Optional[str] = None
    checked: Optional[bool] = None
    rowIndex: Optional[int] = None
    options: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        """Convert FormField instance to dictionary."""
        return {
            "label": self.label,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "placeholder": self.placeholder,
            "required": self.required,
            "disabled": self.disabled,
            "variant": self.variant,
            "value": self.value,
            "checked": self.checked,
            "rowIndex": self.rowIndex,
            "options": self.options
        }

@dataclass
class FormTemplate:
    form_name: str
    form_description: str
    fields: List[FormField] 
    template_path: str
    operation_type: str = ""
    type: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict, template_path: str) -> 'FormTemplate':
        """Create a FormTemplate instance from a dictionary."""
        fields_data = data.get('fields', [])
        fields = [FormField(**field) for field in fields_data]  # Convert each dict to FormField
        
        return cls(
            form_name=data.get('form_name', ''),
            form_description=data.get('form_description', data.get('form_name', '')),
            fields=fields,
            template_path=template_path,
            operation_type=data.get('operation_type', ''),
            type=data.get('type', '')
        )