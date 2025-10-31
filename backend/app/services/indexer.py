import os
import glob
import uuid
from typing import List
from qdrant_client.models import PointStruct
from ..db.qdrant_client import client, COLLECTION_NAME
from ..ai.embeddings import embed_texts
from .ingest import file_to_chunks

def list_namespace_files(namespace: str) -> List[str]:
    """
    Returns absolute paths of files saved under uploads/<namespace>/...
    """
    base = os.path.join("backend", "app", "uploads", namespace)
    if not os.path.isdir(base):
        return []
    return glob.glob(os.path.join(base, "*"))

def chunks_to_points(texts: List[str], payloads: List[dict]) -> List[PointStruct]:
    """
    Convert a batch of texts into vectors + PointStructs for Qdrant.
    """
    vectors = embed_texts(texts)  # -> List[List[float]] (768-dim)
    points: List[PointStruct] = []
    for vec, pl in zip(vectors, payloads):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),  # random stable-ish ID
                vector=vec,
                payload=pl
            )
        )
    return points

def index_namespace(namespace: str, batch_size: int = 32) -> dict:
    """
    For every file in a namespace:
      - build chunks with metadata
      - embed in batches
      - upsert into Qdrant
    Returns a small summary (files, chunks, points).
    """
    files = list_namespace_files(namespace)
    total_chunks = 0
    total_points = 0

    for path in files:
        # Build structured chunks (Story 3)
        chunks = file_to_chunks(path, namespace)
        if not chunks:
            continue

        # Batch by texts and payloads for efficient embedding/upsert
        batch_texts, batch_payloads = [], []
        for ch in chunks:
            batch_texts.append(ch.text)
            payload = ch.metadata.model_dump()
            payload["text"] = ch.text  # store text for retrieval + snippets
            batch_payloads.append(payload)

            # When batch is full, embed + upsert
            if len(batch_texts) >= batch_size:
                pts = chunks_to_points(batch_texts, batch_payloads)
                client.upsert(collection_name=COLLECTION_NAME, points=pts)
                total_points += len(pts)
                batch_texts, batch_payloads = [], []

        # Flush any remainder
        if batch_texts:
            pts = chunks_to_points(batch_texts, batch_payloads)
            client.upsert(collection_name=COLLECTION_NAME, points=pts)
            total_points += len(pts)

        total_chunks += len(chunks)

    return {
        "namespace": namespace,
        "files_indexed": len(files),
        "chunks_processed": total_chunks,
        "points_upserted": total_points
    }
