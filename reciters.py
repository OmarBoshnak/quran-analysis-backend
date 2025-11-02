"""
Build recitation audio URLs for different reciters
"""

import logging

logger = logging.getLogger(__name__)

# Reciter database (can be expanded)
RECITERS = {
    1: {
        'name': 'Abdul Basit Abdul Samad',
        'name_ar': '[translate:عبد الباسط عبد الصمد]',
        'style': 'Mujawwad',
        'base_url': 'https://cdn.islamic.network/quran/audio/128/ar.abdulbasitmurattal'
    },
    2: {
        'name': 'Mishary Rashid Alafasy',
        'name_ar': '[translate:مشاري بن راشد العفاسي]',
        'style': 'Murattal',
        'base_url': 'https://cdn.islamic.network/quran/audio/128/ar.alafasy'
    },
    7: {
        'name': 'Abu Bakr Al-Shatri',
        'name_ar': '[translate:أبو بكر الشاطري]',
        'style': 'Murattal',
        'base_url': 'https://cdn.islamic.network/quran/audio/128/ar.shaatree'
    },
    3: {
        'name': 'Mahmoud Khalil Al-Hussary',
        'name_ar': '[translate:محمود خليل الحصري]',
        'style': 'Murattal',
        'base_url': 'https://cdn.islamic.network/quran/audio/128/ar.hussary'
    },
    4: {
        'name': 'Saad Al-Ghamadi',
        'name_ar': '[translate:سعد الغامدي]',
        'style': 'Murattal',
        'base_url': 'https://cdn.islamic.network/quran/audio/128/ar.saadalghamadi'
    }
}


def build_reciter_url(surah: int, ayah: int, reciter_id: int = 7) -> str:
    """
    Build MP3 URL for specific Surah/Ayah recitation

    Parameters:
        surah: Surah number (1-114)
        ayah: Ayah number (1-286 depending on surah)
        reciter_id: Reciter identifier (default: 7 = Al-Shatri)

    Returns:
        Direct MP3 URL for the recitation

    Note:
        This uses the islamic.network CDN. You can replace with your own CDN.
        Format: {base_url}/{padded_number}.mp3
        where padded_number = surah*1000 + ayah (e.g., 1001 = Surah 1, Ayah 1)
    """

    if reciter_id not in RECITERS:
        logger.warning(f"Unknown reciter_id {reciter_id}, defaulting to 7")
        reciter_id = 7

    reciter = RECITERS[reciter_id]

    # Format: surah (3 digits) + ayah (3 digits)
    # Example: Surah 2, Ayah 255 → 002255
    # Some CDNs use: surah*1000 + ayah → 2255

    # Islamic.network uses sequential numbering
    # We'll use the padded format
    padded_number = surah * 1000 + ayah

    url = f"{reciter['base_url']}/{padded_number}.mp3"

    logger.info(f"Built URL for Surah {surah}, Ayah {ayah}, Reciter: {reciter['name']}")

    return url


def get_reciter_info(reciter_id: int) -> dict:
    """Get reciter information"""
    return RECITERS.get(reciter_id, RECITERS[7])


def list_available_reciters() -> list:
    """List all available reciters"""
    return [
        {
            'id': rec_id,
            'name': rec['name'],
            'name_ar': rec['name_ar'],
            'style': rec['style']
        }
        for rec_id, rec in RECITERS.items()
    ]
