"""
Arabic text normalization utilities
Handles diacritics, letter forms, and cleanup
"""

import re

# Tashkeel (diacritical marks) regex - all Arabic diacritics
TASHKEEL = re.compile(r"[\u0610-\u061A\u064B-\u065F\u06D6-\u06ED]")

# Normalize different alif and ya forms
ALIF_FORMS = str.maketrans({
    "أ": "ا",  # Alif with hamza above
    "إ": "ا",  # Alif with hamza below
    "آ": "ا",  # Alif with madda
    "ى": "ي",  # Alif maksura to ya
})


def strip_tashkeel(text: str) -> str:
    """
    Remove all Arabic diacritical marks (harakat)

    Removes: fatha, damma, kasra, sukoon, tanween, shadda, etc.
    """
    return TASHKEEL.sub("", text)


def normalize_letters(text: str) -> str:
    """
    Normalize Arabic letter forms for consistent comparison

    Operations:
    - Unify alif variants (أ إ آ → ا)
    - Convert alif maksura to ya (ى → ي)
    - Remove tatweel (kashida)
    - Normalize whitespace
    """

    # Apply letter normalization
    text = text.translate(ALIF_FORMS)

    # Remove tatweel (decorative elongation)
    text = text.replace("ـ", "")

    # Normalize whitespace (multiple spaces to single)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def remove_non_arabic(text: str) -> str:
    """
    Remove non-Arabic characters (keep only Arabic letters and spaces)
    """
    # Keep Arabic letters (0600-06FF) and whitespace
    pattern = r'[^\u0600-\u06FF\s]'
    return re.sub(pattern, '', text)


def normalize_for_comparison(text: str) -> str:
    """
    Full normalization pipeline for text comparison

    Use this when comparing expected vs. actual recitation
    """
    text = normalize_letters(text)
    text = strip_tashkeel(text)
    text = text.strip()
    return text
