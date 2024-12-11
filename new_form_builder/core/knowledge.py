import os
from typing import List, Union, Optional, Tuple
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
from dotenv import load_dotenv
from dataclasses import dataclass
import pandas as pd
import tabula

@dataclass
class DocumentMetadata:
    """ Metadata associated with a document. """
    source: str
    document_type: str
    section_title: Optional[str] = None

class KnowledgeBase:
    """ A class to manage knowledge base creation and storage using vector embeddings.
        Supports PDF, text files, and tabular data, and uses Faiss as the vector store.
    """
    
    def __init__(self, api_key: Optional[str] = None, embedding_model: str = "models/embedding-001",
                 chunk_size: int = 1000, chunk_overlap: int = 200):
        """ Initialize the KnowledgeBase with configuration parameters.
            :param api_key: Google API key (optional, can be loaded from .env)
            :param embedding_model: Embedding model to use
            :param chunk_size: Size of text chunks for embedding
            :param chunk_overlap: Overlap between text chunks
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key must be provided either as argument or in .env file")
        
        genai.configure(api_key=self.api_key)
        self.embedding_model = embedding_model
        self.embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store = None

    def _extract_text_from_pdf(self, pdf_path: Union[str, object]) -> Tuple[str, DocumentMetadata]:
        """ Extract text and metadata from a PDF file.
            :param pdf_path: Path to PDF file or file-like object
            :return: Extracted text and document metadata 
        """
        if isinstance(pdf_path, str):
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
        else:
            raise ValueError("Expected a string path for the PDF file.")

        return text, DocumentMetadata(source=pdf_path, document_type='pdf')

    def _extract_text_from_txt(self, txt_path: Union[str, object]) -> Tuple[str, DocumentMetadata]:
        """ Extract text and metadata from a text file.
            :param txt_path: Path to text file or file-like object
            :return: Extracted text and document metadata 
        """
        if isinstance(txt_path, str):
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read(), DocumentMetadata(source=txt_path, document_type='txt')
        
        else:
            return txt_path.read().decode('utf-8'), DocumentMetadata(source=txt_path, document_type='txt')

    def _extract_table_from_pdf(self, pdf_path: str) -> Tuple[pd.DataFrame, DocumentMetadata]:
        """ Extract tabular data from a PDF file.
            :param pdf_path: Path to PDF file 
            :return: Extracted tabular data and document metadata 
        """
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        if tables:
            return tables[0], DocumentMetadata(source=pdf_path, document_type='pdf')
        
        else:
            return pd.DataFrame(), DocumentMetadata(source=pdf_path, document_type='pdf')

    def _split_text(self, text: str) -> List[Tuple[str, DocumentMetadata]]:
        """ Split text into chunks and associate metadata with each chunk.
            :param text: Input text to be split 
            :return: List of text chunks and their associated metadata 
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        chunks = text_splitter.split_text(text)
        
        return [(chunk, vars(DocumentMetadata(source=self.current_doc_source,
                                               document_type=self.current_doc_type))) for chunk in chunks]

    def create_vector_store(self, documents: Union[List[str], List[object]], 
                             document_type: str = 'pdf', save_path: str = "faiss_index") -> FAISS:
        """ Create a vector store from documents.
            :param documents: List of document paths or file-like objects 
            :param document_type: Type of documents ('pdf', 'txt', or 'table') 
            :param save_path: Path to save the vector store 
            :return: FAISS vector store 
        """
        all_text_chunks = []
        all_tables = []
        
        for doc in documents:
            if document_type.lower() == 'pdf':
                text, metadata = self._extract_text_from_pdf(doc)
                table, table_metadata = self._extract_table_from_pdf(doc)
                
                if table.shape[0] > 0:
                    all_tables.append((table, table_metadata))
            
            elif document_type.lower() == 'txt':
                text, metadata = self._extract_text_from_txt(doc)
            
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            self.current_doc_source = metadata.source
            self.current_doc_type = metadata.document_type
            
            text_chunks = self._split_text(text)
            all_text_chunks.extend(text_chunks)

        self.vector_store = FAISS.from_texts(
            [chunk[0] for chunk in all_text_chunks],
            embedding=self.embeddings,
            metadatas=[chunk[1] for chunk in all_text_chunks]
        )
        
        return self.vector_store

    def load_vector_store(self, load_path: str = "faiss_index") -> FAISS:
        """ Load an existing vector store.
            :param load_path: Path to the saved vector store 
            :return: Loaded FAISS vector store 
        """
        self.vector_store = FAISS.load_local(load_path,
                                              self.embeddings,
                                              allow_dangerous_deserialization=True)
        
        return self.vector_store

    def add_documents(self, documents: List[str], document_type: str = 'pdf',
                      save_path: str = "faiss_index") -> None:
        """ Add new documents to an existing vector store or create a new one.
            :param documents: List of document paths 
            :param document_type: Type of documents ('pdf', 'txt', or 'table') 
            :param save_path: Path to save/update the vector store 
        """
        all_text_chunks = []
        
        for doc in documents:
            if document_type.lower() == 'pdf':
                text, metadata = self._extract_text_from_pdf(doc)
                self.current_doc_source = metadata.source
                self.current_doc_type = metadata.document_type
                
                text_chunks = self._split_text(text)
                all_text_chunks.extend(text_chunks)
                table, table_metadata = self._extract_table_from_pdf(doc)
                
                if not table.empty:
                    table_text = table.to_string(index=False) 
                    all_text_chunks.append((table_text, vars(table_metadata)))

            elif document_type.lower() == 'txt':
                text, metadata = self._extract_text_from_txt(doc)
                self.current_doc_source = metadata.source
                self.current_doc_type = metadata.document_type
                
                text_chunks = self._split_text(text)
                all_text_chunks.extend(text_chunks)

            else:
                raise ValueError(f"Unsupported document type: {document_type}")

        if self.vector_store is None:
            self.create_vector_store(documents, document_type, save_path)
        
        else:
            self.vector_store.add_texts(
                [chunk[0] for chunk in all_text_chunks],
                metadatas=[chunk[1] for chunk in all_text_chunks]
            )
        
        self.vector_store.save_local(save_path)

    def query_vector_store(self, query: str, top_k: int = 5) -> List[Tuple[str, DocumentMetadata]]:
        """ Query the vector store for a particular string.
            :param query: The query string to search for in the vector store 
            :param top_k: Number of top results to return (default is 5) 
            :return: A list of most similar text chunks and their associated metadata 
        """
        
        if self.vector_store is None:
            raise ValueError("Vector store is not loaded or created. Please create/load the vector store first.")
        
        results = self.vector_store.similarity_search(query, k=top_k)
        
        return [(result.page_content, result.metadata) for result in results]