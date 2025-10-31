from fastapi import APIRouter, HTTPException, Query
from ..services.indexer import index_namespace

router = APIRouter(prefix="/index", tags=["Indexing"])

@router.post("/")
def index_now(namespace: str = Query(..., description="Namespace to index")):
    if not namespace.strip():
        raise HTTPException(status_code=400, detail="Namespace required")
    summary = index_namespace(namespace=namespace)
    return summary
