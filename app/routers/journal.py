from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json
from datetime import datetime

from app.database import get_db
from app.models.sql import Book, Chapter, Entry
from app.utils.auth import verify_token, oauth2_scheme
from app.utils.security import encrypt_text, decrypt_text
from app.utils.audit import log_action
from app.utils.chroma_client import get_collection, add_entry

# schemas (move to schemas.py later or define here for speed then refactor)
from pydantic import BaseModel

router = APIRouter()

class BookCreate(BaseModel):
    title: str
    description: str = None

class ChapterCreate(BaseModel):
    title: str
    start_date: datetime
    end_date: datetime = None

class EntryCreate(BaseModel):
    text: str
    date: datetime = None
    emotion_labels: dict = None # {"label": "happy", "score": 0.9}
    client_only: bool = False

class BookResponse(BaseModel):
    book_id: str
    title: str
    description: Optional[str] = None
    chapters: List['ChapterResponse'] = [] # Forward Ref

class ChapterResponse(BaseModel):
    chapter_id: str
    book_id: str
    title: str
    start_date: datetime
    end_date: Optional[datetime] = None

class EntryResponse(BaseModel):
    entry_id: str
    text: str
    date: datetime
    client_only: bool

# Resolve Forward Ref
BookResponse.update_forward_refs()

@router.get("/books", response_model=List[BookResponse])
def get_books(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username: raise HTTPException(401, "Invalid Token")
    
    books = db.query(Book).filter(Book.user_id == username).all()
    return books

@router.post("/books", response_model=BookResponse)
def create_book(book: BookCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    if not username: raise HTTPException(401, "Invalid Token")
    
    new_book = Book(
        book_id=f"k_{uuid.uuid4().hex[:8]}", # k_ prefix for keys
        user_id=username,
        title=book.title,
        description=book.description
    )
    db.add(new_book)
    db.commit()
    log_action(db, username, "CREATE_BOOK", new_book.book_id)
    return new_book

@router.post("/books/{book_id}/chapters", response_model=ChapterResponse)
def create_chapter(book_id: str, chapter: ChapterCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    
    # Verify ownership
    book = db.query(Book).filter(Book.book_id == book_id, Book.user_id == username).first()
    if not book: raise HTTPException(404, "Book not found")
    
    new_chapter = Chapter(
        chapter_id=f"c_{uuid.uuid4().hex[:8]}",
        book_id=book_id,
        title=chapter.title,
        start_date=chapter.start_date,
        end_date=chapter.end_date
    )
    db.add(new_chapter)
    db.commit()
    return new_chapter


    db.add(new_entry)
    db.commit()
    
    log_action(db, username, "CREATE_ENTRY", entry_id)
    return {"status": "created", "entry_id": entry_id}

@router.get("/chapters/{chapter_id}/entries", response_model=List[EntryResponse])
def get_entries(chapter_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token)
    
    # minimal ownership check (refined later)
    entries = db.query(Entry).filter(Entry.chapter_id == chapter_id).order_by(Entry.date.desc()).all()
    
    results = []
    for e in entries:
        # Decrypt on the fly
        text = decrypt_text(e.text_encrypted)
        results.append({
            "entry_id": e.entry_id,
            "text": text,
            "date": e.date,
            "client_only": e.client_only
        })
        
    return results
