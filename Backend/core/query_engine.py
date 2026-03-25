from typing import Dict, List
from functools import lru_cache

import numpy as np
# ============================================================
# SHARED DEPENDENCY: sentence_transformers
# Used by BOTH chat (query encoding) and training (document embedding)
# ============================================================
from sentence_transformers import SentenceTransformer

from config.settings import settings
from core.mongo_store import documents_collection


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def _normalize_query(query: str) -> str:
    return " ".join((query or "").strip().split())


@lru_cache(maxsize=256)
def _encode_query_cached(normalized_query: str) -> tuple:
    vec = embedding_model.encode(
        normalized_query,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)
    return tuple(float(v) for v in vec)


def _build_result_from_items(query: str, ranked_items: List[Dict], top_k: int) -> Dict:
    unique_chunks: List[str] = []
    scores: List[float] = []
    top_results: List[Dict] = []

    for item in ranked_items:
        text = item.get("text", "")
        score = float(item.get("score", 0.0))
        metadata = item.get("metadata", {})

        if not text:
            continue

        unique_chunks.append(text)
        scores.append(score)
        top_results.append({"text": text, "score": score, "metadata": metadata})

        if len(unique_chunks) >= top_k:
            break

    context = "\n\n".join(unique_chunks)
    return {
        "query": query,
        "context": context,
        "top_docs": unique_chunks,
        "scores": scores,
        "top_results": top_results,
    }


def _query_with_atlas_vector_search(query: str, query_vec: np.ndarray, top_k: int) -> Dict:
    # Atlas Vector Search is the only retrieval path.
    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.mongo_vector_index_name,
                "path": "embedding",
                "queryVector": query_vec.tolist(),
                "numCandidates": max(settings.mongo_vector_num_candidates, top_k * 8),
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "source": 1,
                "source_name": 1,
                "chunk_index": 1,
                "pdf_name": 1,
                "pdf_link": 1,
                "category": 1,
                "jurisdiction": 1,
                "subcategory": 1,
                "fingerprint": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    try:
        docs = list(documents_collection.aggregate(pipeline, maxTimeMS=3000))
    except Exception as exc:
        raise RuntimeError(
            "MongoDB Atlas Vector Search failed. Verify Atlas cluster, vector index name, and embedding dimensions."
        ) from exc

    ranked_items: List[Dict] = []
    for item in docs:
        text = (item.get("text") or "").strip().replace("\n", " ")
        if not text:
            continue

        metadata = {
            "source": item.get("source", ""),
            "source_name": item.get("source_name", ""),
            "chunk_index": item.get("chunk_index", ""),
            "pdf_name": item.get("pdf_name", ""),
            "pdf_link": item.get("pdf_link", ""),
            "category": item.get("category", ""),
            "jurisdiction": item.get("jurisdiction", ""),
            "subcategory": item.get("subcategory", ""),
            "fingerprint": item.get("fingerprint", ""),
        }

        ranked_items.append(
            {
                "text": text,
                "score": float(item.get("score", 0.0)),
                "metadata": metadata,
            }
        )

    if not ranked_items:
        return {}

    return _build_result_from_items(query, ranked_items, top_k)


def _query_with_atlas_search(query: str, top_k: int) -> Dict:
    pipeline = [
        {
            "$search": {
                "index": settings.mongo_search_index_name,
                "text": {
                    "query": query,
                    "path": [
                        "text",
                        "pdf_name",
                        "source_name",
                        "category",
                        "jurisdiction",
                        "subcategory",
                    ],
                },
            }
        },
        {"$limit": top_k},
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "source": 1,
                "source_name": 1,
                "chunk_index": 1,
                "pdf_name": 1,
                "pdf_link": 1,
                "category": 1,
                "jurisdiction": 1,
                "subcategory": 1,
                "fingerprint": 1,
                "score": {"$meta": "searchScore"},
            }
        },
    ]

    try:
        docs = list(documents_collection.aggregate(pipeline, maxTimeMS=3000))
    except Exception as exc:
        raise RuntimeError(
            "MongoDB Atlas Search failed. Verify Atlas search index and dynamic mappings."
        ) from exc

    ranked_items: List[Dict] = []
    for item in docs:
        text = (item.get("text") or "").strip().replace("\n", " ")
        if not text:
            continue

        metadata = {
            "source": item.get("source", ""),
            "source_name": item.get("source_name", ""),
            "chunk_index": item.get("chunk_index", ""),
            "pdf_name": item.get("pdf_name", ""),
            "pdf_link": item.get("pdf_link", ""),
            "category": item.get("category", ""),
            "jurisdiction": item.get("jurisdiction", ""),
            "subcategory": item.get("subcategory", ""),
            "fingerprint": item.get("fingerprint", ""),
        }

        ranked_items.append(
            {
                "text": text,
                "score": float(item.get("score", 0.0)),
                "metadata": metadata,
            }
        )

    if not ranked_items:
        return {}

    return _build_result_from_items(query, ranked_items, top_k)


def search_atlas_direct(query: str, top_k: int = 5, mode: str = "auto") -> Dict:
    """
    Direct Atlas search utility.
    mode:
      - "vector": use Atlas Vector Search only
      - "search": use Atlas Search only
      - "auto": vector first, then Atlas Search fallback
    """
    if top_k <= 0:
        return {
            "query": query,
            "mode": mode,
            "context": "",
            "top_docs": [],
            "scores": [],
            "top_results": [],
        }

    normalized_query = _normalize_query(query)
    if not normalized_query:
        return {
            "query": query,
            "mode": mode,
            "context": "",
            "top_docs": [],
            "scores": [],
            "top_results": [],
        }

    mode = (mode or "auto").strip().lower()
    if mode not in {"auto", "vector", "search"}:
        raise ValueError("Invalid mode. Use 'auto', 'vector', or 'search'.")

    if mode == "search":
        result = _query_with_atlas_search(normalized_query, top_k)
        result["mode"] = "search"
        return result

    query_vec = np.asarray(_encode_query_cached(normalized_query), dtype=np.float32)

    vector_result = _query_with_atlas_vector_search(query, query_vec, top_k)
    if mode == "vector":
        vector_result["mode"] = "vector"
        return vector_result

    if vector_result.get("top_docs"):
        vector_result["mode"] = "vector"
        return vector_result

    search_result = _query_with_atlas_search(normalized_query, top_k)
    search_result["mode"] = "search"
    return search_result
