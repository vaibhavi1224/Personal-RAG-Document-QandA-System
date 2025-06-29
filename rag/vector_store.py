import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorStore:
    """Handles vector embeddings and similarity search"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.embeddings = []

    def add_documents(self, chunks: List[Dict[str, Any]]):
        texts = [c['text'] for c in chunks]
        new_embeds = self.model.encode(texts)
        if len(self.embeddings) == 0:
            self.embeddings = new_embeds
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeds])

        self.chunks.extend(chunks)
        self._build_index()

    def _build_index(self):
        if len(self.embeddings) > 0:
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            faiss.normalize_L2(self.embeddings.astype('float32'))
            self.index.add(self.embeddings.astype('float32'))

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.index is None or len(self.chunks) == 0:
            return []
        q_embed = self.model.encode([query])
        faiss.normalize_L2(q_embed.astype('float32'))
        scores, indices = self.index.search(q_embed.astype('float32'), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                r = self.chunks[idx].copy()
                r['similarity_score'] = float(score)
                results.append(r)
        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_chunks': len(self.chunks),
            'embedding_dimension': self.embeddings.shape[1] if len(self.embeddings) > 0 else 0,
            'unique_sources': len(set(c['source'] for c in self.chunks))
        }
