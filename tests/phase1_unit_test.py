import sys
import os
import time
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.chroma_client import query_similar, add_entry, get_collection
from app.utils.distortions import analyzer
from app.utils.embeddings import get_embedding

def test_memory_decay():
    print("Testing Memory Decay...")
    try:
        client = get_collection("test_memory_decay")
        # Clear collection if exists? 
        # For simplicity, use unique text
        import uuid
        uid = str(uuid.uuid4())[:8]
        
        # Add "Old" entry with EXACT match text (Similarity = 1.0)
        # But make it 100 days old. Decay = 1 / (1 + 10) = 0.09
        doc_id_old = f"old_entry_{uid}"
        text_old = f"I love coding in Python {uid}."
        meta_old = {"user_id": "test", "emotion": "joy", "emotion_score": 0.9, "timestamp": (datetime.utcnow() - timedelta(days=100)).isoformat()}
        
        emb_old = get_embedding(text_old)
        client.add(ids=[doc_id_old], documents=[text_old], metadatas=[meta_old], embeddings=[emb_old])
        
        # Add "Recent" entry with MODERATE match (Similarity ~0.7)
        # But it's new. Decay = 1.
        doc_id_new = f"new_entry_{uid}"
        text_new = f"I like writing code {uid}." 
        meta_new = {"user_id": "test", "emotion": "joy", "emotion_score": 0.9, "timestamp": datetime.utcnow().isoformat()}
        
        emb_new = get_embedding(text_new)
        client.add(ids=[doc_id_new], documents=[text_new], metadatas=[meta_new], embeddings=[emb_new])
        
        # Query for "I love coding in Python <uid>."
        query_text = text_old
        results = query_similar(client, query_text, n_results=10)
        
        print(f"Top Result: {results[0] if results else 'None'}")
        
        # Logic:
        # Old Entry: Sim=1.0. EmFactor=1.5. Decay=0.09. Score = 0.135
        # New Entry: Sim~0.7. EmFactor=1.5. Decay=1.0. Score = 1.05
        # New must win.
        
        if results and results[0] == text_new:
            print("[PASS] Recent (less similar) beat Old (exact match) due to decay.")
        elif results and results[0] == text_old:
            print(f"[FAIL] Old entry ranked first. Decay logic might be weak or similarity dominates.")
        else:
            print(f"[FAIL] Unexpected result structure: {results}")

    except Exception as e:
        print(f"[ERROR] Memory Test Failed: {e}")

def test_distortions():
    print("\nTesting Distortions...")
    
    # 1. Positive Case (High Emotion)
    text_catastrophic = "I ruined everything, my life is a total disaster."
    score_high = 0.9
    detected = analyzer.analyze(text_catastrophic, score_high)
    if "catastrophizing" in detected:
        print(f"[PASS] Detected catastrophizing with high emotion (Score: {score_high}).")
    else:
        print(f"[FAIL] Failed to detect catastrophizing. Detected: {detected}")

    # 2. Negative Case (Low Emotion)
    text_factual = "I always wake up at 7 am."
    score_low = 0.3
    detected = analyzer.analyze(text_factual, score_low)
    if not detected:
        print(f"[PASS] Correctly ignored factual statement with low emotion (Score: {score_low}).")
    else:
        print(f"[FAIL] False positive on factual statement. Detected: {detected}")

if __name__ == "__main__":
    test_memory_decay()
    test_distortions()
