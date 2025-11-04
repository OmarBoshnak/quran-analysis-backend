"""
Audio management for Quran recitations
Handles CDN integration and URL generation
"""

import logging
from typing import Optional, Dict
from config import settings

logger = logging.getLogger(__name__)

# Reciter database - extended from reciters.py
AUDIO_RECITERS = {
    1: {
        'id': 1,
        'name': 'Abdul Basit Abdul Samad',
        'name_ar': 'عبد الباسط عبد الصمد',
        'style': 'Mujawwad',
        'base_url': f'{settings.AUDIO_CDN_BASE_URL}/128/ar.abdulbasitmurattal',
        'quality': 'high'
    },
    2: {
        'id': 2,
        'name': 'Mishary Rashid Alafasy',
        'name_ar': 'مشاري بن راشد العفاسي',
        'style': 'Murattal',
        'base_url': f'{settings.AUDIO_CDN_BASE_URL}/128/ar.alafasy',
        'quality': 'high'
    },
    3: {
        'id': 3,
        'name': 'Mahmoud Khalil Al-Hussary',
        'name_ar': 'محمود خليل الحصري',
        'style': 'Murattal',
        'base_url': f'{settings.AUDIO_CDN_BASE_URL}/128/ar.hussary',
        'quality': 'high'
    },
    4: {
        'id': 4,
        'name': 'Saad Al-Ghamadi',
        'name_ar': 'سعد الغامدي',
        'style': 'Murattal',
        'base_url': f'{settings.AUDIO_CDN_BASE_URL}/128/ar.saadalghamadi',
        'quality': 'high'
    },
    7: {
        'id': 7,
        'name': 'Abu Bakr Al-Shatri',
        'name_ar': 'أبو بكر الشاطري',
        'style': 'Murattal',
        'base_url': f'{settings.AUDIO_CDN_BASE_URL}/128/ar.shaatree',
        'quality': 'high'
    }
}


def get_audio_url(reciter_id: int, surah: int, ayah: int) -> str:
    """
    Generate audio URL for specific recitation
    
    Args:
        reciter_id: Reciter identifier
        surah: Surah number (1-114)
        ayah: Ayah number
        
    Returns:
        Direct MP3 URL for the recitation
    """
    # Default to Abu Bakr Al-Shatri if reciter not found
    if reciter_id not in AUDIO_RECITERS:
        logger.warning(f"Unknown reciter_id {reciter_id}, defaulting to 7 (Al-Shatri)")
        reciter_id = 7
    
    reciter = AUDIO_RECITERS[reciter_id]
    
    # Format: surah * 1000 + ayah
    # Example: Surah 2, Ayah 255 → 2255
    padded_number = surah * 1000 + ayah
    
    url = f"{reciter['base_url']}/{padded_number}.mp3"
    
    logger.info(f"Generated audio URL for Surah {surah}, Ayah {ayah}, Reciter: {reciter['name']}")
    
    return url


def get_reciter_by_id(reciter_id: int) -> Optional[Dict]:
    """
    Get reciter information by ID
    
    Args:
        reciter_id: Reciter identifier
        
    Returns:
        Reciter information dictionary or None
    """
    return AUDIO_RECITERS.get(reciter_id)


def get_all_reciters() -> list:
    """
    Get list of all available reciters
    
    Returns:
        List of reciter information dictionaries
    """
    return [
        {
            'id': rec['id'],
            'name': rec['name'],
            'name_ar': rec['name_ar'],
            'style': rec['style'],
            'quality': rec['quality']
        }
        for rec in AUDIO_RECITERS.values()
    ]


def validate_audio_request(surah: int, ayah: int, reciter_id: int) -> tuple:
    """
    Validate audio request parameters
    
    Args:
        surah: Surah number
        ayah: Ayah number
        reciter_id: Reciter identifier
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate surah
    if not (1 <= surah <= 114):
        return False, f"Invalid surah number: {surah}. Must be between 1-114"
    
    # Validate ayah (basic check, detailed validation in quran_data)
    if ayah < 1:
        return False, f"Invalid ayah number: {ayah}. Must be at least 1"
    
    # Validate reciter (optional check - will use default if not found)
    if reciter_id not in AUDIO_RECITERS:
        logger.warning(f"Reciter {reciter_id} not found, will use default")
    
    return True, None
