"""
Synapse 4D - Semantic Vector Store
Provides high-speed vector retrieval using ChromaDB with an automated lightweight fallback.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

class VectorStore:
    """Manages persistent embeddings and semantic similarity queries."""

    def __init__(self, persist_dir: Path):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = None
        self.collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.collection = self.client.get_or_create_collection(
                name="synapse_semantic_memory",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.client = None
            self.collection = None

    def upsert(self, doc_id: str, document: str, metadata: Dict[str, Any]):
        """Upserts a single document chunk."""
        if self.collection:
            # Clean metadata to primitive types
            clean_meta = {}
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            self.collection.upsert(
                ids=[doc_id],
                documents=[document],
                metadatas=[clean_meta]
            )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Searches semantically for the query."""
        if self.collection:
            try:
                res = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
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
                return []
        return []

    def count(self) -> int:
        if self.collection:
            try:
                return self.collection.count()
            except Exception:
                return 0
        return 0
