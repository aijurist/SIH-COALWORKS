import os
from new_form_builder.core.knowledge import KnowledgeBase  # Replace with the actual file name if different

def test_knowledge_base():
    # Set up test parameters
    vector_store_path = "new_form_builder/data/faiss_index"
    query_string = "create a form for blasting operations in coal mines"

    # Initialize the KnowledgeBase instance
    try:
        kb = KnowledgeBase()
    except ValueError as e:
        print(f"Initialization error: {e}")
        return

    # Test loading the vector store
    try:
        print("Loading the vector store from disk...")
        kb.load_vector_store(vector_store_path)
        print("Vector store loaded successfully.")
    except Exception as e:
        print(f"Error while loading vector store: {e}")
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

    print("All tests completed successfully.")

if __name__ == "__main__":
    test_knowledge_base()