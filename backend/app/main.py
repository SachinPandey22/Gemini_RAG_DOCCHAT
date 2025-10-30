from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.qdrant_client import ensure_collection

app = FastAPI(title="Gemini RAG DocChat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    ensure_collection()

@app.get("/health")
def health():
    return {"status": "ok", "message": "API is running"}
@app.get("/qdrant")
def qdrant_ping():
    return {"collection": "docs", "status": "ready"}
