"""
Database models and configuration using SQLAlchemy
"""

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./quran.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()


# ============ Models ============

class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    preferences = Column(JSON, default=dict)
    
    # Relationships
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Progress(Base):
    """User progress tracking for Quran reading and memorization"""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    surah_id = Column(Integer, nullable=False, index=True)
    completed_verses = Column(JSON, default=list)  # List of completed verse numbers
    memorized_verses = Column(JSON, default=list)  # List of memorized verse numbers
    last_read_verse = Column(Integer, nullable=True)
    last_read_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, surah_id={self.surah_id})>"


class Bookmark(Base):
    """User bookmarks for specific verses"""
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    surah_id = Column(Integer, nullable=False)
    verse_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    note = Column(Text, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="bookmarks")

    def __repr__(self):
        return f"<Bookmark(user_id={self.user_id}, surah={self.surah_id}, verse={self.verse_index})>"


# ============ Database Functions ============

def get_db() -> Session:
    """
    Dependency function to get database session
    Usage in FastAPI: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_progress(db: Session, user_id: int, surah_id: Optional[int] = None):
    """Get user progress, optionally filtered by surah"""
    query = db.query(Progress).filter(Progress.user_id == user_id)
    if surah_id is not None:
        query = query.filter(Progress.surah_id == surah_id)
    return query.all()


def get_user_bookmarks(db: Session, user_id: int):
    """Get all bookmarks for a user"""
    return db.query(Bookmark).filter(Bookmark.user_id == user_id).order_by(Bookmark.created_at.desc()).all()
