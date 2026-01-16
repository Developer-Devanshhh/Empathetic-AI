from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models.sql import Entry # We can reuse Entry or create a new Message model if strict about plan. 
# Plan said: "Entry" for journal, but Room messages are ephemeral or stored separately?
# Plan Check: "Room Memory Policy: IF safe: Store USER message only...".
# For MVP, let's store room messages in a simple SQL table or just use Chroma?
# User's request (Step 0) suggested: "POST /rooms/message".
# My Implementation Plan (Step 30) says:
# - POST /rooms: Create session
# - GET /rooms/{room_id}: Fetch history (from SQL)
# - POST /rooms/{room_id}/message: Send message

# I need a Room/Message model in SQL? 
# "AuditLog" is there. "Entry" is for journal.
# Let's add a lightweight "RoomMessage" model or just use JSON in a "Room" model if simple.
# For now, let's stick to the simplest working path: 
# We'll adapt the existing Orchestrator to return responses and maybe store chat in a "Room" model.

from app.utils.auth import verify_token, oauth2_scheme
from app.orchestrator import orchestrator
from app.utils.chroma_client import get_collection
from pydantic import BaseModel

router = APIRouter()

# In-memory storage for MVP rooms (since we didn't add Room model to SQL yet)
# We should ideally modify models/sql.py, but to avoid migrations mid-flight without Alembic, 
# we can use a simple JSON file or in-memory dict for the session state if acceptable.
# User wants "Session continuity".
# Let's add a proper SQL model later, for now we can rely on Client-side history or In-Memory.
# Wait, user explicitly asked for "POST /rooms".
# Let's use a global dict for MVP Rooms to unblock.
rooms_db = {} 

class RoomCreate(BaseModel):
    name: str = "New Session"
    active_agents: List[str] = ["listener", "planner"]

class MessageIn(BaseModel):
    text: str

@router.get("/personas")
def get_personas():
    """Return list of available agent personas."""
    return orchestrator.get_personas()

@router.post("/rooms")
def create_room(room: RoomCreate, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username: raise HTTPException(401, "Invalid Token")
    
    room_id = str(uuid.uuid4())
    rooms_db[room_id] = {
        "id": room_id,
        "user_id": username,
        "agents": room.active_agents,
        "history": [],
        "created_at": datetime.utcnow()
    }
    return {"room_id": room_id, "name": room.name}

@router.get("/rooms/{room_id}")
def get_room(room_id: str, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if room_id not in rooms_db: raise HTTPException(404, "Room not found")
    return rooms_db[room_id]

@router.post("/rooms/{room_id}/message")
async def send_message(room_id: str, msg: MessageIn, token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    if not username: raise HTTPException(401, "Invalid Token")
    
    # Auto-create room if it doesn't exist (for easier UX)
    if room_id not in rooms_db:
        rooms_db[room_id] = {
            "id": room_id,
            "user_id": username,
            "agents": ["listener", "planner", "supporter"],  # Default agents
            "history": [],
            "created_at": datetime.utcnow()
        }
    
    room = rooms_db[room_id]
    
    # 1. Add User Message to History
    user_msg = {"role": "user", "content": msg.text, "timestamp": datetime.utcnow().isoformat()}
    room["history"].append(user_msg)
    
    # 2. Call Orchestrator
    collection = get_collection("journals")
    
    # Orchestrator expects: process_message(text, active_agents, user_id, collection)
    result = await orchestrator.process_message(msg.text, room["agents"], username, collection)
    
    # 3. Check safety first
    if not result.get("is_safe", True):
        return {
            "is_safe": False,
            "crisis_message": result.get("crisis_message", "Safety check failed"),
            "responses": []
        }
    
    # 4. Add Agent Replies to History
    agents_response = result.get("responses", [])
    for reply in agents_response:
        agent_msg = {
            "role": "agent", 
            "agent_id": reply.get("agent_id"), 
            "name": reply.get("name"),
            "content": reply.get("response", ""),
            "color": reply.get("color", "gray"),
            "timestamp": datetime.utcnow().isoformat()
        }
        room["history"].append(agent_msg)
        
    return {
        "is_safe": True,
        "responses": agents_response
    }
