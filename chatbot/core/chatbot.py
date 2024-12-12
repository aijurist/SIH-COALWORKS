import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Knowledge Base and LLM imports
from chatbot.db.knowledge_base import KnowledgeBase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMemory

@dataclass
class ChatMessage:
    """Represents a single chat message with metadata."""
    role: str  # 'human' or 'ai'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class KnowledgeBaseChatbot:
    """
    A chatbot that integrates a knowledge base and maintains chat history.
    
    Attributes:
        knowledge_base (KnowledgeBase): Vector store for semantic search
        llm (ChatGoogleGenerativeAI): Language model for generating responses
        chat_history (List[ChatMessage]): Conversation history
        memory (ConversationBufferMemory): LangChain memory for tracking conversation context
    """
    
    def __init__(self, 
                 api_key: str = None, 
                 knowledge_base_path: str = "data/vector_db/faiss_index",
                 model: str = "gemini-1.5-pro"):
        """
        Initialize the chatbot with knowledge base and language model.
        
        :param api_key: Google API key (optional, can be loaded from environment)
        :param knowledge_base_path: Path to the FAISS vector store
        :param model: Gemini model to use for chat
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key must be provided")
        self.knowledge_base = KnowledgeBase(api_key=self.api_key)

        try:
            self.knowledge_base.load_vector_store(knowledge_base_path)
        except Exception:
            print(f"No existing vector store found at {knowledge_base_path}. You may need to create one.")
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=self.api_key,
            temperature=0.7,
        )

        self.chat_history: List[ChatMessage] = []
        self.memory = ConversationBufferMemory(return_messages=True)
        self.prompt_template = PromptTemplate(
            input_variables=["chat_history", "knowledge_base_context", "human_input"],
            template="""
            Based on the conversation history and the most relevant context from the knowledge base, 
            provide a helpful and accurate response. You are Anthra, a coal mine chatbot who will help the supervisor and others 
            in the coal mine. You need to give concrete answers to the questions posed by the user. 

            Knowledge Base Context:
            {knowledge_base_context}

            Conversation History:
            {chat_history}

            Human Input: {human_input}
            AI Response:"""
        )
    
    def _retrieve_knowledge_base_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve most relevant context from the knowledge base.
        
        :param query: User's input query
        :param top_k: Number of top similar chunks to retrieve
        :return: Formatted context string
        """
        try:
            similar_chunks = self.knowledge_base.query_vector_store(query, top_k=top_k)
            context_str = "\n\n".join([
                f"Source: {metadata['source']}\nContent: {chunk}"
                for chunk, metadata in similar_chunks
            ])
            
            return context_str
        except Exception as e:
            print(f"Error retrieving knowledge base context: {e}")
            return ""
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response using the knowledge base and language model.
        
        :param user_input: User's input message
        :return: AI-generated response
        """
        knowledge_base_context = self._retrieve_knowledge_base_context(user_input)
        chat_history_str = "\n".join([
            f"{msg.role.capitalize()}: {msg.content}" 
            for msg in self.chat_history[-5:] 
        ])

        prompt = self.prompt_template.format(
            chat_history=chat_history_str,
            knowledge_base_context=knowledge_base_context,
            human_input=user_input
        )
        
        # Generate response
        try:
            response = self.llm.invoke(prompt).content
        except Exception as e:
            print(f"Error generating response: {e}")
            response = "I'm sorry, I couldn't generate a response at the moment."
        
        # Update chat history
        self.chat_history.extend([
            ChatMessage(role='human', content=user_input),
            ChatMessage(role='ai', content=response)
        ])
        
        # Update memory
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(response)
        
        return response