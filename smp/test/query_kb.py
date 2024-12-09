from smp.data.vector_store import KnowledgeBase
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

def main():
    # Initialize the KnowledgeBase instance
    kb = KnowledgeBase(api_key="GOOGLE_API_KEY")
    
    # Load the vector store
    vector_store_path = "smp/data/vector_db"
    kb.load_vector_store(load_path=vector_store_path)
    
    # Query the vector store
    query = "Principal Hazard Management Plans (PHMPs)"
    results = kb.query_vector_store(query, top_k=3)
    
    # Print the results
    print("Top search results:")
    for i, result in enumerate(results, 1):
        print(f"{i}: {result}")

# Run the example
if __name__ == "__main__":
    main()
