# -*- coding: utf-8 -*-
"""Vector Store — Long-term memory using chromadb for semantic search.

Stores founder writing style, past posts, topic performance, and audience prefs.
Falls back gracefully when chromadb is not installed (uses JSON backup).

Usage:
    from memory_engine.vector_store import VectorStore
    vs = VectorStore()
    vs.add("post_123", "LinkedIn post about AI agents...", {"platform": "linkedin"})
    results = vs.search("AI agent content", top_k=5)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("memory")

VECTOR_DIR = Path(__file__).resolve().parent / "vectors"
FALLBACK_FILE = VECTOR_DIR / "fallback_store.json"

# Collection names
COLLECTIONS = {
    "posts": "past_successful_posts",
    "style": "founder_writing_style",
    "topics": "topic_performance",
    "audience": "audience_preferences",
}


class VectorStore:
    """Semantic memory store with chromadb backend and JSON fallback."""

    def __init__(self, collection: str = "posts"):
        self._collection_name = COLLECTIONS.get(collection, collection)
        self._client = None
        self._collection = None
        self._fallback_mode = False

        self._init_store()

    def _init_store(self):
        """Initialize chromadb or fall back to JSON."""
        try:
            import chromadb
            VECTOR_DIR.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(VECTOR_DIR))
            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Vector store initialized: %s (%d items)",
                        self._collection_name, self._collection.count())
        except ImportError:
            logger.info("chromadb not installed; using JSON fallback. Run: pip install chromadb")
            self._fallback_mode = True
            self._fallback_data = self._load_fallback()
        except Exception as exc:
            logger.warning("chromadb init failed: %s; using fallback", exc)
            self._fallback_mode = True
            self._fallback_data = self._load_fallback()

    def _load_fallback(self) -> List[Dict]:
        VECTOR_DIR.mkdir(parents=True, exist_ok=True)
        if FALLBACK_FILE.exists():
            try:
                return json.loads(FALLBACK_FILE.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def _save_fallback(self):
        FALLBACK_FILE.write_text(json.dumps(self._fallback_data, indent=2), encoding="utf-8")

    def add(self, doc_id: str, text: str, metadata: Optional[Dict] = None):
        """Add a document to the vector store.

        Args:
            doc_id: Unique identifier.
            text: Content text.
            metadata: Optional key-value metadata.
        """
        if self._fallback_mode:
            self._fallback_data.append({
                "id": doc_id, "text": text, "metadata": metadata or {},
            })
            self._save_fallback()
            return

        self._collection.upsert(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}],
        )

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for semantically similar documents.

        Args:
            query: Search text.
            top_k: Number of results.

        Returns:
            List of dicts with 'id', 'text', 'metadata', 'distance'.
        """
        if self._fallback_mode:
            # Simple keyword search fallback
            query_words = set(query.lower().split())
            scored = []
            for item in self._fallback_data:
                text_words = set(item.get("text", "").lower().split())
                overlap = len(query_words & text_words)
                if overlap > 0:
                    scored.append((overlap, item))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [
                {"id": item["id"], "text": item["text"], "metadata": item.get("metadata", {}), "distance": 0}
                for _, item in scored[:top_k]
            ]

        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, self._collection.count() or 1),
        )

        items = []
        for i, doc_id in enumerate(results.get("ids", [[]])[0]):
            items.append({
                "id": doc_id,
                "text": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0,
            })
        return items

    def count(self) -> int:
        """Return total items in the store."""
        if self._fallback_mode:
            return len(self._fallback_data)
        return self._collection.count()

    def delete(self, doc_id: str):
        """Delete a document by ID."""
        if self._fallback_mode:
            self._fallback_data = [d for d in self._fallback_data if d.get("id") != doc_id]
            self._save_fallback()
            return
        self._collection.delete(ids=[doc_id])


# ── Convenience stores ─────────────────────────────────────────────────────────

def posts_store() -> VectorStore:
    return VectorStore("posts")

def style_store() -> VectorStore:
    return VectorStore("style")

def topics_store() -> VectorStore:
    return VectorStore("topics")

def audience_store() -> VectorStore:
    return VectorStore("audience")
