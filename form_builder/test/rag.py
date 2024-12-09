from form_builder.services.form_generation import FormGenerationService

# Initialize service
generator = FormGenerationService(template_dir="form_builder/template")

# Generate form
query = "I need a log form for a blasting operator to record all relevant operational details, such as explosives used, blast locations, timings, safety checks, and environmental precautions. This form should provide complete information that can be used by a supervisor to fill out their administrative form accurately"
form_data = generator.generate_form(query)

# Save template
template_path = generator.save_template(form_data)
print("form saved to ", template_path)