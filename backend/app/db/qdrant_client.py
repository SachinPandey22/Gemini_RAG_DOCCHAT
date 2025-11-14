import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http import models as rest

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))  # temp default; update later if needed

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

def ensure_collection():
    # create if missing; safe to call on startup
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.recreate_collection(
            COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
    # Ensure we can filter by namespace efficiently. Without this, Qdrant rejects
    # search filters that reference the field.
    payload_schema = (client.get_collection(COLLECTION_NAME).payload_schema) or {}
    if "namespace" not in payload_schema:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="namespace",
            field_schema=rest.PayloadSchemaType.KEYWORD,
        )
