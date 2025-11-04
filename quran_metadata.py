"""
Complete Quran metadata including surah information, juz data, translations, and tafsir
"""

from typing import List, Dict, Optional

# Complete Surah metadata
SURAH_METADATA = [
    {"id": 1, "name": "Al-Fatihah", "arabic_name": "الفاتحة", "ayah_count": 7, "juz": 1, "revelation_place": "Makkah"},
    {"id": 2, "name": "Al-Baqarah", "arabic_name": "البقرة", "ayah_count": 286, "juz": 1, "revelation_place": "Madinah"},
    {"id": 3, "name": "Aal-E-Imran", "arabic_name": "آل عمران", "ayah_count": 200, "juz": 3, "revelation_place": "Madinah"},
    {"id": 4, "name": "An-Nisa", "arabic_name": "النساء", "ayah_count": 176, "juz": 4, "revelation_place": "Madinah"},
    {"id": 5, "name": "Al-Ma'idah", "arabic_name": "المائدة", "ayah_count": 120, "juz": 6, "revelation_place": "Madinah"},
    {"id": 6, "name": "Al-An'am", "arabic_name": "الأنعام", "ayah_count": 165, "juz": 7, "revelation_place": "Makkah"},
    {"id": 7, "name": "Al-A'raf", "arabic_name": "الأعراف", "ayah_count": 206, "juz": 8, "revelation_place": "Makkah"},
    {"id": 8, "name": "Al-Anfal", "arabic_name": "الأنفال", "ayah_count": 75, "juz": 9, "revelation_place": "Madinah"},
    {"id": 9, "name": "At-Tawbah", "arabic_name": "التوبة", "ayah_count": 129, "juz": 10, "revelation_place": "Madinah"},
    {"id": 10, "name": "Yunus", "arabic_name": "يونس", "ayah_count": 109, "juz": 11, "revelation_place": "Makkah"},
    {"id": 11, "name": "Hud", "arabic_name": "هود", "ayah_count": 123, "juz": 11, "revelation_place": "Makkah"},
    {"id": 12, "name": "Yusuf", "arabic_name": "يوسف", "ayah_count": 111, "juz": 12, "revelation_place": "Makkah"},
    {"id": 13, "name": "Ar-Ra'd", "arabic_name": "الرعد", "ayah_count": 43, "juz": 13, "revelation_place": "Madinah"},
    {"id": 14, "name": "Ibrahim", "arabic_name": "ابراهيم", "ayah_count": 52, "juz": 13, "revelation_place": "Makkah"},
    {"id": 15, "name": "Al-Hijr", "arabic_name": "الحجر", "ayah_count": 99, "juz": 14, "revelation_place": "Makkah"},
    {"id": 16, "name": "An-Nahl", "arabic_name": "النحل", "ayah_count": 128, "juz": 14, "revelation_place": "Makkah"},
    {"id": 17, "name": "Al-Isra", "arabic_name": "الإسراء", "ayah_count": 111, "juz": 15, "revelation_place": "Makkah"},
    {"id": 18, "name": "Al-Kahf", "arabic_name": "الكهف", "ayah_count": 110, "juz": 15, "revelation_place": "Makkah"},
    {"id": 19, "name": "Maryam", "arabic_name": "مريم", "ayah_count": 98, "juz": 16, "revelation_place": "Makkah"},
    {"id": 20, "name": "Ta-Ha", "arabic_name": "طه", "ayah_count": 135, "juz": 16, "revelation_place": "Makkah"},
    {"id": 21, "name": "Al-Anbiya", "arabic_name": "الأنبياء", "ayah_count": 112, "juz": 17, "revelation_place": "Makkah"},
    {"id": 22, "name": "Al-Hajj", "arabic_name": "الحج", "ayah_count": 78, "juz": 17, "revelation_place": "Madinah"},
    {"id": 23, "name": "Al-Mu'minun", "arabic_name": "المؤمنون", "ayah_count": 118, "juz": 18, "revelation_place": "Makkah"},
    {"id": 24, "name": "An-Nur", "arabic_name": "النور", "ayah_count": 64, "juz": 18, "revelation_place": "Madinah"},
    {"id": 25, "name": "Al-Furqan", "arabic_name": "الفرقان", "ayah_count": 77, "juz": 18, "revelation_place": "Makkah"},
    {"id": 26, "name": "Ash-Shu'ara", "arabic_name": "الشعراء", "ayah_count": 227, "juz": 19, "revelation_place": "Makkah"},
    {"id": 27, "name": "An-Naml", "arabic_name": "النمل", "ayah_count": 93, "juz": 19, "revelation_place": "Makkah"},
    {"id": 28, "name": "Al-Qasas", "arabic_name": "القصص", "ayah_count": 88, "juz": 20, "revelation_place": "Makkah"},
    {"id": 29, "name": "Al-Ankabut", "arabic_name": "العنكبوت", "ayah_count": 69, "juz": 20, "revelation_place": "Makkah"},
    {"id": 30, "name": "Ar-Rum", "arabic_name": "الروم", "ayah_count": 60, "juz": 21, "revelation_place": "Makkah"},
    {"id": 31, "name": "Luqman", "arabic_name": "لقمان", "ayah_count": 34, "juz": 21, "revelation_place": "Makkah"},
    {"id": 32, "name": "As-Sajdah", "arabic_name": "السجدة", "ayah_count": 30, "juz": 21, "revelation_place": "Makkah"},
    {"id": 33, "name": "Al-Ahzab", "arabic_name": "الأحزاب", "ayah_count": 73, "juz": 21, "revelation_place": "Madinah"},
    {"id": 34, "name": "Saba", "arabic_name": "سبإ", "ayah_count": 54, "juz": 22, "revelation_place": "Makkah"},
    {"id": 35, "name": "Fatir", "arabic_name": "فاطر", "ayah_count": 45, "juz": 22, "revelation_place": "Makkah"},
    {"id": 36, "name": "Ya-Sin", "arabic_name": "يس", "ayah_count": 83, "juz": 22, "revelation_place": "Makkah"},
    {"id": 37, "name": "As-Saffat", "arabic_name": "الصافات", "ayah_count": 182, "juz": 23, "revelation_place": "Makkah"},
    {"id": 38, "name": "Sad", "arabic_name": "ص", "ayah_count": 88, "juz": 23, "revelation_place": "Makkah"},
    {"id": 39, "name": "Az-Zumar", "arabic_name": "الزمر", "ayah_count": 75, "juz": 23, "revelation_place": "Makkah"},
    {"id": 40, "name": "Ghafir", "arabic_name": "غافر", "ayah_count": 85, "juz": 24, "revelation_place": "Makkah"},
    {"id": 41, "name": "Fussilat", "arabic_name": "فصلت", "ayah_count": 54, "juz": 24, "revelation_place": "Makkah"},
    {"id": 42, "name": "Ash-Shura", "arabic_name": "الشورى", "ayah_count": 53, "juz": 25, "revelation_place": "Makkah"},
    {"id": 43, "name": "Az-Zukhruf", "arabic_name": "الزخرف", "ayah_count": 89, "juz": 25, "revelation_place": "Makkah"},
    {"id": 44, "name": "Ad-Dukhan", "arabic_name": "الدخان", "ayah_count": 59, "juz": 25, "revelation_place": "Makkah"},
    {"id": 45, "name": "Al-Jathiyah", "arabic_name": "الجاثية", "ayah_count": 37, "juz": 25, "revelation_place": "Makkah"},
    {"id": 46, "name": "Al-Ahqaf", "arabic_name": "الأحقاف", "ayah_count": 35, "juz": 26, "revelation_place": "Makkah"},
    {"id": 47, "name": "Muhammad", "arabic_name": "محمد", "ayah_count": 38, "juz": 26, "revelation_place": "Madinah"},
    {"id": 48, "name": "Al-Fath", "arabic_name": "الفتح", "ayah_count": 29, "juz": 26, "revelation_place": "Madinah"},
    {"id": 49, "name": "Al-Hujurat", "arabic_name": "الحجرات", "ayah_count": 18, "juz": 26, "revelation_place": "Madinah"},
    {"id": 50, "name": "Qaf", "arabic_name": "ق", "ayah_count": 45, "juz": 26, "revelation_place": "Makkah"},
    {"id": 51, "name": "Adh-Dhariyat", "arabic_name": "الذاريات", "ayah_count": 60, "juz": 26, "revelation_place": "Makkah"},
    {"id": 52, "name": "At-Tur", "arabic_name": "الطور", "ayah_count": 49, "juz": 27, "revelation_place": "Makkah"},
    {"id": 53, "name": "An-Najm", "arabic_name": "النجم", "ayah_count": 62, "juz": 27, "revelation_place": "Makkah"},
    {"id": 54, "name": "Al-Qamar", "arabic_name": "القمر", "ayah_count": 55, "juz": 27, "revelation_place": "Makkah"},
    {"id": 55, "name": "Ar-Rahman", "arabic_name": "الرحمن", "ayah_count": 78, "juz": 27, "revelation_place": "Madinah"},
    {"id": 56, "name": "Al-Waqi'ah", "arabic_name": "الواقعة", "ayah_count": 96, "juz": 27, "revelation_place": "Makkah"},
    {"id": 57, "name": "Al-Hadid", "arabic_name": "الحديد", "ayah_count": 29, "juz": 27, "revelation_place": "Madinah"},
    {"id": 58, "name": "Al-Mujadila", "arabic_name": "المجادلة", "ayah_count": 22, "juz": 28, "revelation_place": "Madinah"},
    {"id": 59, "name": "Al-Hashr", "arabic_name": "الحشر", "ayah_count": 24, "juz": 28, "revelation_place": "Madinah"},
    {"id": 60, "name": "Al-Mumtahanah", "arabic_name": "الممتحنة", "ayah_count": 13, "juz": 28, "revelation_place": "Madinah"},
    {"id": 61, "name": "As-Saff", "arabic_name": "الصف", "ayah_count": 14, "juz": 28, "revelation_place": "Madinah"},
    {"id": 62, "name": "Al-Jumu'ah", "arabic_name": "الجمعة", "ayah_count": 11, "juz": 28, "revelation_place": "Madinah"},
    {"id": 63, "name": "Al-Munafiqun", "arabic_name": "المنافقون", "ayah_count": 11, "juz": 28, "revelation_place": "Madinah"},
    {"id": 64, "name": "At-Taghabun", "arabic_name": "التغابن", "ayah_count": 18, "juz": 28, "revelation_place": "Madinah"},
    {"id": 65, "name": "At-Talaq", "arabic_name": "الطلاق", "ayah_count": 12, "juz": 28, "revelation_place": "Madinah"},
    {"id": 66, "name": "At-Tahrim", "arabic_name": "التحريم", "ayah_count": 12, "juz": 28, "revelation_place": "Madinah"},
    {"id": 67, "name": "Al-Mulk", "arabic_name": "الملك", "ayah_count": 30, "juz": 29, "revelation_place": "Makkah"},
    {"id": 68, "name": "Al-Qalam", "arabic_name": "القلم", "ayah_count": 52, "juz": 29, "revelation_place": "Makkah"},
    {"id": 69, "name": "Al-Haqqah", "arabic_name": "الحاقة", "ayah_count": 52, "juz": 29, "revelation_place": "Makkah"},
    {"id": 70, "name": "Al-Ma'arij", "arabic_name": "المعارج", "ayah_count": 44, "juz": 29, "revelation_place": "Makkah"},
    {"id": 71, "name": "Nuh", "arabic_name": "نوح", "ayah_count": 28, "juz": 29, "revelation_place": "Makkah"},
    {"id": 72, "name": "Al-Jinn", "arabic_name": "الجن", "ayah_count": 28, "juz": 29, "revelation_place": "Makkah"},
    {"id": 73, "name": "Al-Muzzammil", "arabic_name": "المزمل", "ayah_count": 20, "juz": 29, "revelation_place": "Makkah"},
    {"id": 74, "name": "Al-Muddaththir", "arabic_name": "المدثر", "ayah_count": 56, "juz": 29, "revelation_place": "Makkah"},
    {"id": 75, "name": "Al-Qiyamah", "arabic_name": "القيامة", "ayah_count": 40, "juz": 29, "revelation_place": "Makkah"},
    {"id": 76, "name": "Al-Insan", "arabic_name": "الانسان", "ayah_count": 31, "juz": 29, "revelation_place": "Madinah"},
    {"id": 77, "name": "Al-Mursalat", "arabic_name": "المرسلات", "ayah_count": 50, "juz": 29, "revelation_place": "Makkah"},
    {"id": 78, "name": "An-Naba", "arabic_name": "النبإ", "ayah_count": 40, "juz": 30, "revelation_place": "Makkah"},
    {"id": 79, "name": "An-Nazi'at", "arabic_name": "النازعات", "ayah_count": 46, "juz": 30, "revelation_place": "Makkah"},
    {"id": 80, "name": "Abasa", "arabic_name": "عبس", "ayah_count": 42, "juz": 30, "revelation_place": "Makkah"},
    {"id": 81, "name": "At-Takwir", "arabic_name": "التكوير", "ayah_count": 29, "juz": 30, "revelation_place": "Makkah"},
    {"id": 82, "name": "Al-Infitar", "arabic_name": "الإنفطار", "ayah_count": 19, "juz": 30, "revelation_place": "Makkah"},
    {"id": 83, "name": "Al-Mutaffifin", "arabic_name": "المطففين", "ayah_count": 36, "juz": 30, "revelation_place": "Makkah"},
    {"id": 84, "name": "Al-Inshiqaq", "arabic_name": "الإنشقاق", "ayah_count": 25, "juz": 30, "revelation_place": "Makkah"},
    {"id": 85, "name": "Al-Buruj", "arabic_name": "البروج", "ayah_count": 22, "juz": 30, "revelation_place": "Makkah"},
    {"id": 86, "name": "At-Tariq", "arabic_name": "الطارق", "ayah_count": 17, "juz": 30, "revelation_place": "Makkah"},
    {"id": 87, "name": "Al-A'la", "arabic_name": "الأعلى", "ayah_count": 19, "juz": 30, "revelation_place": "Makkah"},
    {"id": 88, "name": "Al-Ghashiyah", "arabic_name": "الغاشية", "ayah_count": 26, "juz": 30, "revelation_place": "Makkah"},
    {"id": 89, "name": "Al-Fajr", "arabic_name": "الفجر", "ayah_count": 30, "juz": 30, "revelation_place": "Makkah"},
    {"id": 90, "name": "Al-Balad", "arabic_name": "البلد", "ayah_count": 20, "juz": 30, "revelation_place": "Makkah"},
    {"id": 91, "name": "Ash-Shams", "arabic_name": "الشمس", "ayah_count": 15, "juz": 30, "revelation_place": "Makkah"},
    {"id": 92, "name": "Al-Layl", "arabic_name": "الليل", "ayah_count": 21, "juz": 30, "revelation_place": "Makkah"},
    {"id": 93, "name": "Ad-Duhaa", "arabic_name": "الضحى", "ayah_count": 11, "juz": 30, "revelation_place": "Makkah"},
    {"id": 94, "name": "Ash-Sharh", "arabic_name": "الشرح", "ayah_count": 8, "juz": 30, "revelation_place": "Makkah"},
    {"id": 95, "name": "At-Tin", "arabic_name": "التين", "ayah_count": 8, "juz": 30, "revelation_place": "Makkah"},
    {"id": 96, "name": "Al-Alaq", "arabic_name": "العلق", "ayah_count": 19, "juz": 30, "revelation_place": "Makkah"},
    {"id": 97, "name": "Al-Qadr", "arabic_name": "القدر", "ayah_count": 5, "juz": 30, "revelation_place": "Makkah"},
    {"id": 98, "name": "Al-Bayyinah", "arabic_name": "البينة", "ayah_count": 8, "juz": 30, "revelation_place": "Madinah"},
    {"id": 99, "name": "Az-Zalzalah", "arabic_name": "الزلزلة", "ayah_count": 8, "juz": 30, "revelation_place": "Madinah"},
    {"id": 100, "name": "Al-Adiyat", "arabic_name": "العاديات", "ayah_count": 11, "juz": 30, "revelation_place": "Makkah"},
    {"id": 101, "name": "Al-Qari'ah", "arabic_name": "القارعة", "ayah_count": 11, "juz": 30, "revelation_place": "Makkah"},
    {"id": 102, "name": "At-Takathur", "arabic_name": "التكاثر", "ayah_count": 8, "juz": 30, "revelation_place": "Makkah"},
    {"id": 103, "name": "Al-Asr", "arabic_name": "العصر", "ayah_count": 3, "juz": 30, "revelation_place": "Makkah"},
    {"id": 104, "name": "Al-Humazah", "arabic_name": "الهمزة", "ayah_count": 9, "juz": 30, "revelation_place": "Makkah"},
    {"id": 105, "name": "Al-Fil", "arabic_name": "الفيل", "ayah_count": 5, "juz": 30, "revelation_place": "Makkah"},
    {"id": 106, "name": "Quraysh", "arabic_name": "قريش", "ayah_count": 4, "juz": 30, "revelation_place": "Makkah"},
    {"id": 107, "name": "Al-Ma'un", "arabic_name": "الماعون", "ayah_count": 7, "juz": 30, "revelation_place": "Makkah"},
    {"id": 108, "name": "Al-Kawthar", "arabic_name": "الكوثر", "ayah_count": 3, "juz": 30, "revelation_place": "Makkah"},
    {"id": 109, "name": "Al-Kafirun", "arabic_name": "الكافرون", "ayah_count": 6, "juz": 30, "revelation_place": "Makkah"},
    {"id": 110, "name": "An-Nasr", "arabic_name": "النصر", "ayah_count": 3, "juz": 30, "revelation_place": "Madinah"},
    {"id": 111, "name": "Al-Masad", "arabic_name": "المسد", "ayah_count": 5, "juz": 30, "revelation_place": "Makkah"},
    {"id": 112, "name": "Al-Ikhlas", "arabic_name": "الإخلاص", "ayah_count": 4, "juz": 30, "revelation_place": "Makkah"},
    {"id": 113, "name": "Al-Falaq", "arabic_name": "الفلق", "ayah_count": 5, "juz": 30, "revelation_place": "Makkah"},
    {"id": 114, "name": "An-Nas", "arabic_name": "الناس", "ayah_count": 6, "juz": 30, "revelation_place": "Makkah"},
]

# Juz metadata with start and end surah/ayah
JUZ_METADATA = [
    {"id": 1, "start_surah": 1, "start_ayah": 1, "end_surah": 2, "end_ayah": 141},
    {"id": 2, "start_surah": 2, "start_ayah": 142, "end_surah": 2, "end_ayah": 252},
    {"id": 3, "start_surah": 2, "start_ayah": 253, "end_surah": 3, "end_ayah": 92},
    {"id": 4, "start_surah": 3, "start_ayah": 93, "end_surah": 4, "end_ayah": 23},
    {"id": 5, "start_surah": 4, "start_ayah": 24, "end_surah": 4, "end_ayah": 147},
    {"id": 6, "start_surah": 4, "start_ayah": 148, "end_surah": 5, "end_ayah": 81},
    {"id": 7, "start_surah": 5, "start_ayah": 82, "end_surah": 6, "end_ayah": 110},
    {"id": 8, "start_surah": 6, "start_ayah": 111, "end_surah": 7, "end_ayah": 87},
    {"id": 9, "start_surah": 7, "start_ayah": 88, "end_surah": 8, "end_ayah": 40},
    {"id": 10, "start_surah": 8, "start_ayah": 41, "end_surah": 9, "end_ayah": 92},
    {"id": 11, "start_surah": 9, "start_ayah": 93, "end_surah": 11, "end_ayah": 5},
    {"id": 12, "start_surah": 11, "start_ayah": 6, "end_surah": 12, "end_ayah": 52},
    {"id": 13, "start_surah": 12, "start_ayah": 53, "end_surah": 14, "end_ayah": 52},
    {"id": 14, "start_surah": 15, "start_ayah": 1, "end_surah": 16, "end_ayah": 128},
    {"id": 15, "start_surah": 17, "start_ayah": 1, "end_surah": 18, "end_ayah": 74},
    {"id": 16, "start_surah": 18, "start_ayah": 75, "end_surah": 20, "end_ayah": 135},
    {"id": 17, "start_surah": 21, "start_ayah": 1, "end_surah": 22, "end_ayah": 78},
    {"id": 18, "start_surah": 23, "start_ayah": 1, "end_surah": 25, "end_ayah": 20},
    {"id": 19, "start_surah": 25, "start_ayah": 21, "end_surah": 27, "end_ayah": 55},
    {"id": 20, "start_surah": 27, "start_ayah": 56, "end_surah": 29, "end_ayah": 45},
    {"id": 21, "start_surah": 29, "start_ayah": 46, "end_surah": 33, "end_ayah": 30},
    {"id": 22, "start_surah": 33, "start_ayah": 31, "end_surah": 36, "end_ayah": 27},
    {"id": 23, "start_surah": 36, "start_ayah": 28, "end_surah": 39, "end_ayah": 31},
    {"id": 24, "start_surah": 39, "start_ayah": 32, "end_surah": 41, "end_ayah": 46},
    {"id": 25, "start_surah": 41, "start_ayah": 47, "end_surah": 45, "end_ayah": 37},
    {"id": 26, "start_surah": 46, "start_ayah": 1, "end_surah": 51, "end_ayah": 30},
    {"id": 27, "start_surah": 51, "start_ayah": 31, "end_surah": 57, "end_ayah": 29},
    {"id": 28, "start_surah": 58, "start_ayah": 1, "end_surah": 66, "end_ayah": 12},
    {"id": 29, "start_surah": 67, "start_ayah": 1, "end_surah": 77, "end_ayah": 50},
    {"id": 30, "start_surah": 78, "start_ayah": 1, "end_surah": 114, "end_ayah": 6},
]


def get_all_surahs() -> List[Dict]:
    """Get all surah metadata"""
    return SURAH_METADATA


def get_surah_by_id(surah_id: int) -> Optional[Dict]:
    """Get specific surah metadata by ID"""
    if 1 <= surah_id <= 114:
        return SURAH_METADATA[surah_id - 1]
    return None


def get_surahs_by_juz(juz: int) -> List[Dict]:
    """Get all surahs that belong to a specific juz"""
    return [s for s in SURAH_METADATA if s["juz"] == juz]


def get_all_juz() -> List[Dict]:
    """Get all juz metadata"""
    return JUZ_METADATA


def get_juz_by_id(juz_id: int) -> Optional[Dict]:
    """Get specific juz metadata by ID"""
    if 1 <= juz_id <= 30:
        return JUZ_METADATA[juz_id - 1]
    return None


def get_surah_name(surah_id: int, language: str = "en") -> Optional[str]:
    """Get surah name in specified language"""
    surah = get_surah_by_id(surah_id)
    if surah:
        return surah["arabic_name"] if language == "ar" else surah["name"]
    return None
