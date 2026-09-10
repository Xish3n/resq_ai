"""
RAG Knowledge Retriever for ResQ-AI.

Loads plain-text emergency-response guideline documents from backend/data/,
splits them into chunks, embeds them, and retrieves the most relevant
chunks for a given query.

Primary path: sentence-transformers embeddings + FAISS similarity search.
Fallback path: scikit-learn TF-IDF + cosine similarity, used automatically
if the embedding model cannot be loaded (e.g. no internet access at a
hackathon venue). Either way the API surface (`retrieve`) is identical,
so the rest of the app does not need to know which backend is active.
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from typing import List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@dataclass
class Chunk:
    doc_name: str
    text: str


def _load_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.txt"))):
        doc_name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # Split into paragraph-sized chunks (blank-line separated).
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for para in paragraphs:
            # Keep the TITLE line attached to the first real chunk for context.
            chunks.append(Chunk(doc_name=doc_name, text=para))
    return chunks


class KnowledgeRetriever:
    """Retrieves relevant emergency-guideline chunks for a query."""

    def __init__(self):
        self.chunks: List[Chunk] = _load_chunks()
        self.backend = "none"
        self._embedder = None
        self._index = None
        self._vectorizer = None
        self._tfidf_matrix = None
        self._build_index()

    def _build_index(self) -> None:
        # Try the embeddings + FAISS path first.
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            import numpy as np

            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            vectors = self._embedder.encode(
                [c.text for c in self.chunks], normalize_embeddings=True
            )
            vectors = np.asarray(vectors, dtype="float32")
            dim = vectors.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(vectors)
            self._index = index
            self.backend = "faiss+minilm"
            return
        except Exception:
            pass

        # Fallback: TF-IDF, which has no download/network dependency.
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            self._vectorizer = TfidfVectorizer(stop_words="english")
            self._tfidf_matrix = self._vectorizer.fit_transform(
                [c.text for c in self.chunks]
            )
            self.backend = "tfidf"
        except Exception:
            self.backend = "keyword"

    def retrieve(self, query: str, top_k: int = 4) -> List[dict]:
        """Return top_k most relevant chunks as dicts with source + text."""
        if not self.chunks:
            return []

        if self.backend == "faiss+minilm":
            import numpy as np

            q_vec = self._embedder.encode([query], normalize_embeddings=True)
            q_vec = np.asarray(q_vec, dtype="float32")
            scores, idxs = self._index.search(q_vec, min(top_k, len(self.chunks)))
            results = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx == -1:
                    continue
                c = self.chunks[idx]
                results.append(
                    {"source": c.doc_name, "text": c.text, "score": float(score)}
                )
            return results

        if self.backend == "tfidf":
            from sklearn.metrics.pairwise import cosine_similarity

            q_vec = self._vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self._tfidf_matrix)[0]
            top_idx = sims.argsort()[::-1][:top_k]
            results = []
            for idx in top_idx:
                if sims[idx] <= 0:
                    continue
                c = self.chunks[idx]
                results.append(
                    {"source": c.doc_name, "text": c.text, "score": float(sims[idx])}
                )
            return results

        # Last-resort keyword overlap scoring, no external deps at all.
        q_words = set(re.findall(r"[a-zA-Z]+", query.lower()))
        scored = []
        for c in self.chunks:
            c_words = set(re.findall(r"[a-zA-Z]+", c.text.lower()))
            overlap = len(q_words & c_words)
            if overlap:
                scored.append((overlap, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"source": c.doc_name, "text": c.text, "score": float(score)}
            for score, c in scored[:top_k]
        ]


# Singleton instance built once at import time, reused by the agents.
retriever = KnowledgeRetriever()
