import numpy as np

def normalize_embedding(embedding):
    """Normalize a vector to unit length."""
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm

def calculate_volatility(current_embedding, past_entries, current_emotion, threshold=0.3):
    """
    Calculates mood volatility based on cosine distance between consecutive embeddings.
    
    Args:
        current_embedding: List or array of floats (current entry vector).
        past_entries: List of dicts, each containing 'embedding' and 'metadata'.
                      Expected to be sorted chronologically.
        current_emotion: The emotion label of the current entry.
        threshold: The cosine distance threshold to flag a mood swing.
        
    Returns:
        dict: {
            "mood_swing": bool,
            "volatility_score": float, # Mean cosine distance
            "message": str
        }
    """
    if not past_entries:
        return {"mood_swing": False, "volatility_score": 0.0, "message": "First entry."}

    # 1. Prepare embeddings list (oldest -> newest -> current)
    # We only care about the sequence.
    
    # Convert all to numpy arrays and normalize
    vectors = [normalize_embedding(np.array(e["embedding"])) for e in past_entries]
    curr_vec = normalize_embedding(np.array(current_embedding))
    vectors.append(curr_vec)
    
    # 2. Calculate consecutive cosine distances
    distances = []
    for i in range(len(vectors) - 1):
        # Cosine Distance = 1 - Cosine Similarity
        # matching Scikit-learn definition
        sim = np.dot(vectors[i], vectors[i+1])
        dist = 1 - sim
        distances.append(dist)
        
    # 3. Compute mean volatility
    if not distances:
        volatility = 0.0
    else:
        volatility = float(np.mean(distances))
        
    # 4. Check for mood swing
    # Condition: High volatility AND Emotion Change
    # (Pre-requisite: We need the previous emotion to compare)
    last_emotion = past_entries[-1]["metadata"].get("emotion", "")
    
    emotion_changed = (last_emotion != current_emotion) and (last_emotion != "")
    
    is_swing = (volatility > threshold) and emotion_changed
    
    return {
        "mood_swing": is_swing,
        "volatility_score": volatility,
        "message": f"Volatility: {volatility:.2f}, Emotion Change: {emotion_changed}"
    }
