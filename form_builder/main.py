import sys
import os
import json
from typing import Tuple

# Append the parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from form_builder.database.vector_store import FormVectorDB
from form_builder.services.form_generation import FormGenerationService
from form_builder.config import get_settings, VECTOR_DB_CONFIG, TEMPLATE_DIR

def template_to_json(template):
    """Convert FormTemplate instance to a JSON-compatible dictionary."""
    return {
        "form_name": template.form_name,
        "form_description": template.form_description,
        "template_path": template.template_path,
        "operation_type": template.operation_type,
        "type": template.type,
        "fields": [field.to_dict() for field in template.fields]  # Convert each FormField to dict
    }

def main():
    # Load settings from config.py
    settings = get_settings()

    vector_db = FormVectorDB(model_name=VECTOR_DB_CONFIG["model_name"])
    template_dir = TEMPLATE_DIR

    try:
        vector_db.load_templates(template_dir)
    except FileNotFoundError as e:
        print(f"Error loading templates: {e}")
        return

    try:
        vector_db.build_index()
    except ValueError as e:
        print(f"Error building index: {e}")
        return

    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'saved_index')
    vector_db.save_index(save_dir)
    print(f"Index and templates saved to {save_dir}")

    user_query = input("Enter your query for a new form: ")

    try:
        results = vector_db.search_similar_forms(
            user_query,
            k=VECTOR_DB_CONFIG.get("max_results", 1),
            threshold=VECTOR_DB_CONFIG.get("similarity_threshold", 0.9)
        )

        if results:
            top_result = results[0]
            template, similarity_score = top_result
            print("Similar form found:")
            print(json.dumps(template_to_json(template), indent=2))
            print("Similarity score:", similarity_score)
        else:
            generator = FormGenerationService(template_dir=template_dir)
            form_data = generator.generate_form(user_query)
            template_path = generator.save_template(form_data)
            print("New form generated:")
            print(json.dumps(form_data, indent=2))
            print(f"Template saved to: {template_path}")
    except ValueError as e:
        print(f"Error in form generation or search: {e}")

if __name__ == "__main__":
    main()
