import os
from new_form_builder.core.knowledge import KnowledgeBase  # Replace with the actual file name if different

def test_knowledge_base():
    # Set up test parameters
    test_files = [
        "data/raw/smp.pdf", 
        "data/raw/yellowbook.pdf",
        "data/raw/cmr.pdf",     
        "data/raw/workers.pdf", 
        "data/raw/smp2.pdf", 
        "data/raw/safety.pdf",
        "data/raw/report.pdf",
        "data/raw/risk.pdf",
        "data/raw/risk2.pdf"
    ]
    vector_store_path = "data/vector_db/faiss_index"
    query_string = "create a form for blasting operations in coal mines"

    # Ensure test files exist
    for test_file in test_files:
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"{test_file} not found. Please provide valid files.")

    # Initialize the KnowledgeBase instance
    try:
        kb = KnowledgeBase()
    except ValueError as e:
        print(f"Initialization error: {e}")
        return

    # Test vector store creation or updating with multiple documents
    try:
        print("Creating or updating vector store with documents...")
        kb.add_documents(test_files, document_type="pdf", save_path=vector_store_path)
        print("Documents added successfully.")
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
