from pydantic import BaseModel
from typing import Optional

class ChunkMetadata(BaseModel):
    filename: str
    namespace: str
    page: Optional[int] = None         # for PDFs when known
    section: Optional[str] = None      # placeholder for future heading-aware chunking
    source: Optional[str] = None       # e.g., "uploads/<ns>/<file>"
    uploaded_at: Optional[str] = None  # ISO string if you want to include it later

class Chunk(BaseModel):
    text: str
    metadata: ChunkMetadata
