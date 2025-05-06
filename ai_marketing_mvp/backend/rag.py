import faiss, numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")  # 384‑d embeddings

class RAG:
    def __init__(self):
        self.index = {}      # ip  -> FAISS index
        self.memory = {}     # ip  -> list[(user, bot)]

    def _embed(self, text: str) -> np.ndarray:
        return np.asarray([_model.encode(text)], dtype="float32")

    def add(self, ip: str, user: str, bot: str):
        if ip not in self.index:
            d = self._embed(user).shape[1]
            self.index[ip] = faiss.IndexFlatL2(d)
            self.memory[ip] = []
        self.index[ip].add(self._embed(user))
        self.memory[ip].append((user, bot))

    def retrieve(self, ip: str, query: str, k: int = 5):
        if ip not in self.index or not self.memory[ip]:
            return []
        D, I = self.index[ip].search(self._embed(query), k)
        return [self.memory[ip][i] for i in I[0] if i < len(self.memory[ip])]
