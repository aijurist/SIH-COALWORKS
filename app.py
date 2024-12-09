import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from new_form_builder.core.form_builder import CoalMineFormGenerator

# Load environment variables
load_dotenv()

# Retrieve Google API key from environment variables
google_api_key = os.getenv('GOOGLE_API_KEY')

# Initialize the form generator
if not google_api_key:
    raise ValueError("Error: GOOGLE_API_KEY not found in environment variables.")

form_generator = CoalMineFormGenerator(google_api_key)

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

@app.route("/generate_form", methods=["POST"])
def generate_form():
    """
    Generate a comprehensive form for the given industrial operation description.

    :return: JSON representation of the generated form.
    """
    try:
        # Parse JSON input
        data = request.get_json()

        if not data or "description" not in data:
            return jsonify({"error": "Missing 'description' field in the request body"}), 400

        # Generate the form
        description = data["description"]
        generated_form = form_generator.generate_form(description)

        if not generated_form:
            return jsonify({"error": "Form generation failed"}), 500

        return jsonify({"query": description, "form": generated_form})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    # Run on all network interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
