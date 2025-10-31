import os
import google.generativeai as genai
from tenacity import retry, wait_exponential, stop_after_attempt

# 1) Read API key from env and configure the SDK once.
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2) Choose the embeddings model (Gemini's current recommended one).
EMBED_MODEL = "text-embedding-004"

def _ensure_text(x: str) -> str:
    """
    Small guard: make sure inputs are strings and trimmed.
    """
    return (x or "").strip()

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(5))
def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Create embeddings for a list of strings.
    - We retry on transient errors (network, rate limit) using tenacity.
    - Returns a list of 768-dim vectors (one per input).
    """
    clean = [_ensure_text(t) for t in texts]
    # The Gemini SDK supports batch embedding via embed_content with list inputs.
    resp = genai.embed_content(
        model=EMBED_MODEL,
        content=clean,
        task_type="retrieval_document"  # hint to the model about use-case
    )
    # SDK returns dict with 'embedding' or list under 'embeddings'
    # Normalize to a list of vectors.
    # Newer SDKs: resp['embedding'] when single, resp['embeddings'] when batch.
# The response has an 'embedding' attribute containing the vectors
# For batch requests, it's a list of dicts with 'values'
    if hasattr(resp, 'embedding'):
        # Single embedding
        return [resp['embedding']]
    elif hasattr(resp, 'embeddings'):
        # Batch embeddings - extract the values
        return [emb['values'] if isinstance(emb, dict) else emb for emb in resp['embeddings']]
    else:
        # Fallback - try dict access
        embeddings = resp.get('embedding') or resp.get('embeddings', [])
        if isinstance(embeddings, list):
            return [e['values'] if isinstance(e, dict) else e for e in embeddings]
        return [embeddings]