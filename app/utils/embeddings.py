from sentence_transformers import SentenceTransformer

# Use a compact embedding for speed in MVP
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    return EMBED_MODEL.encode(text).tolist()
