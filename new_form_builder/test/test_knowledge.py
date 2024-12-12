import os
from new_form_builder.core.knowledge import KnowledgeBase  # Replace with the actual file name if different

def test_knowledge_base():
    # Set up test parameters
    test_pdf = "data/raw/smp.pdf"  # Replace with the path to a valid test PDF
    test_txt = "data/raw/yellowbook.pdf"  # Replace with the path to a valid test text file
    vector_store_path = "new_form_builder/data/faiss_index"
    query_string = "create a form for blasting operations in coal mines"

    # Ensure test files exist
    if not os.path.exists(test_pdf):
        raise FileNotFoundError(f"{test_pdf} not found. Please provide a valid PDF file.")
    if not os.path.exists(test_txt):
        raise FileNotFoundError(f"{test_txt} not found. Please provide a valid PDF file.")

    # Initialize the KnowledgeBase instance
    try:
        kb = KnowledgeBase()
    except ValueError as e:
        print(f"Initialization error: {e}")
        return

    # Test vector store creation with PDF
    try:
        print("Creating vector store with PDF...")
        vector_store = kb.create_vector_store([test_pdf], document_type="pdf", save_path=vector_store_path)
        print("Vector store created successfully.")
    except Exception as e:
        print(f"Error while creating vector store: {e}")
        return

    # Test adding text documents
    try:
        print("Adding text document to vector store...")
        kb.add_documents([test_txt], document_type="pdf", save_path=vector_store_path)
        print("Text document added successfully.")
    except Exception as e:
        print(f"Error while adding documents: {e}")
        return

    # Test querying the vector store
    try:
        print(f"Querying the vector store with query: '{query_string}'...")
        results = kb.query_vector_store(query_string, top_k=3)
        print("Query results:")
        for i, (content, metadata) in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"  Content: {content}")
            print(f"  Metadata: {metadata}")
    except Exception as e:
        print(f"Error while querying vector store: {e}")
        return

    # Test loading the vector store
    try:
        print("Loading the vector store from disk...")
        kb.load_vector_store(vector_store_path)
        print("Vector store loaded successfully.")
    except Exception as e:
        print(f"Error while loading vector store: {e}")
        return

    print("All tests completed successfully.")

if __name__ == "__main__":
    test_knowledge_base()
