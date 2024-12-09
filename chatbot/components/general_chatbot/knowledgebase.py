import os
import json
from datetime import datetime
import asyncio
import websockets

# Langchain and Google imports
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class KnowledgeBase:
    """
    A comprehensive knowledge base management system that:
    - Supports multiple file formats (PDF, TXT, DOCX)
    - Uses Google's Generative AI Embeddings
    - Stores documents in FAISS vector database
    - Integrates with WebSocket for dynamic data ingestion
    """
    
    def __init__(self, 
                 google_api_key, 
                 embedding_model='models/embedding-001', 
                 vector_db_path='chatbot/database/faiss_index'):
        """
        Initialize the Knowledge Base

        Args:
            google_api_key (str): Google API key for embeddings
            embedding_model (str, optional): Google embedding model. Defaults to 'models/embedding-001'
            vector_db_path (str, optional): Path to store FAISS vector database
        """
        # Set API key
        os.environ['GOOGLE_API_KEY'] = google_api_key
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            task_type="retrieval_document"
        )
        
        # Vector DB path
        self.vector_db_path = vector_db_path
        
        # Initialize vector store
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """
        Load existing FAISS index or create a new one
        """
        try:
            # Try to load existing vector store
            self.vectorstore = FAISS.load_local(
                self.vector_db_path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception:
            # Create a new vector store if no existing index
            self.vectorstore = FAISS.from_texts(
                texts=["Initial placeholder text"], 
                embedding=self.embeddings
            )
            self._save_vectorstore()
    
    def _save_vectorstore(self):
        """
        Save the current state of the vector store
        """
        if self.vectorstore:
            self.vectorstore.save_local(self.vector_db_path)
    
    def add_document(self, file_path, metadata=None):
        """
        Add a document to the knowledge base

        Args:
            file_path (str): Path to the document
            metadata (dict, optional): Additional metadata for the document
        """
        # Determine loader based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.docx': Docx2txtLoader
        }
        
        loader = loaders.get(file_ext)
        if not loader:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Load document
        documents = loader(file_path).load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Add metadata if provided
        if metadata:
            for split in splits:
                split.metadata.update(metadata)
        
        # Add to vector store
        self.vectorstore.add_documents(splits)
        self._save_vectorstore()
    
    def add_websocket_data(self, page_data):
        """
        Add data received from WebSocket to knowledge base

        Args:
            page_data (dict): Data received from WebSocket
        """
        page_number = page_data.get('page', 'unknown')
        data_content = page_data.get('data', {}).get('data', {})
        timestamp = page_data.get('timestamp', datetime.now().isoformat())
        
        text_content = json.dumps({
            'page': page_number,
            'data': data_content,
            'timestamp': timestamp
        })
        
        # langchain document for easier storage
        document = Document(
            page_content=text_content,
            metadata={
                'source': 'websocket',
                'page_number': page_number,
                'timestamp': timestamp
            }
        )
        
        # adding to vectordb - needs check since it sometimes doesnt get added
        self.vectorstore.add_documents([document])
        self._save_vectorstore()
    
    def search(self, query, k=4):
        """
        Search the knowledge base

        Args:
            query (str): Search query
            k (int, optional): Number of results to return. Defaults to 4.
        """
        return self.vectorstore.similarity_search(query, k=k)