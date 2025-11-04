"""
Tests for Quran metadata functionality
"""

import pytest
from quran_metadata import (
    get_all_surahs,
    get_surah_by_id,
    get_surahs_by_juz,
    get_all_juz,
    get_juz_by_id,
    get_surah_name
)


class TestSurahMetadata:
    """Test surah metadata functions"""
    
    def test_get_all_surahs(self):
        """Test getting all surahs"""
        surahs = get_all_surahs()
        assert len(surahs) == 114
        assert surahs[0]["id"] == 1
        assert surahs[0]["name"] == "Al-Fatihah"
        assert surahs[113]["id"] == 114
        assert surahs[113]["name"] == "An-Nas"
    
    def test_get_surah_by_id_valid(self):
        """Test getting surah by valid ID"""
        # Test Al-Fatihah
        surah = get_surah_by_id(1)
        assert surah is not None
        assert surah["name"] == "Al-Fatihah"
        assert surah["arabic_name"] == "الفاتحة"
        assert surah["ayah_count"] == 7
        assert surah["juz"] == 1
        assert surah["revelation_place"] == "Makkah"
        
        # Test Al-Baqarah
        surah = get_surah_by_id(2)
        assert surah is not None
        assert surah["name"] == "Al-Baqarah"
        assert surah["ayah_count"] == 286
    
    def test_get_surah_by_id_invalid(self):
        """Test getting surah with invalid ID"""
        assert get_surah_by_id(0) is None
        assert get_surah_by_id(115) is None
        assert get_surah_by_id(-1) is None
    
    def test_get_surahs_by_juz(self):
        """Test getting surahs by juz"""
        # Juz 1 contains Al-Fatihah and part of Al-Baqarah
        juz_1_surahs = get_surahs_by_juz(1)
        assert len(juz_1_surahs) >= 1
        assert any(s["id"] == 1 for s in juz_1_surahs)
        
        # Juz 30 contains multiple short surahs
        juz_30_surahs = get_surahs_by_juz(30)
        assert len(juz_30_surahs) > 30  # Many short surahs in Juz 30
    
    def test_get_surah_name(self):
        """Test getting surah name in different languages"""
        # English
        name_en = get_surah_name(1, "en")
        assert name_en == "Al-Fatihah"
        
        # Arabic
        name_ar = get_surah_name(1, "ar")
        assert name_ar == "الفاتحة"
        
        # Invalid ID
        assert get_surah_name(0) is None
        assert get_surah_name(115) is None


class TestJuzMetadata:
    """Test juz metadata functions"""
    
    def test_get_all_juz(self):
        """Test getting all juz"""
        juz_list = get_all_juz()
        assert len(juz_list) == 30
        assert juz_list[0]["id"] == 1
        assert juz_list[29]["id"] == 30
    
    def test_get_juz_by_id_valid(self):
        """Test getting juz by valid ID"""
        # Test Juz 1
        juz = get_juz_by_id(1)
        assert juz is not None
        assert juz["start_surah"] == 1
        assert juz["start_ayah"] == 1
        
        # Test Juz 30
        juz = get_juz_by_id(30)
        assert juz is not None
        assert juz["start_surah"] == 78
        assert juz["end_surah"] == 114
    
    def test_get_juz_by_id_invalid(self):
        """Test getting juz with invalid ID"""
        assert get_juz_by_id(0) is None
        assert get_juz_by_id(31) is None
        assert get_juz_by_id(-1) is None
    
    def test_juz_completeness(self):
        """Test that all juz data is complete"""
        juz_list = get_all_juz()
        for juz in juz_list:
            assert "id" in juz
            assert "start_surah" in juz
            assert "start_ayah" in juz
            assert "end_surah" in juz
            assert "end_ayah" in juz
            assert 1 <= juz["start_surah"] <= 114
            assert 1 <= juz["end_surah"] <= 114
            assert juz["start_ayah"] >= 1
            assert juz["end_ayah"] >= 1


class TestDataConsistency:
    """Test consistency between different data structures"""
    
    def test_surah_count_consistency(self):
        """Test that ayah counts are consistent"""
        surahs = get_all_surahs()
        from quran_data import SURAH_AYAH_COUNTS
        
        for surah in surahs:
            surah_id = surah["id"]
            assert surah["ayah_count"] == SURAH_AYAH_COUNTS[surah_id], \
                f"Ayah count mismatch for Surah {surah_id}"
    
    def test_juz_numbers(self):
        """Test that juz numbers are valid"""
        surahs = get_all_surahs()
        for surah in surahs:
            assert 1 <= surah["juz"] <= 30, \
                f"Invalid juz number for Surah {surah['id']}: {surah['juz']}"
    
    def test_revelation_places(self):
        """Test that revelation places are valid"""
        surahs = get_all_surahs()
        valid_places = ["Makkah", "Madinah"]
        for surah in surahs:
            assert surah["revelation_place"] in valid_places, \
                f"Invalid revelation place for Surah {surah['id']}: {surah['revelation_place']}"
