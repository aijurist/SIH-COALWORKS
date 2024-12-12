from new_form_builder.core.schema import FormField
from pydantic import ValidationError


try:
    form_field = FormField(
        label="Select Field",
        name="select_field",
        type="string",
        description="A field with options",
        placeholder="Choose an option",
        variant="Select",
        options=[],  # Empty options for a variant that requires options
    )
except ValidationError as e:
    print(e)