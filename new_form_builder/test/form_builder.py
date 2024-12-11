import os
from dotenv import load_dotenv
from new_form_builder.core.form_builder import CoalMineFormGenerator

def main():
    # Load environment variables
    load_dotenv()

    # Retrieve Google API key from environment variables
    google_api_key = os.getenv('GOOGLE_API_KEY')
    print(google_api_key)
    if not google_api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    # Initialize the form generator
    form_generator = CoalMineFormGenerator(google_api_key)

    # Test cases for different operational descriptions
    test_queries = [
        # "Coal mine blasting operations, following Indian mining safety standards",
        # "Underground coal extraction process documentation",
        "Equipment maintenance and inspection for mining operations",
        # "Environmental safety and compliance form for coal mining site",
        # "Personnel safety and training documentation for mining workers"
    ]

    # Generate and save forms for each test query
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}: {query}")
        print(f"{'='*50}")

        # Generate the form
        generated_form = form_generator.generate_form(query, form_type="shift_handover_log")

        # Save the form to a JSON file if generation is successful
        if generated_form:
            output_filename = f"generated_form_{i}.json"
            form_generator.save_form_to_json(generated_form, output_filename)
            print(f"Form generated successfully. Details:")
            
            # Optionally, print some basic information about the generated form
            print("Generated Form", generated_form)
        else:
            print("Failed to generate form.")

if __name__ == "__main__":
    main()