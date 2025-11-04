"""
User management and JWT authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db, User, get_user_by_username, get_user_by_email, get_user_by_id
from exceptions import AuthenticationException, ResourceNotFoundException

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '604800'))  # 7 days

security = HTTPBearer()


# ============ Request/Response Models ============

class UserRegistration(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class UserProfile(BaseModel):
    """User profile response"""
    id: int
    username: str
    email: str
    created_at: datetime
    last_login: Optional[datetime]
    preferences: dict

    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """User preferences update"""
    font_size: Optional[int] = Field(None, ge=12, le=32)
    auto_scroll: Optional[bool] = None
    language: Optional[str] = Field(None, pattern="^(en|ar)$")
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")
    reciter_id: Optional[int] = None


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


# ============ Password Hashing ============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# ============ JWT Token Functions ============

def create_access_token(user_id: int, username: str) -> str:
    """Create JWT access token"""
    expiration = datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiration,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """Create JWT refresh token"""
    expiration = datetime.utcnow() + timedelta(seconds=JWT_REFRESH_TOKEN_EXPIRES)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expiration,
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationException("Invalid token")


# ============ Authentication Dependency ============

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    Use this in FastAPI endpoints: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise AuthenticationException("Invalid token type")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise AuthenticationException("Invalid token payload")
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise ResourceNotFoundException("User", str(user_id))
    
    return user


# ============ User Management Functions ============

def register_user(db: Session, registration: UserRegistration) -> User:
    """
    Register a new user
    
    Args:
        db: Database session
        registration: User registration data
        
    Returns:
        Created User object
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    existing_user = get_user_by_username(db, registration.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = get_user_by_email(db, registration.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    password_hash = hash_password(registration.password)
    new_user = User(
        username=registration.username,
        email=registration.email,
        password_hash=password_hash,
        preferences={
            "font_size": 16,
            "auto_scroll": True,
            "language": "en",
            "theme": "light",
            "reciter_id": 7
        }
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, login: UserLogin) -> User:
    """
    Authenticate user with username and password
    
    Args:
        db: Database session
        login: User login credentials
        
    Returns:
        Authenticated User object
        
    Raises:
        AuthenticationException: If credentials are invalid
    """
    user = get_user_by_username(db, login.username)
    if not user:
        raise AuthenticationException("Invalid username or password")
    
    if not verify_password(login.password, user.password_hash):
        raise AuthenticationException("Invalid username or password")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


def update_user_preferences(db: Session, user: User, preferences: UserPreferences) -> User:
    """
    Update user preferences
    
    Args:
        db: Database session
        user: User object
        preferences: New preferences
        
    Returns:
        Updated User object
    """
    # Merge new preferences with existing ones
    user_prefs = user.preferences or {}
    
    if preferences.font_size is not None:
        user_prefs["font_size"] = preferences.font_size
    if preferences.auto_scroll is not None:
        user_prefs["auto_scroll"] = preferences.auto_scroll
    if preferences.language is not None:
        user_prefs["language"] = preferences.language
    if preferences.theme is not None:
        user_prefs["theme"] = preferences.theme
    if preferences.reciter_id is not None:
        user_prefs["reciter_id"] = preferences.reciter_id
    
    user.preferences = user_prefs
    db.commit()
    db.refresh(user)
    
    return user
