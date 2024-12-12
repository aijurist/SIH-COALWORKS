import os
from dotenv import load_dotenv
from chatbot.agent.general_chatbot.chatbot import CoalMineChatbot  # Assuming the previous code is in a file named paste.py

def main():
    # Load environment variables (ensure you have a .env file with GOOGLE_API_KEY)
    load_dotenv()
    
    # Alternative 1: Using environment variable
    chatbot = CoalMineChatbot(api_key=os.getenv('GOOGLE_API_KEY'))
    
    # Alternative 2: Explicitly passing API key
    # chatbot = CoalMineChatbot(api_key='your_google_api_key_here')
    
    # Test queries
    test_questions = [
        "What is the significance of coal mining in India?",
        "How does the coal mining sector impact the environment?",
        "What are the main technological innovations in Indian coal mining?",
        "Explain the regulatory framework for coal mining in India",
        "What are the social impacts of coal mining in rural areas?"
    ]
    
    # Run test queries
    for question in test_questions:
        print(f"\nQuestion: {question}")
        print("-" * 50)
        try:
            response = chatbot.query(question)
            print(response)
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()
