import os
from typing import List, Iterable, Tuple
from pypdf import PdfReader
from . import text_utils
from docx import Document
from ..models.types import Chunk, ChunkMetadata

# ---------- TEXT EXTRACTION ----------

def extract_text_from_pdf(path: str) -> Iterable[Tuple[int, str]]:
    """
    Yields (page_index, page_text) for each page.
    Using a generator avoids loading the whole file into RAM.
    """
    reader = PdfReader(path)
    for i, page in enumerate(reader.pages):
        yield i, (page.extract_text() or "")

def extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_md(path: str) -> str:
    # For now, treat markdown as plain text. Later you can parse headings.
    return extract_text_from_txt(path)

def extract_text_from_docx(path: str) -> str:
    """
    Extracts all text from a DOCX file.
    """
    doc = Document(path)
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)

# ---------- CHUNKING ----------

def chunk_text(
    text: str,
    max_words: int = 600,
    overlap_words: int = 80
) -> List[str]:
    """
    Splits text into overlapping windows to preserve context across boundaries.
    - max_words: approx size per chunk
    - overlap_words: number of words repeated between chunks to avoid 'cut-off' loss
    """
    words = text_utils.to_words(text)
    chunks = []
    i = 0
    while i < len(words):
        window = words[i:i + max_words]
        if not window:
            break
        chunks.append(" ".join(window))
        # move forward by (max - overlap) so we keep overlap
        i += max_words - overlap_words
    return chunks

# ---------- HIGH-LEVEL: FILE -> CHUNKS ----------

def file_to_chunks(path: str, namespace: str) -> List[Chunk]:
    """
    Detects file type, extracts text, splits into chunks,
    returns a list of Chunk(text + metadata).
    """
    filename = os.path.basename(path).strip()
    ext = os.path.splitext(filename)[1].lower()
    source = path

    all_chunks: List[Chunk] = []

    if ext == ".pdf":
        # Create chunks page-by-page so we can keep precise page metadata
        for page_idx, page_text in extract_text_from_pdf(path):
            # Clean page text a bit
            clean = text_utils.normalize_whitespace(page_text)
            if not clean.strip():
                continue
            for piece in chunk_text(clean):
                all_chunks.append(Chunk(
                    text=piece,
                    metadata=ChunkMetadata(
                        filename=filename,
                        namespace=namespace,
                        page=page_idx + 1,  # 1-based page number
                        section=None,
                        source=source
                    )
                ))
    elif ext in (".txt", ".md", ".docx"):
        if ext == ".txt":
            raw = extract_text_from_txt(path)
        elif ext == ".md":
            raw = extract_text_from_md(path)
        else:  # .docx
            raw = extract_text_from_docx(path)
            clean = text_utils.normalize_whitespace(raw)
        if clean.strip():
            for piece in chunk_text(clean):
                all_chunks.append(Chunk(
                    text=piece,
                    metadata=ChunkMetadata(
                        filename=filename,
                        namespace=namespace,
                        page=None,
                        section=None,
                        source=source
                    )
                ))
    else:
        # Ignore unsupported types; your upload endpoint already filters types
        pass

    return all_chunks
