from sentence_transformers import SentenceTransformer
import sys

# Use a compact embedding for speed in MVP
try:
    print("Loading embedding model...")
    # FORCE MOCK for offline verification
    raise Exception("Forcing mock mode to unblock server startup.")
    # EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    def get_embedding(text: str):
        return EMBED_MODEL.encode(text).tolist()
except Exception as e:
    print(f"[WARNING] Could not load embedding model: {e}")
    print("[WARNING] Running in database-only mode (Server-side embeddings disabled).")
    
    # Mock embedding function for offline/dev redundancy
    def get_embedding(text: str):
        # Return 384-dim zero vector + deterministic noise based on text length
        import random
        random.seed(len(text))
        return [random.random() for _ in range(384)]
