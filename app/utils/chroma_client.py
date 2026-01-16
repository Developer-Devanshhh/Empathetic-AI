import os
import chromadb
from chromadb.config import Settings
from ..utils.embeddings import get_embedding
from datetime import datetime

from ..utils.security import encrypt_text, decrypt_text

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
client = chromadb.PersistentClient(path=PERSIST_DIR)

def get_collection(name="journals"):
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name)

def add_entry(collection, doc_id: str, text: str, metadata: dict, embedding: list = None):
    if embedding is None:
        embedding = get_embedding(text)
    metadata["timestamp"] = datetime.utcnow().isoformat()
    
    # 🔒 ENCRYPT SENSITIVE DATA
    encrypted_text = encrypt_text(text)
    
    collection.add(
        ids=[doc_id],
        documents=[encrypted_text],
        metadatas=[metadata],
        embeddings=[embedding],
    )

def get_recent_entries(collection, user_id: str, limit: int = 5):
    # Fetch embeddings explicitly
    # Exclude safety-flagged entries from history
    results = collection.get(
        where={
            "$and": [
                {"user_id": user_id},
                {"safety_flag": {"$ne": True}}
            ]
        }, 
        include=["documents", "metadatas", "embeddings"]
    )
    
    if not results or len(results["ids"]) == 0:
        return []

    # Zip data together
    entries = []
    for i in range(len(results["ids"])):
        # 🔓 DECRYPT SENSITIVE DATA
        decrypted_text = decrypt_text(results["documents"][i])
        
        entries.append({
            "text": decrypted_text,
            "metadata": results["metadatas"][i],
            "embedding": results["embeddings"][i]
        })
    
    # Sort by timestamp (ensure chronological order)
    entries.sort(key=lambda x: x["metadata"].get("timestamp", ""))

    # Return last N entries
    return entries[-limit:]

def query_similar(collection, text: str, n_results: int = 10):
    embedding = get_embedding(text)
    
    # Exclude safety-flagged entries from RAG context
    # Use broader n_results to allow for filtering and re-ranking
    res = collection.query(
        query_embeddings=[embedding], 
        n_results=n_results,
        where={"safety_flag": {"$ne": True}},
        include=["documents", "metadatas", "distances"]
    )
    
    if "documents" not in res or not res["documents"]:
        return []
    
    # Flatten lists (Chroma returns list of lists)
    docs = res["documents"][0]
    metadatas = res["metadatas"][0]
    distances = res["distances"][0]
    
    if not docs:
        return []
        
    scored_entries = []
    
    for i in range(len(docs)):
        meta = metadatas[i]
        
        # 🔓 DECRYPT SENSITIVE DATA
        decrypted_text = decrypt_text(docs[i])
        
        # 1. Similarity
        # Chroma returns distance (lower is better). similarity = 1 - distance (approx)
        dist = distances[i]
        similarity = max(0, 1 - dist)
        
        # 2. Emotion Weighting
        # Cap emotion influence to avoid domination
        emotion_score = meta.get("emotion_score", 0.0)
        emotion_factor = 1 + min(emotion_score, 0.5)
        
        # 3. Time Decay
        # Default to now if no timestamp
        ts_str = meta.get("timestamp")
        if ts_str:
            try:
                entry_dt = datetime.fromisoformat(ts_str)
                days_since = (datetime.utcnow() - entry_dt).days
                days_since = max(0, days_since)
            except ValueError:
                days_since = 0
        else:
            days_since = 0
            
        decay_factor = 1 / (1 + 0.1 * days_since)
        
        # Final Score
        final_score = similarity * emotion_factor * decay_factor
        
        scored_entries.append({
            "text": decrypted_text,
            "score": final_score
        })
        
    # Sort by final score descending
    scored_entries.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 3 text only
    return [e["text"] for e in scored_entries[:3]]

def delete_entry(collection, doc_id: str):
    """Deletes a single entry by ID."""
    collection.delete(ids=[doc_id])

def delete_user_entries(collection, user_id: str):
    """Deletes ALL entries for a specific user."""
    collection.delete(where={"user_id": user_id})

def get_all_entries_for_dashboard(collection, user_id: str, limit: int = 50):
    """Retrieves list of entries specifically for the dashboard (with IDs)."""
    results = collection.get(
        where={"user_id": user_id},
        include=["documents", "metadatas"],
        limit=limit
    )
    
    if not results or len(results["ids"]) == 0:
        return []
        
    entries = []
    for i in range(len(results["ids"])):
        # Decrypt text
        decrypted = decrypt_text(results["documents"][i])
        
        entries.append({
            "id": results["ids"][i],
            "text": decrypted,
            "metadata": results["metadatas"][i]
        })
    
    # Sort distinct by timestamp desc
    entries.sort(key=lambda x: x["metadata"].get("timestamp", ""), reverse=True)
    return entries
