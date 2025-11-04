"""
Tests for audio manager functionality
"""

import pytest
from audio_manager import (
    get_audio_url,
    get_reciter_by_id,
    get_all_reciters,
    validate_audio_request
)


class TestAudioURLGeneration:
    """Test audio URL generation"""
    
    def test_get_audio_url_default_reciter(self):
        """Test audio URL generation with default reciter"""
        url = get_audio_url(7, 1, 1)
        assert url.endswith("/1001.mp3")
        assert "ar.shaatree" in url
    
    def test_get_audio_url_different_reciters(self):
        """Test audio URL generation for different reciters"""
        # Abdul Basit
        url1 = get_audio_url(1, 1, 1)
        assert "ar.abdulbasitmurattal" in url1
        
        # Mishary Alafasy
        url2 = get_audio_url(2, 1, 1)
        assert "ar.alafasy" in url2
        
        # Different URLs for different reciters
        assert url1 != url2
    
    def test_get_audio_url_different_verses(self):
        """Test audio URL generation for different verses"""
        url1 = get_audio_url(7, 1, 1)
        url2 = get_audio_url(7, 2, 1)
        url3 = get_audio_url(7, 2, 255)
        
        assert url1.endswith("/1001.mp3")
        assert url2.endswith("/2001.mp3")
        assert url3.endswith("/2255.mp3")
    
    def test_get_audio_url_unknown_reciter(self):
        """Test that unknown reciter defaults to Al-Shatri"""
        url = get_audio_url(999, 1, 1)
        assert "ar.shaatree" in url  # Should default to reciter 7


class TestReciterData:
    """Test reciter data access"""
    
    def test_get_reciter_by_id_valid(self):
        """Test getting reciter by valid ID"""
        reciter = get_reciter_by_id(1)
        assert reciter is not None
        assert reciter["name"] == "Abdul Basit Abdul Samad"
        assert reciter["style"] == "Mujawwad"
    
    def test_get_reciter_by_id_invalid(self):
        """Test getting reciter by invalid ID"""
        assert get_reciter_by_id(999) is None
        assert get_reciter_by_id(0) is None
    
    def test_get_all_reciters(self):
        """Test getting all reciters"""
        reciters = get_all_reciters()
        assert len(reciters) == 5
        assert all("id" in r for r in reciters)
        assert all("name" in r for r in reciters)
        assert all("name_ar" in r for r in reciters)
        assert all("style" in r for r in reciters)
    
    def test_reciter_names(self):
        """Test that reciter names are present"""
        expected_names = [
            "Abdul Basit Abdul Samad",
            "Mishary Rashid Alafasy",
            "Abu Bakr Al-Shatri",
            "Mahmoud Khalil Al-Hussary",
            "Saad Al-Ghamadi"
        ]
        reciters = get_all_reciters()
        reciter_names = [r["name"] for r in reciters]
        
        for name in expected_names:
            assert name in reciter_names


class TestAudioValidation:
    """Test audio request validation"""
    
    def test_validate_valid_request(self):
        """Test validation of valid audio request"""
        is_valid, error = validate_audio_request(1, 1, 7)
        assert is_valid is True
        assert error is None
    
    def test_validate_invalid_surah(self):
        """Test validation with invalid surah"""
        is_valid, error = validate_audio_request(0, 1, 7)
        assert is_valid is False
        assert "Invalid surah" in error
        
        is_valid, error = validate_audio_request(115, 1, 7)
        assert is_valid is False
        assert "Invalid surah" in error
    
    def test_validate_invalid_ayah(self):
        """Test validation with invalid ayah"""
        is_valid, error = validate_audio_request(1, 0, 7)
        assert is_valid is False
        assert "Invalid ayah" in error
        
        is_valid, error = validate_audio_request(1, -1, 7)
        assert is_valid is False
        assert "Invalid ayah" in error
    
    def test_validate_unknown_reciter(self):
        """Test validation with unknown reciter (should be valid)"""
        # Unknown reciter should still validate, will default to Al-Shatri
        is_valid, error = validate_audio_request(1, 1, 999)
        assert is_valid is True
        assert error is None
