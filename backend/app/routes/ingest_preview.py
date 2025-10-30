import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..services.ingest import file_to_chunks

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.get("/preview")
def preview_chunks(
    namespace: str = Query(..., description="Upload namespace"),
    filename: str = Query(..., description="A file name inside the namespace folder"),
    limit: int = Query(3, ge=1, le=10)
):
    folder = os.path.join("backend", "app", "uploads", namespace)
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found in this namespace")

    chunks = file_to_chunks(path, namespace)
    # only return first few snippets to keep response small
    preview = [
        {
            "text": c.text[:240] + ("..." if len(c.text) > 240 else ""),
            "metadata": c.metadata.model_dump()
        }
        for c in chunks[:limit]
    ]

    return {
        "namespace": namespace,
        "filename": filename,
        "total_chunks": len(chunks),
        "preview": preview
    }
