from pydantic import BaseModel
from typing import Optional

class JournalEntryIn(BaseModel):
    user_id: str
    text: str
    embedding: Optional[list[float]] = None

class ResponseOut(BaseModel):
    reply: str
    emotion: Optional[str] = None
    mood_swing: Optional[bool] = False

# Request schema for analyze_emotion
class EmotionRequest(BaseModel):
    text: str

# Response schema for analyze_emotion
class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    message: str


class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
