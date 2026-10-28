"""
Synapse 4D - Multi-Modal Vector Store
Supports high-performance ChromaDB when installed, with a zero-dependency
embedded TF-IDF cosine similarity vector engine as a resilient fallback.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import math
import re

class VectorStore:
    """Manages persistent embeddings and semantic similarity queries."""

    def __init__(self, persist_dir: Path):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.fallback_file = self.persist_dir / "embedded_vectors.json"
        self.client = None
        self.collection = None
        self.local_docs = self._load_fallback()
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = self.client.get_or_create_collection(
                name="synapse_semantic_memory",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.client = None
            self.collection = None

    def _load_fallback(self) -> Dict[str, Any]:
        if self.fallback_file.exists():
            try:
                return json.loads(self.fallback_file.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_fallback(self):
        self.fallback_file.write_text(json.dumps(self.local_docs, indent=2, ensure_ascii=False), encoding="utf-8")

    def _tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r'\w+', text.lower()) if len(w) > 2]

    def upsert(self, doc_id: str, document: str, metadata: Dict[str, Any]):
        """Upserts a single document chunk into Chroma and local persistent storage."""
        # Clean metadata
        clean_meta = {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in metadata.items()}

        # 1. Local fallback storage
        tokens = self._tokenize(document)
        self.local_docs[doc_id] = {
            "document": document,
            "metadata": clean_meta,
            "tokens": tokens
        }
        self._save_fallback()

        # 2. Chroma storage if available
        if self.collection:
            try:
                self.collection.upsert(
                    ids=[doc_id],
                    documents=[document],
                    metadatas=[clean_meta]
                )
            except Exception:
                pass

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Searches semantically for the query using Chroma or embedded vector engine."""
        # Try Chroma first
        if self.collection:
            try:
                res = self.collection.query(query_texts=[query_text], n_results=n_results)
                hits = []
                if res and res.get("documents") and res["documents"][0]:
                    docs = res["documents"][0]
                    metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(docs)
                    distances = res["distances"][0] if res.get("distances") else [0.0] * len(docs)
                    ids = res["ids"][0] if res.get("ids") else [""] * len(docs)

                    for d, m, dist, cid in zip(docs, metas, distances, ids):
                        hits.append({
                            "id": cid,
                            "document": d,
                            "metadata": m,
                            "score": round(1.0 - dist, 4) if dist is not None else 1.0
                        })
                    return hits
            except Exception:
                pass

        # Resilient Embedded TF-IDF Cosine Matcher
        q_tokens = self._tokenize(query_text)
        if not q_tokens or not self.local_docs:
            return []

        q_tf = {}
        for t in q_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1

        scored = []
        n_docs = len(self.local_docs)

        for doc_id, data in self.local_docs.items():
            doc_tokens = data.get("tokens", [])
            if not doc_tokens:
                continue

            doc_tf = {}
            for t in doc_tokens:
                doc_tf[t] = doc_tf.get(t, 0) + 1

            # Compute Cosine similarity
            dot_product = sum(q_tf[t] * doc_tf.get(t, 0) for t in q_tf)
            q_norm = math.sqrt(sum(v ** 2 for v in q_tf.values()))
            doc_norm = math.sqrt(sum(v ** 2 for v in doc_tf.values()))

            if q_norm > 0 and doc_norm > 0 and dot_product > 0:
                sim = dot_product / (q_norm * doc_norm)
                scored.append({
                    "id": doc_id,
                    "document": data["document"],
                    "metadata": data["metadata"],
                    "score": round(sim, 4)
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:n_results]

    def count(self) -> int:
        if self.collection:
            try:
                c = self.collection.count()
                if c > 0:
                    return c
            except Exception:
                pass
        return len(self.local_docs)
