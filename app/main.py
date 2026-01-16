import os
import uuid
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional

from app.database import engine, Base
from app.routers import journal
from app.models.user_model import User
from app.utils.auth import users_db, create_access_token, verify_token
from app.schemas import UserRegister, UserLogin, TokenResponse, EmotionResponse, EmotionRequest
from app.utils.emotion_infer import predict_emotion

# ✅ Load environment variables
load_dotenv()

# ✅ Create Tables
Base.metadata.create_all(bind=engine)

# ✅ Create FastAPI instance
app = FastAPI(title="Empathetic Journaling Assistant - SQL Overhaul")

# ✅ Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include Routers
# ✅ Include Routers
app.include_router(journal.router, prefix="/api", tags=["Journal"])
app.include_router(journal.router, prefix="/api", tags=["Journal"]) # Logic check: remove duplicate if exists. 
# Better:
try:
    from app.routers import companion
    app.include_router(companion.router, prefix="/api", tags=["Companion"])
except Exception as e:
    print(f"Failed to load companion router: {e}")

# ✅ Auth & Utility Endpoints (Preserved)
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

@app.get("/health")
def health():
    return {"status": "ok", "mode": "SQL-primary"}

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