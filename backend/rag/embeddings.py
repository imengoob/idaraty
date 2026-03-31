from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingManager:
    """Gestionnaire d'embeddings pour le RAG"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialise le modèle d'embeddings
        
        Args:
            model_name: Nom du modèle Sentence Transformers
        """
        print(f"🔧 Chargement du modèle d'embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"✅ Modèle chargé (dimension: {self.dimension})")
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode une liste de textes en embeddings
        
        Args:
            texts: Liste de textes à encoder
            
        Returns:
            Array numpy d'embeddings
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        
        return embeddings.astype('float32')
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode un seul texte
        
        Args:
            text: Texte à encoder
            
        Returns:
            Array numpy de l'embedding
        """
        return self.encode_texts([text])[0]
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calcule la similarité cosinus entre deux embeddings
        
        Args:
            emb1: Premier embedding
            emb2: Deuxième embedding
            
        Returns:
            Score de similarité (0-1)
        """
        # Normaliser
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)
        
        # Produit scalaire
        similarity = np.dot(emb1_norm, emb2_norm)
        
        return float(similarity)


# Instance globale (optionnel)
embedding_manager = EmbeddingManager()