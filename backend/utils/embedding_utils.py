"""
Embedding utilities for semantic search in the University Support System.
This module provides vector embedding functionality for all specialized tools.
"""

import os
import pickle
from typing import Dict, List, Tuple, Any, Optional

from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Singleton pattern to ensure we only load the model once
_model = None

def get_model():
    """Get or initialize the sentence transformer model"""
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text: str) -> np.ndarray:
    """Embed a single text string"""
    model = get_model()
    return model.encode(text)

def embed_items(items: List[Dict[str, Any]], 
                text_key: str = 'text', 
                id_key: str = 'id') -> Tuple[List[Dict[str, Any]], np.ndarray]:
    """
    Embeds a list of items, where each item is a dictionary.
    
    Args:
        items: List of dictionaries containing the items to embed
        text_key: Key in the dictionary containing the text to embed
        id_key: Key in the dictionary containing the ID of the item
        
    Returns:
        Tuple of (list of items, numpy array of embeddings)
    """
    model = get_model()
    texts = [item[text_key] for item in items]
    embeddings = model.encode(texts)
    return items, embeddings

def similarity_search(query: str, 
                      items: List[Dict[str, Any]], 
                      embeddings: np.ndarray, 
                      top_k: int = 3, 
                      threshold: float = 0.5) -> List[Tuple[Dict[str, Any], float]]:
    """
    Searches for similar items based on a query.
    
    Args:
        query: Query text
        items: List of items (dictionaries)
        embeddings: Numpy array of embeddings for each item
        top_k: Number of top results to return
        threshold: Minimum similarity score threshold
        
    Returns:
        List of tuples (item, similarity_score) sorted by similarity
    """
    print(f"\n[EMBEDDING DEBUG] Performing semantic search for query: '{query}'")
    print(f"[EMBEDDING DEBUG] Database contains {len(items)} items")
    
    query_embedding = embed_text(query)
    similarity_scores = cosine_similarity([query_embedding], embeddings)[0]
    
    # Get indices sorted by score in descending order
    indices = similarity_scores.argsort()[::-1]
    
    results = []
    for idx in indices:
        score = similarity_scores[idx]
        if score >= threshold and len(results) < top_k:
            item_id = items[idx].get('id', 'unknown')
            print(f"[EMBEDDING DEBUG] Match: '{item_id}' with score: {score:.4f}")
            results.append((items[idx], score))
    
    if not results:
        print(f"[EMBEDDING DEBUG] No matches found above threshold {threshold}")
    else:
        print(f"[EMBEDDING DEBUG] Found {len(results)} matches above threshold {threshold}")
    
    return results

def save_embeddings(items: List[Dict[str, Any]], 
                    embeddings: np.ndarray, 
                    filename: str):
    """Save embeddings and items to a file"""
    data = {
        'items': items,
        'embeddings': embeddings
    }
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_embeddings(filename: str) -> Tuple[List[Dict[str, Any]], np.ndarray]:
    """Load embeddings and items from a file"""
    if not os.path.exists(filename):
        return [], np.array([])
        
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data['items'], data['embeddings']

class EmbeddingIndex:
    """Class to manage an embedding index for semantic search"""
    
    def __init__(self, name: str, cache_dir: str = '/tmp'):
        self.name = name
        self.items = []
        self.embeddings = np.array([])
        self.cache_file = os.path.join(cache_dir, f"{name}_embeddings.pkl")
        
    def load_or_create(self, 
                       items: List[Dict[str, Any]] = None, 
                       text_key: str = 'text',
                       id_key: str = 'id',
                       force_rebuild: bool = False):
        """Load from cache or create embeddings from items"""
        if not force_rebuild and os.path.exists(self.cache_file):
            try:
                self.items, self.embeddings = load_embeddings(self.cache_file)
                return
            except Exception as e:
                print(f"Error loading embeddings: {e}")
        
        if items:
            self.items, self.embeddings = embed_items(items, text_key, id_key)
            save_embeddings(self.items, self.embeddings, self.cache_file)
    
    def search(self, 
               query: str, 
               top_k: int = 3, 
               threshold: float = 0.5) -> List[Tuple[Dict[str, Any], float]]:
        """Search the index with a query"""
        return similarity_search(query, self.items, self.embeddings, top_k, threshold)
