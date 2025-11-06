import os
import uuid
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

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
from app.utils.chroma_client import get_collection, add_entry, query_similar
from app.utils.gemini_client import generate_empathetic_reply
from app.utils.auth import users_db, create_access_token, verify_token
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

        # 🧠 2️⃣ Detect emotion using your HuggingFace model
        emo = predict_emotion(entry.text)
        label = emo["label"] if isinstance(emo, dict) else emo[0]

        # 📚 3️⃣ Retrieve similar past reflections for context
        collection = get_collection("journals")
        similar_docs = query_similar(collection, entry.text)
        context_text = "\n".join(similar_docs) if similar_docs else "No prior entries yet."

        # 💬 4️⃣ Generate empathetic reflection via Gemini
        reply = generate_empathetic_reply(label, context_text, entry.text)

        # 💾 5️⃣ Store both user entry and reflection in Chroma
        doc_id = f"{username}-{uuid.uuid4()}"
        metadata = {"user_id": username, "emotion": label}
        combined_text = f"User: {entry.text}\nAI Reflection: {reply}"
        add_entry(collection, doc_id, combined_text, metadata)

        # 🩵 6️⃣ Placeholder for mood tracking
        mood_swing = False

        # ✅ 7️⃣ Return response to frontend
        return ResponseOut(reply=reply, emotion=label, mood_swing=mood_swing)

    except Exception as e:
        print("[ERROR] /journal:", e)
        raise HTTPException(status_code=500, detail=str(e))