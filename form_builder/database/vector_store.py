# form_builder/database/vector_store.py

import json
import os
from typing import Dict, List, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

from form_builder.database.schema import FormTemplate
from form_builder.utils.helpers import generate_form_description


class FormVectorDB:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the Form Vector Database.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.encoder = SentenceTransformer(model_name)
        self.templates: List[FormTemplate] = []
        self.index = None
        
    def load_templates(self, template_dir: str) -> None:
        """Load all template JSON files from the given directory and its subdirectories.
        
        Args:
            template_dir (str): Path to the directory containing template JSON files
        """
        template_path = Path(template_dir)
        if not template_path.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
            
        for file_path in template_path.rglob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    data['form_description'] = generate_form_description(data)
                    
                    template = FormTemplate.from_dict(data, str(file_path))
                    self.templates.append(template)
                    
            except json.JSONDecodeError:
                print(f"Error loading template from {file_path}")
                continue
                
        print(f"Loaded {len(self.templates)} templates")
    
    def build_index(self) -> None:
        """Build FAISS index from loaded templates."""
        if not self.templates:
            raise ValueError("No templates loaded. Call load_templates first.")
            
        descriptions = [
        f"{template.form_description} | Operation Type: {template.operation_type} | Type: {template.type}"
        for template in self.templates
    ]
        print("-"*50, descriptions)
        embeddings = self.encoder.encode(descriptions)
        
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype(np.float32))
        
        print(f"Built index with {len(self.templates)} templates")
    
    def search_similar_forms(
        self, 
        query: str, 
        k: int = 15, 
        threshold: float = 0.9
    ) -> List[Tuple[FormTemplate, float]]:
        """Search for similar forms given a query.
        
        Args:
            query (str): The search query
            k (int): Number of results to return
            threshold (float): Minimum similarity score threshold
            
        Returns:
            List[Tuple[FormTemplate, float]]: List of (template, score) tuples
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")
            
        # Encode query and normalize
        query_embedding = self.encoder.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search index
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Debugging: Check all raw scores
        print(f"Raw distances: {distances[0]}")
        
        # Filter and return results above threshold
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.templates):  # Ensure valid index
                # Debugging output to understand filtering
                print(f"Index: {idx}, Distance: {distance}, Threshold: {threshold}")
                if distance >= threshold:
                    print(f"Accepted: {self.templates[idx].form_name} with score {distance}")
                    results.append((self.templates[idx], float(distance)))
                else:
                    print(f"Rejected: {self.templates[idx].form_name} with score {distance}")
        
        return results

    
    def save_index(self, save_dir: str) -> None:
        """Save the FAISS index and templates to disk.
        
        Args:
            save_dir (str): Directory to save the index and templates
        """
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
            
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_path / "form_index.faiss"))
        
        # Save templates using the to_dict method for each FormTemplate and its fields
        templates_data = [
            {
                "form_name": t.form_name,
                "form_description": t.form_description,
                "fields": [field.to_dict() for field in t.fields],  # Convert each FormField to dict
                "template_path": t.template_path,
                "operation_type": t.operation_type,
                "type": t.type
            }
            for t in self.templates
        ]
        
        with open(save_path / "templates.json", 'w') as f:
            json.dump(templates_data, f, indent=2)
            
    def load_index(self, load_dir: str) -> None:
        """Load a previously saved index and templates.
        
        Args:
            load_dir (str): Directory containing the saved index and templates
        """
        load_path = Path(load_dir)
        
        # Load FAISS index
        self.index = faiss.read_index(str(load_path / "form_index.faiss"))
        
        # Load templates
        with open(load_path / "templates.json", 'r') as f:
            templates_data = json.load(f)
            
        self.templates = [
            FormTemplate(**template_data)
            for template_data in templates_data
        ]