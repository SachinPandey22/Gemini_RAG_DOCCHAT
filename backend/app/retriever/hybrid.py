from typing import List, Dict, Any, Tuple
from qdrant_client.http import models as rest
from ..db.qdrant_client import client, COLLECTION_NAME
from rank_bm25 import BM25Okapi

# --- Dense (Qdrant) ---

def dense_search(query_vec: List[float], namespace: str, k: int = 20):
    """
    Vector search in Qdrant, filtered by namespace.
    Returns list of (payload, score).
    """
    flt = rest.Filter(
        must=[rest.FieldCondition(key="namespace", match=rest.MatchValue(value=namespace))]
    )
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vec,
        limit=k,
        query_filter=flt,
    )
    # Qdrant similarity score: higher = more similar.
    return [ (h.payload, float(h.score)) for h in hits ]

# --- BM25 (keyword) ---

def _load_namespace_corpus(namespace: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Pull all texts + payloads for a namespace from Qdrant.
    We'll use this as our BM25 corpus.
    """
    texts, payloads = [], []
    # Scroll all points in this namespace (small projects: ok)
    next_page = None
    while True:
        resp = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=rest.Filter(
                must=[rest.FieldCondition(key="namespace", match=rest.MatchValue(value=namespace))]
            ),
            with_payload=True,
            limit=256,
            offset=next_page,
        )
        points, next_page = resp[0], resp[1]
        for p in points:
            txt = p.payload.get("text", "")
            if txt:
                texts.append(txt)
                payloads.append(p.payload)
        if next_page is None:
            break
    return texts, payloads

def bm25_search(query: str, namespace: str, k: int = 20):
    """
    Keyword search with BM25 over the namespace corpus.
    Returns list of (payload, score).
    """
    texts, payloads = _load_namespace_corpus(namespace)
    if not texts:
        return []
    tokenized = [t.split() for t in texts]   # simple whitespace tokens (good enough to learn)
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.split())
    # Pair each payload with its score and take top-k
    ranked = sorted(zip(payloads, scores), key=lambda x: x[1], reverse=True)[:k]
    return [ (pl, float(s)) for pl, s in ranked ]

# --- Score fusion ---

def fuse_results(
    dense: List[Tuple[Dict[str, Any], float]],
    bm25: List[Tuple[Dict[str, Any], float]],
    alpha: float = 0.6,   # weight for dense; (1-alpha) for bm25
    top_k: int = 8
):
    """
    Merge by payload identity (filename + page + text hash if you add one later),
    normalize each score list, then combine: alpha*dense + (1-alpha)*bm25.
    """
    # Build maps
    def key(pl):  # lightweight identity
        return (pl.get("filename"), pl.get("page"), pl.get("text")[:120])
    from collections import defaultdict

    # Gather raw scores
    d_map, b_map = {}, {}
    for pl, s in dense: d_map[key(pl)] = (pl, s)
    for pl, s in bm25: b_map[key(pl)] = (pl, s)

    # Normalize scores to [0,1] within each list
    def normalize(scores):
        if not scores: return {}
        vals = [s for _, s in scores]
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or 1.0
        return { key(pl): (pl, (s - lo) / span) for pl, s in scores }

    d_norm = normalize(dense)
    b_norm = normalize(bm25)

    # Fuse
    all_keys = set(d_norm.keys()) | set(b_norm.keys())
    fused = []
    for k in all_keys:
        pl = (d_norm.get(k, b_norm.get(k)))[0]
        ds = d_norm.get(k, (None, 0.0))[1]
        bs = b_norm.get(k, (None, 0.0))[1]
        fused_score = alpha * ds + (1 - alpha) * bs
        fused.append( (pl, fused_score) )

    fused.sort(key=lambda x: x[1], reverse=True)
    return fused[:top_k]
