import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/")
async def upload_files(
    files: List[UploadFile] = File(...),
    namespace: str = Form("default")
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    # Make directory for this namespace
    folder = os.path.join("backend", "app", "uploads", namespace)
    os.makedirs(folder, exist_ok=True)

    saved_files = []
    for file in files:
        if not file.filename.lower().endswith((".pdf", ".txt", ".md", ".docx")):
            continue  # skip unsupported types

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(folder, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        saved_files.append({
            "filename": filename,
            "size_kb": round(os.path.getsize(filepath) / 1024, 2)
        })

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid files uploaded (PDF, TXT, MD, docx only).")

    return {
        "namespace": namespace,
        "files_saved": saved_files,
        "count": len(saved_files)
    }
