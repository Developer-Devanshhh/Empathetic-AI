import os
import uuid
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from typing import List, Optional

# ✅ Load environment variables first
load_dotenv()

# ✅ Create FastAPI instance before routes
app = FastAPI(title="Empathetic Journaling Assistant - MVP")

# ✅ Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Then import project modules (which rely on env vars)
from app.schemas import EmotionResponse, EmotionRequest, JournalEntryIn, ResponseOut
from app.utils.emotion_infer import predict_emotion
from app.utils.chroma_client import get_collection, add_entry, query_similar, get_recent_entries
from app.utils.gemini_client import generate_empathetic_reply
from app.utils.auth import users_db, create_access_token, verify_token
from app.utils.embeddings import get_embedding
from app.utils.mood_analysis import calculate_volatility
from app.utils.safety import check_safety
from app.utils.distortions import analyzer
from app.models.user_model import User
from app.schemas import UserRegister, UserLogin, TokenResponse

# Initialize OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ✅ Initialize collection (optional)
collection = get_collection("journals")

@app.post("/register")
def register_user(user: UserRegister):
    if user.username in users_db:
        return {"error": "User already exists"}
    users_db[user.username] = User(user.username, user.password)
    return {"message": "User registered successfully"}

@app.post("/login", response_model=TokenResponse)
def login_user(user: UserLogin):
    stored_user = users_db.get(user.username)
    if not stored_user or not stored_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=access_token)

# 🩵 Health Check
@app.get("/health")
def health():
    return {"status": "ok"}

# 🧠 Simple Emotion Analysis Endpoint
@app.post("/analyze_emotion", response_model=EmotionResponse)
async def analyze_emotion(payload: EmotionRequest):
    text = payload.text.strip()
    if not text:
        return {"emotion": "neutral", "confidence": 0.0, "message": "No text provided."}

    try:
        result = predict_emotion(text)
        emotion = result.get("label", "neutral")
        confidence = result.get("score", 0.0)
        return {
            "emotion": emotion,
            "confidence": confidence,
            "message": f"I sense some {emotion} in your writing."
        }
    except Exception as e:
        print("Error in /analyze_emotion:", e)
        return {"emotion": "error", "confidence": 0.0, "message": str(e)}

@app.post("/journal", response_model=ResponseOut)
async def add_journal(entry: JournalEntryIn, token: str = Depends(oauth2_scheme)):
    """
    Accepts a journal entry from an authenticated user,
    detects emotion, generates Gemini reflection,
    and stores both in Chroma with user-specific metadata.
    """
    try:
        # 🔐 1️⃣ Verify JWT and extract username
        username = verify_token(token)
        if not username:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # 🚨 1.5️⃣ Safety Check
        safety_status = check_safety(entry.text)
        if not safety_status["is_safe"]:
            # Handle unsafe entry:
            # 1. Skip standard analysis
            # 2. Store securely with flag (using dummy embedding to avoid meaningful vector space)
            # 3. Return crisis resource immediately
            
            doc_id = f"{username}-{uuid.uuid4()}"
            metadata = {
                "user_id": username, 
                "safety_flag": True, 
                "category": safety_status["category"],
                "emotion": "crisis" # Placeholder
            }
            
            # Zero vector for "no embedding" (MiniLM-L6-v2 is 384 dims)
            dummy_embedding = [0.0] * 384 
            
            add_entry(collection, doc_id, f"UNSAFE_ENTRY: {entry.text}", metadata, embedding=dummy_embedding)
            
            return ResponseOut(
                reply=safety_status["response_message"], 
                emotion="crisis", 
                mood_swing=False
            )

        # 🧠 2️⃣ Detect emotion using your HuggingFace model
        emo = predict_emotion(entry.text)
        label = emo.get("label", emo[0]) if isinstance(emo, dict) else emo[0]
        score = emo.get("score", 0.0) if isinstance(emo, dict) else 0.0

        # 📉 2.5️⃣ Calculate Embedding & Mood Volatility
        # Use client-provided embedding if valid, else generate on server
        if entry.embedding and len(entry.embedding) == 384:
            current_embedding = entry.embedding
        else:
            current_embedding = get_embedding(entry.text)

        # Retrieve recent entries for comparison
        # (We use a larger limit to have enough history, e.g. 5)
        recent_entries = get_recent_entries(collection, username, limit=5)
        
        mood_analysis = calculate_volatility(current_embedding, recent_entries, label)
        mood_swing = mood_analysis["mood_swing"]
        # Can also use mood_analysis["volatility_score"] if we want to log it or return it

        # 📚 3️⃣ Retrieve similar past reflections for context
        collection = get_collection("journals")
        similar_docs = query_similar(collection, entry.text)
        context_text = "\n".join(similar_docs) if similar_docs else "No prior entries yet."

        # 🧠 3.5️⃣ Check for Cognitive Distortions
        distortions = analyzer.analyze(entry.text, float(score))

        # 💬 4️⃣ Generate empathetic reflection via Gemini
        reply = generate_empathetic_reply(label, context_text, entry.text, distortions=distortions)

        # 💾 5️⃣ Store both user entry and reflection in Chroma
        doc_id = f"{username}-{uuid.uuid4()}"
        metadata = {"user_id": username, "emotion": label, "emotion_score": float(score)}
        combined_text = f"User: {entry.text}\nAI Reflection: {reply}"
        
        # Pass the pre-computed embedding to save time
        add_entry(collection, doc_id, combined_text, metadata, embedding=current_embedding)

        # ✅ 7️⃣ Return response to frontend
        return ResponseOut(reply=reply, emotion=label, mood_swing=mood_swing)

    except Exception as e:
        print("[ERROR] /journal:", e)
        raise HTTPException(status_code=500, detail=str(e))

# 🗑️ Privacy & Memory Management
from app.utils.chroma_client import delete_entry, delete_user_entries, get_all_entries_for_dashboard

@app.get("/memories")
def get_memories(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    entries = get_all_entries_for_dashboard(collection, username)
    return entries

@app.delete("/memories/{doc_id}")
def delete_memory(doc_id: str, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    # Technically we should verify the doc belongs to user, but Chroma delete where ID=X AND User=Y isn't direct in 'delete(ids=[])' 
    # But since IDs are UUIDs prefixed with username (logic in add_journal), we can check prefix or just rely on UUID uniqueness.
    # Safe check:
    if not doc_id.startswith(username):
         raise HTTPException(status_code=403, detail="Permission denied")
         
    delete_entry(collection, doc_id)
    return {"message": "Memory deleted"}

@app.delete("/memories")
def clear_history(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    delete_user_entries(collection, username)
    return {"message": "All memories cleared"}

# 🎭 Phase 2: Multi-Agent Room
from app.orchestrator import orchestrator

class RoomMessageIn(BaseModel):
    text: str
    active_agents: list[str]

@app.get("/personas")
def get_personas():
    """Return available agent personas."""
    return orchestrator.get_personas()

@app.post("/rooms/message")
async def room_message(msg: RoomMessageIn, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 1. Orchestrated Execution (Safety & Retrieval inside)
    result = await orchestrator.process_message(msg.text, msg.active_agents, username, collection)
    
    # 2. Room Memory Policy:
    # IF safe: Store USER message only. 
    # Do NOT store agent replies.
    if result.get("is_safe"):
        doc_id = f"{username}-{uuid.uuid4()}"
        # Minimal metadata for context
        metadata = {"user_id": username, "type": "room_chat"}
        
        # We need to detect emotion for better retrieval later?
        # For now, simplistic storage. Maybe reuse existing logic?
        # Let's detect emotion quickly just for metadata if possible, 
        # but to save latency we might skip or do async.
        # Plan says: "Only user messages are eligible...".
        # Let's simple-store for now.
        add_entry(collection, doc_id, msg.text, metadata)
        
    return result