import os
import chromadb
from chromadb.config import Settings
from ..utils.embeddings import get_embedding
from datetime import datetime

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
client = chromadb.PersistentClient(path=PERSIST_DIR)

def get_collection(name="journals"):
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name)

def add_entry(collection, doc_id: str, text: str, metadata: dict):
    embedding = get_embedding(text)
    metadata["timestamp"] = datetime.utcnow().isoformat()
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata],
        embeddings=[embedding],
    )

def get_recent_entries(collection, user_id: str, limit: int = 5):
    results = collection.get(where={"user_id": user_id})
    if not results or len(results["ids"]) == 0:
        return []
    docs = results["documents"][-limit:]
    return docs

def query_similar(collection, text: str, n_results: int = 3):
    embedding = get_embedding(text)
    res = collection.query(query_embeddings=[embedding], n_results=n_results)
    if "documents" not in res or not res["documents"]:
        return []
    return res["documents"][0]
