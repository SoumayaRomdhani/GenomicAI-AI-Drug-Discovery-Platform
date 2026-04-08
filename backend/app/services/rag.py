from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import settings

try:
    import chromadb
    from sentence_transformers import SentenceTransformer

    HAS_EMBEDDINGS = True
except Exception:
    HAS_EMBEDDINGS = False


class BiomedicalRAGService:
    def __init__(self) -> None:
        self.demo_path = Path(settings.pubmed_demo_path)
        self.docs = self._load_docs()
        self.backend_name = "tfidf"
        self.tfidf = None
        self.matrix = None
        self.embedder = None
        self.collection = None
        self._build()

    def _load_docs(self) -> List[dict]:
        with self.demo_path.open("r", encoding="utf-8") as f:
            docs = json.load(f)
        normalized = []
        for idx, doc in enumerate(docs):
            normalized.append(
                {
                    "doc_id": doc.get("doc_id", f"demo-{idx+1}"),
                    "title": doc["title"],
                    "source": doc.get("source", "Demo Biomedical Corpus"),
                    "year": doc.get("year"),
                    "abstract": doc["abstract"],
                }
            )
        return normalized

    def _build(self) -> None:
        texts = [f'{d["title"]}. {d["abstract"]}' for d in self.docs]

        if HAS_EMBEDDINGS and settings.use_sentence_transformers:
            try:
                self.embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                embeddings = self.embedder.encode(texts, convert_to_numpy=True)
                if settings.use_chroma:
                    persist_dir = Path(settings.rag_persist_dir)
                    persist_dir.mkdir(parents=True, exist_ok=True)
                    client = chromadb.PersistentClient(path=str(persist_dir))
                    name = "biomedical_docs"
                    existing = [c.name for c in client.list_collections()]
                    if name in existing:
                        client.delete_collection(name)
                    self.collection = client.create_collection(name=name)
                    self.collection.add(
                        ids=[d["doc_id"] for d in self.docs],
                        documents=texts,
                        metadatas=[
                            {"title": d["title"], "source": d["source"], "year": d.get("year")}
                            for d in self.docs
                        ],
                        embeddings=embeddings.tolist(),
                    )
                    self.backend_name = "sentence_transformers+chroma"
                    return
                self.embeddings = embeddings
                self.backend_name = "sentence_transformers"
                return
            except Exception:
                pass

        self.tfidf = TfidfVectorizer(stop_words="english")
        self.matrix = self.tfidf.fit_transform(texts)
        self.backend_name = "tfidf"

    def query(self, query: str, top_k: int = 3) -> dict:
        top_k = max(1, min(top_k, len(self.docs)))

        if self.collection is not None and self.embedder is not None:
            query_embedding = self.embedder.encode([query], convert_to_numpy=True)[0].tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            docs = []
            for doc_id, meta, document, distance in zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0],
            ):
                docs.append(
                    {
                        "doc_id": doc_id,
                        "title": meta["title"],
                        "source": meta.get("source", "Corpus"),
                        "year": meta.get("year"),
                        "score": round(1 - float(distance), 4),
                        "snippet": document[:320] + ("..." if len(document) > 320 else ""),
                    }
                )
            return self._format_response(query, docs)

        if getattr(self, "embedder", None) is not None:
            q = self.embedder.encode([query], convert_to_numpy=True)[0]
            norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q)
            sims = (self.embeddings @ q) / np.maximum(norms, 1e-8)
            order = np.argsort(-sims)[:top_k]
            docs = [
                {
                    "doc_id": self.docs[i]["doc_id"],
                    "title": self.docs[i]["title"],
                    "source": self.docs[i]["source"],
                    "year": self.docs[i]["year"],
                    "score": round(float(sims[i]), 4),
                    "snippet": self.docs[i]["abstract"][:320] + ("..." if len(self.docs[i]["abstract"]) > 320 else ""),
                }
                for i in order
            ]
            return self._format_response(query, docs)

        q = self.tfidf.transform([query])
        scores = (self.matrix @ q.T).toarray().ravel()
        order = np.argsort(-scores)[:top_k]
        docs = [
            {
                "doc_id": self.docs[i]["doc_id"],
                "title": self.docs[i]["title"],
                "source": self.docs[i]["source"],
                "year": self.docs[i]["year"],
                "score": round(float(scores[i]), 4),
                "snippet": self.docs[i]["abstract"][:320] + ("..." if len(self.docs[i]["abstract"]) > 320 else ""),
            }
            for i in order
        ]
        return self._format_response(query, docs)

    def _format_response(self, query: str, docs: List[dict]) -> dict:
        if not docs:
            answer = "No relevant biomedical documents were found in the local corpus."
        else:
            answer = (
                "Top documents suggest that current biomedical AI workflows combine molecular representation learning, "
                "protein modeling, and retrieval over literature to improve hypothesis generation. "
                f"The most relevant source here is '{docs[0]['title']}'."
            )

        return {
            "query": query,
            "answer": answer,
            "documents": docs,
            "backend": self.backend_name,
        }
