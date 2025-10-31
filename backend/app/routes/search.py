from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from ..ai.embeddings import embed_texts
from ..retriever.hybrid import dense_search, bm25_search, fuse_results

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def search(
    namespace: str = Query(...),
    q: str = Query(..., min_length=2),
    k: int = Query(8, ge=1, le=20),
    alpha: float = Query(0.6, ge=0.0, le=1.0)
) -> Dict[str, Any]:
    """
    Returns fused retrieval results for a query.
    - alpha controls weight: 1.0 = all dense, 0.0 = all BM25.
    """
    # 1) Embed query once for dense search
    qvec = embed_texts([q])[0]

    # 2) Run both searches
    d = dense_search(qvec, namespace=namespace, k=max(k, 20))
    b = bm25_search(q, namespace=namespace, k=max(k, 20))

    # 3) Fuse and trim
    fused = fuse_results(d, b, alpha=alpha, top_k=k)

    # 4) Shape response (snippet preview)
    items = []
    for pl, s in fused:
        snippet = pl.get("text", "")
        items.append({
            "score": round(float(s), 4),
            "filename": pl.get("filename"),
            "page": pl.get("page"),
            "namespace": pl.get("namespace"),
            "snippet": (snippet[:240] + "...") if len(snippet) > 240 else snippet
        })

    return {
        "query": q,
        "namespace": namespace,
        "alpha": alpha,
        "results": items
    }
