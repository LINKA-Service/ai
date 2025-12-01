from typing import List

import torch
from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(settings.embedding_model, device=device)
        self._initialized = True

    def encode_query(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_tensor=True)
        return embedding.cpu().tolist()

    def encode_document(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_tensor=True)
        return embedding.cpu().tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts, convert_to_tensor=True, show_progress_bar=True
        )
        return embeddings.cpu().tolist()
