import os
from chatbot.db.knowledge_base import KnowledgeBase
from chatbot.core.chatbot import KnowledgeBaseChatbot
import os
from dotenv import load_dotenv

load_dotenv# Assuming the previous code is in a module named 'paste'

def main():
    # Set up Google API key 
    # IMPORTANT: Replace with your actual Google API key or set as environment variabl
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    # Initialize the knowledge base (if not already created)
    def prepare_knowledge_base():
        """
        Example method to prepare knowledge base with some initial documents.
        Modify this based on your actual KnowledgeBase implementation.
        """
        kb = KnowledgeBase(api_key=GOOGLE_API_KEY)
        

    # Prepare the knowledge base
    prepare_knowledge_base()

    # Create chatbot instance
    chatbot = KnowledgeBaseChatbot(
        api_key=os.getenv("GOOGLE_API_KEY"),
        knowledge_base_path="data/vector_db/faiss_index"
    )

    # Test conversation loop
    def test_conversation():
        print("Knowledge Base Chatbot Test")
        print("Type 'quit' to exit")

        while True:
            try:
                # Get user input
                user_input = input("You: ")

                # Check for exit condition
                if user_input.lower() == 'quit':
                    print("Exiting chatbot...")
                    break

                # Generate and print response
                response = chatbot.generate_response(user_input)
                print("Chatbot:", response)

                # Optional: Print retrieved knowledge base context
                context = chatbot._retrieve_knowledge_base_context(user_input)
                # print("\nRetrieved Knowledge Base Context:")
                # print(context)
                # print("-" * 50)

            except KeyboardInterrupt:
                print("\nExiting chatbot...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    # Run the conversation test
    test_conversation()

    # Print out chat history for review
    print("\nChat History:")
    for msg in chatbot.chat_history:
        print(f"{msg.role.capitalize()} [{msg.timestamp}]: {msg.content}")

if __name__ == "__main__":
    main()