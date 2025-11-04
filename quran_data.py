"""
Minimal Quran validation utilities
Since frontend has complete Quran API, we only need validation logic here
"""

import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Minimal Surah-Ayah counts for server-side validation
# This prevents invalid requests from reaching your API
SURAH_AYAH_COUNTS: Dict[int, int] = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}


def validate_surah_ayah(surah: int, ayah: int) -> Tuple[bool, Optional[str]]:
    """
    Server-side validation for surah/ayah numbers

    Args:
        surah: Surah number (1-114)
        ayah: Ayah number (1-N)

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_surah_ayah(1, 7)
        (True, None)
        >>> validate_surah_ayah(1, 8)
        (False, "Invalid ayah number. Surah 1 has 7 ayahs")
    """
    # Validate surah number
    if not (1 <= surah <= 114):
        return False, "Invalid surah number. Must be between 1-114"

    # Validate ayah number
    max_ayah = SURAH_AYAH_COUNTS.get(surah)
    if max_ayah is None:
        logger.error(f"Surah {surah} not found in lookup table")
        return False, f"Surah data not available for surah {surah}"

    if not (1 <= ayah <= max_ayah):
        return False, f"Invalid ayah number. Surah {surah} has {max_ayah} ayahs (requested: {ayah})"

    return True, None


def get_max_ayah(surah: int) -> Optional[int]:
    """
    Get maximum ayah count for a surah

    Args:
        surah: Surah number (1-114)

    Returns:
        Maximum ayah count or None if invalid
    """
    return SURAH_AYAH_COUNTS.get(surah)


def validate_juz(juz: int) -> Tuple[bool, Optional[str]]:
    """
    Validate Juz number

    Args:
        juz: Juz number (1-30)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (1 <= juz <= 30):
        return False, "Invalid juz number. Must be between 1-30"
    return True, None


def validate_ayah_range(surah: int, start_ayah: int, end_ayah: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a range of ayahs for bulk operations

    Args:
        surah: Surah number
        start_ayah: Starting ayah number
        end_ayah: Ending ayah number

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate surah first
    is_valid, error = validate_surah_ayah(surah, start_ayah)
    if not is_valid:
        return False, error

    is_valid, error = validate_surah_ayah(surah, end_ayah)
    if not is_valid:
        return False, error

    # Validate range order
    if start_ayah > end_ayah:
        return False, f"Invalid range: start_ayah ({start_ayah}) cannot be greater than end_ayah ({end_ayah})"

    return True, None
