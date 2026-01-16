import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# --- STEP 1: Resolve absolute path ---
# Start from project root and normalize
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.path.join(ROOT_DIR, "models", "emotion_model")

# Prefer .env variable if it exists, otherwise use default
MODEL_DIR = os.getenv("EMOTION_MODEL_PATH", DEFAULT_MODEL_DIR)
MODEL_DIR = os.path.abspath(MODEL_DIR)  # normalize to full absolute path

print(f"[INFO] Loading emotion model from: {MODEL_DIR}")

# --- STEP 2: Validate folder existence ---
try:
    if not os.path.isdir(MODEL_DIR):
        raise FileNotFoundError(f"Model dir not found: {MODEL_DIR}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    USE_MOCK = False
except Exception as e:
    print(f"[WARNING] Emotion model not found or failed to load: {e}")
    print("[INFO] Using MOCK emotion prediction for development/verification.")
    USE_MOCK = True
    tokenizer = None
    model = None

# --- STEP 4: Inference function ---
def predict_emotion(text: str):
    if USE_MOCK:
        # Simple heuristic for verification
        text_lower = text.lower()
        if "furious" in text_lower or "angry" in text_lower:
            return {"label": "anger", "score": 0.95}
        if "happy" in text_lower or "joy" in text_lower:
            return {"label": "joy", "score": 0.95}
        if "sad" in text_lower:
            return {"label": "sadness", "score": 0.95}
        return {"label": "neutral", "score": 0.5}

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    label_idx = int(np.argmax(probs))
    label_map = getattr(model.config, "id2label", {i: f"LABEL_{i}" for i in range(len(probs))})
    raw_label = label_map.get(label_idx, str(label_idx))
    score = float(np.max(probs))

    # 🧠 Human-readable mapping for your dataset
    label_map_clean = {
        "LABEL_0": "admiration",
        "LABEL_1": "amusement",
        "LABEL_2": "anger",
        "LABEL_3": "annoyance",
        "LABEL_4": "approval",
        "LABEL_5": "caring",
        "LABEL_6": "confusion",
        "LABEL_7": "curiosity",
        "LABEL_8": "desire",
        "LABEL_9": "disappointment",
        "LABEL_10": "disapproval",
        "LABEL_11": "disgust",
        "LABEL_12": "embarrassment",
        "LABEL_13": "excitement",
        "LABEL_14": "fear",
        "LABEL_15": "gratitude",
        "LABEL_16": "grief",
        "LABEL_17": "joy",
        "LABEL_18": "love",
        "LABEL_19": "nervousness",
        "LABEL_20": "optimism",
        "LABEL_21": "pride",
        "LABEL_22": "realization",
        "LABEL_23": "relief",
        "LABEL_24": "remorse",
        "LABEL_25": "sadness",
        "LABEL_26": "surprise",
        "LABEL_27": "neutral",
    }

    # Convert label if it matches our mapping
    label = label_map_clean.get(raw_label, raw_label)

    return {"label": label, "score": score}
