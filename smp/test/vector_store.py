from smp.data.vector_store import KnowledgeBase
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

def main():
    # Initialize the KnowledgeBase instance
    kb = KnowledgeBase(api_key=GOOGLE_API_KEY)  # Replace with your actual API key
    
    # Step 1: Create a vector store with the first PDF
    first_pdf_path = "smp/example/smp.pdf"  # Replace with the path to your first PDF
    vector_store_path = "smp/data/vector_db"  # Path to save the vector store

    # Create a vector store with the first PDF
    print("Creating vector store with the first PDF...")
    vector_store = kb.create_vector_store(documents=[first_pdf_path], document_type="pdf", save_path=vector_store_path)
    print("Vector store created and saved locally.")

    # Step 2: Load the previously saved vector store
    print("\nLoading the existing vector store...")
    loaded_vector_store = kb.load_vector_store(load_path=vector_store_path)
    print("Vector store loaded successfully.")

    # Step 3: Add a new PDF to the existing vector store
    second_pdf_path = "smp/example/regulation.pdf"  # Replace with the path to your second PDF

    print("\nAdding a new PDF to the existing vector store...")
    kb.add_documents(documents=[second_pdf_path], document_type="pdf", save_path=vector_store_path)
    print("New PDF added to the vector store and saved locally.")

# Run the example
if __name__ == "__main__":
    main()
