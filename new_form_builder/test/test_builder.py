import os
from dotenv import load_dotenv
from new_form_builder.core.form_builder import CoalMineFormGenerator

def main():
    load_dotenv()
    google_api_key = os.getenv('GOOGLE_API_KEY')
    print(google_api_key)
    if not google_api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    form_generator = CoalMineFormGenerator(google_api_key)

    test_queries = [
        # "Coal mine blasting operations, following Indian mining safety standards",
        # "Underground coal extraction process documentation",
        "Equipment maintenance and inspection for mining operations",
        # "Environmental safety and compliance form for coal mining site",
        # "Personnel safety and training documentation for mining workers"
    ]
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}: {query}")
        print(f"{'='*50}")
        generated_form = form_generator.generate_form(user_description="Fly rock during Blasting Operation",form_type="control_plan",activity_info={})
        if generated_form:
            output_filename = f"generated_form_{i}.json"
            form_generator.save_form_to_json(generated_form, output_filename)
            print(f"Form generated successfully. Details:")
            
            print("Generated Form", generated_form)
        else:
            print("Failed to generate form.")

if __name__ == "__main__":
    main()