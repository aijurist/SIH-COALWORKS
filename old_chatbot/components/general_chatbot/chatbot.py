import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Langchain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.vectorstores import VectorStore

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoalMineChatbot:
    """
    A specialized chatbot for answering questions about coal mines in India
    using Google's Generative AI with knowledge base similarity search.
    """
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-pro"):
        """
        Initialize the chatbot with Google API key, model, and knowledge base.
        
        Args:
            api_key (str, optional): Google API key. Defaults to None (will load from environment).
            model_name (str, optional): Name of the Google AI model to use.
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Use provided API key or try to get from environment
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Initialize the Google AI model and embeddings
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.api_key, 
            model=model_name,
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=self.api_key,
            model="models/embedding-001"
        )
        
        # Predefined knowledge base about coal mining in India
        self.coal_mine_knowledge = [
            {
                "text": "Coal is a critical energy resource in India, with Coal India Limited (CIL) being the largest coal-producing company in the world. India is the second-largest coal producer globally, with most coal mines located in states like Jharkhand, Odisha, Chhattisgarh, and West Bengal."
            },
            {
                "text": "The coal mining sector in India is primarily regulated by the Ministry of Coal. The Coal Mines (Special Provisions) Act, 2015 and subsequent amendments have transformed the coal mining landscape, allowing commercial mining and breaking the monopoly of Coal India Limited."
            },
            {
                "text": "Environmental considerations are crucial in Indian coal mining. The Ministry of Environment, Forest and Climate Change (MoEFCC) mandates Environmental Impact Assessments (EIA) for new mining projects. Rehabilitation and reforestation are key components of modern coal mining practices in India."
            },
            {
                "text": "Technological innovations in Indian coal mining include longwall mining, opencast mining, and underground mining techniques. Efforts are being made to improve mining efficiency, reduce environmental impact, and implement advanced extraction methods."
            },
            {
                "text": "The social impact of coal mining in India is significant. Many mining areas are in tribal and rural regions, requiring careful management of community displacement, employment, and local economic development. Sustainable mining practices aim to balance economic needs with social welfare."
            },
            {
                "text": "Coal continues to be a primary energy source in India, accounting for approximately 70% of electricity generation. Despite growing renewable energy investments, coal remains crucial for India's energy security and industrial development."
            }
        ]
        
        self.vectorstore = self._load_knowledge_base()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert assistant specializing in coal mines and operations in India. 
            Provide detailed, accurate, and context-aware responses about:
            - Coal mining operations in India
            - Geological aspects of coal deposits
            - Environmental and regulatory considerations
            - Economic significance of coal mining
            - Technological innovations in coal mining
            - Social and community impacts
            - Operational aspects in coal mines
            - and data given to you(Iot Data, machinery data and many more)
            
            If the information is not in your knowledge base, provide the most relevant 
            and helpful information possible based on your training."""),
            ("human", "{context}\n\nQuestion: {question}")
        ])
        
        self._create_retrieval_chain()
    
    def _load_knowledge_base(self) -> VectorStore:
        """
        Load the knowledge base with multiple fallback mechanisms.
        
        Returns:
            VectorStore: A FAISS vector store with embeddings
        """
        # Paths for FAISS index
        index_path = os.path.join('chatbot', 'database', 'faiss_index', 'index.faiss')
        store_path = os.path.join('chatbot', 'database', 'faiss_index')

        try:
            if os.path.exists(index_path):
                logger.info("Attempting to load existing FAISS index...")
                vectorstore = FAISS.load_local(
                    folder_path=store_path, 
                    embeddings=self.embeddings,
                    index_name='index'
                )
                logger.info("Existing FAISS index loaded successfully.")
                return vectorstore
        except Exception as e:
            logger.warning(f"Error loading FAISS index: {e}")
        
        # Fallback: Create new vector store from predefined knowledge
        try:
            logger.info("Creating fallback vector store from predefined knowledge...")
            vectorstore = FAISS.from_texts(
                [item['text'] for item in self.coal_mine_knowledge], 
                embedding=self.embeddings
            )
            logger.info("Fallback vector store created successfully.")
            return vectorstore
        except Exception as e:
            logger.error(f"Critical error creating fallback vector store: {e}")
            return None
            
    def _create_retrieval_chain(self):
        """
        Create the retrieval-augmented generation chain.
        """
        # Check if vectorstore exists
        if self.vectorstore is None:
            logger.warning("No vector store available. Falling back to base model without retrieval.")
            # Create a simple chain without retrieval
            self.rag_chain = (
                {"question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        else:
            # Retriever
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
            
            # Retrieval chain
            self.rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
    
    def query(self, question: str) -> str:
        """
        Query the chatbot with a specific question about coal mines in India.
        
        Args:
            question (str): User's question about coal mining
        
        Returns:
            str: Detailed response from the chatbot
        """
        try:
            # Invoke the retrieval-augmented generation chain
            logger.info(f"Processing query: {question}")
            response = self.rag_chain.invoke(question)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"An error occurred while processing your query: {str(e)}"