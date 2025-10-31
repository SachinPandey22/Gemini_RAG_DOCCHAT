from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..state.memory import add_turn, get_recent
from .intent import detect_intent
from ..ai.generator import generate_small_talk, generate_doc_answer
from ..ai.embeddings import embed_texts
from ..retriever.hybrid import dense_search, bm25_search, fuse_results

router = APIRouter(prefix="/ask", tags=["Ask"])

class AskReq(BaseModel):
    namespace: str
    question: str
    top_k: int = 4
    alpha: float = 0.6  # dense weight for fusion (0..1)

@router.post("/")
def ask(req: AskReq) -> Dict[str, Any]:
    ns = (req.namespace or "").strip()
    q = (req.question or "").strip()
    if not ns or not q:
        raise HTTPException(status_code=400, detail="namespace and question are required.")

    # 1) Save user turn
    add_turn(ns, "user", q)

    # 2) Intent route
    intent = detect_intent(q)

    if intent == "SMALL_TALK":
        history = get_recent(ns, max_turns=5)
        text = generate_small_talk(history, q)
        add_turn(ns, "assistant", text)
        return {
            "mode": "SMALL_TALK",
            "answer": text,
            "citations": []
        }

    # 3) DOC_QA path: retrieve, then generate grounded answer
    # 3a) embed query once for dense search
    qvec = embed_texts([q])[0]

    # 3b) run dense + bm25; fuse
    dense = dense_search(qvec, namespace=ns, k=max(req.top_k, 20))
    bm25  = bm25_search(q, namespace=ns, k=max(req.top_k, 20))
    fused = fuse_results(dense, bm25, alpha=req.alpha, top_k=req.top_k)

    # 3c) prepare context pack for the prompt
    contexts = []
    for pl, _score in fused:
        contexts.append({
            "text": pl.get("text", ""),
            "filename": pl.get("filename"),
            "page": pl.get("page")
        })

    # 3d) generate grounded answer
    history = get_recent(ns, max_turns=5)
    text = generate_doc_answer(history, q, contexts)

    # 3e) naive citation extraction from our own contexts list
    # (since we instructed the model to cite [filename (page X)], but we'll
    # also output our structured citations derived from contexts)
    citations = []
    for c in contexts:
        label = c["filename"] + (f" (page {c['page']})" if c.get("page") else "")
        citations.append({"label": label})

    add_turn(ns, "assistant", text)
    return {
        "mode": "DOC_QA",
        "answer": text,
        "citations": citations
    }
