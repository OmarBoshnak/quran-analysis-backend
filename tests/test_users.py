"""
Tests for user authentication and management
"""

import pytest
from users import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    UserRegistration,
    UserLogin,
    UserPreferences
)
from exceptions import AuthenticationException


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_hash_password_different_outputs(self):
        """Test that same password produces different hashes (due to salt)"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes due to different salts
        assert hash1 != hash2
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "MyPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "MyPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestJWTTokens:
    """Test JWT token creation and validation"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        token = create_access_token(1, "testuser")
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        token = create_refresh_token(1, "testuser")
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_decode_access_token(self):
        """Test decoding access token"""
        user_id = 42
        username = "testuser"
        token = create_access_token(user_id, username)
        
        payload = decode_token(token)
        assert payload["user_id"] == user_id
        assert payload["username"] == username
        assert payload["type"] == "access"
    
    def test_decode_refresh_token(self):
        """Test decoding refresh token"""
        user_id = 42
        username = "testuser"
        token = create_refresh_token(user_id, username)
        
        payload = decode_token(token)
        assert payload["user_id"] == user_id
        assert payload["username"] == username
        assert payload["type"] == "refresh"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        with pytest.raises(AuthenticationException):
            decode_token("invalid.token.here")
    
    def test_token_contains_expiration(self):
        """Test that tokens contain expiration"""
        token = create_access_token(1, "testuser")
        payload = decode_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)


class TestUserModels:
    """Test user-related Pydantic models"""
    
    def test_user_registration_valid(self):
        """Test valid user registration model"""
        data = {
            "username": "newuser123",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        user_reg = UserRegistration(**data)
        
        assert user_reg.username == "newuser123"
        assert user_reg.email == "test@example.com"
        assert user_reg.password == "SecurePass123!"
    
    def test_user_registration_invalid_username(self):
        """Test user registration with invalid username"""
        data = {
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        with pytest.raises(ValueError):
            UserRegistration(**data)
    
    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email"""
        data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "SecurePass123!"
        }
        
        with pytest.raises(ValueError):
            UserRegistration(**data)
    
    def test_user_registration_short_password(self):
        """Test user registration with short password"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # Too short
        }
        
        with pytest.raises(ValueError):
            UserRegistration(**data)
    
    def test_user_login_model(self):
        """Test user login model"""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        login = UserLogin(**data)
        
        assert login.username == "testuser"
        assert login.password == "password123"
    
    def test_user_preferences_partial(self):
        """Test user preferences with partial data"""
        # All fields are optional
        prefs = UserPreferences(font_size=18)
        assert prefs.font_size == 18
        assert prefs.auto_scroll is None
        
        prefs2 = UserPreferences(theme="dark", language="ar")
        assert prefs2.theme == "dark"
        assert prefs2.language == "ar"
        assert prefs2.font_size is None
    
    def test_user_preferences_validation(self):
        """Test user preferences validation"""
        # Invalid font size
        with pytest.raises(ValueError):
            UserPreferences(font_size=5)  # Too small
        
        with pytest.raises(ValueError):
            UserPreferences(font_size=50)  # Too large
        
        # Invalid language
        with pytest.raises(ValueError):
            UserPreferences(language="fr")  # Not en or ar
        
        # Invalid theme
        with pytest.raises(ValueError):
            UserPreferences(theme="blue")  # Not light or dark
