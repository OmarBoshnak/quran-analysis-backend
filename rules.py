"""
Comprehensive Tajweed Rules for Quran Recitation Analysis
Integrated from advanced implementation with full rule coverage
"""

import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class TajweedAnalyzer:
    """
    Complete Tajweed rules database with analysis capabilities
    Covers all major Tajweed rules for proper Quran pronunciation
    """

    # Madd (Elongation) rules - hold for 2, 4, or 6 counts
    MADD_RULES = {
        'madd_tabee3i': {
            'pattern': r'[اوي](?=[ً-ٌ-ٍ-َ-ُ-ِ])',
            'duration': 2,
            'name_ar': '[translate:مد طبيعي]',
            'description': 'Natural elongation - hold for 2 counts',
            'examples': ['[translate:قَالَ]', '[translate:قِيلَ]', '[translate:قُولُوا]']
        },
        'madd_muttasil': {
            'pattern': r'[اوي](?=ء[ً-ٌ-ٍ-َ-ُ-ِ])',
            'duration': 4,
            'name_ar': '[translate:مد متصل]',
            'description': 'Connected elongation - hold for 4-5 counts',
            'examples': ['[translate:السَّمَاءِ]', '[translate:جَاءَ]']
        },
        'madd_munfasil': {
            'pattern': r'[اوي]\s+[ء]',
            'duration': 4,
            'name_ar': '[translate:مد منفصل]',
            'description': 'Separated elongation - hold for 4-5 counts',
            'examples': ['[translate:وَفِي أَنفُسِكُم]']
        },
        'madd_lazim': {
            'pattern': r'[اوي](?=[ّ])',
            'duration': 6,
            'name_ar': '[translate:مد لازم]',
            'description': 'Necessary elongation - hold for 6 counts',
            'examples': ['[translate:الصَّاخَّةُ]', '[translate:الْحَاقَّةُ]']
        }
    }

    # Qalqala (Echo) rules - letters that bounce: ق ط ب ج د
    QALQALA_LETTERS = {
        'letters': ['ق', 'ط', 'ب', 'ج', 'د'],
        'name_ar': '[translate:قلقلة]',
        'description': 'Echo/bounce sound when letter has sukoon',
        'types': {
            'sughra': 'Small echo (middle of word)',
            'kubra': 'Big echo (end of verse)'
        },
        'examples': {
            'ق': '[translate:يَخْلُقُ]',
            'ط': '[translate:وَالْقِسْطِ]',
            'ب': '[translate:اكْتَسَبَ]',
            'ج': '[translate:أَخْرَجَ]',
            'د': '[translate:رَدَّ]'
        }
    }

    # Idgham (Merging) rules - YARMULUN letters (يرملون)
    IDGHAM_RULES = {
        'with_ghunna': {
            'letters': ['ي', 'ن', 'م', 'و'],
            'name_ar': '[translate:إدغام بغنة]',
            'description': 'Merge with nasal sound (ghunna) for 2 counts',
            'examples': ['[translate:مِن يَّقُولُ]', '[translate:مِن نَّذِيرٍ]']
        },
        'without_ghunna': {
            'letters': ['ل', 'ر'],
            'name_ar': '[translate:إدغام بلا غنة]',
            'description': 'Merge without nasal sound',
            'examples': ['[translate:مِن رَّبِّهِمْ]', '[translate:مِن لَّدُنْهُ]']
        }
    }

    # Ikhfa (Hiding) - 15 letters
    IKHFA_LETTERS = {
        'letters': ['ت', 'ث', 'ج', 'د', 'ذ', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ف', 'ق', 'ك'],
        'name_ar': '[translate:إخفاء]',
        'description': 'Hide noon sakinah/tanween with nasal sound'
    }

    # Iqlab (Conversion)
    IQLAB_LETTER = {
        'letter': 'ب',
        'name_ar': '[translate:إقلاب]',
        'description': 'Convert noon sakinah/tanween to meem sound before baa'
    }

    # Izhar (Clear pronunciation) - Throat letters
    IZHAR_LETTERS = {
        'letters': ['ء', 'ه', 'ع', 'ح', 'غ', 'خ'],
        'name_ar': '[translate:إظهار]',
        'description': 'Clear pronunciation of noon sakinah/tanween'
    }

    # Tafkhim (Heavy) vs Tarqeeq (Light)
    TAFKHIM_LETTERS = {
        'primary': ['ص', 'ض', 'ط', 'ظ'],  # Always heavy
        'name_ar': '[translate:تفخيم]',
        'conditional': {
            'ر': 'Heavy when fatha/damma or after fatha/damma',
            'ل': 'Heavy only in Allah (except after kasra)',
            'ق': 'Heavy letter'
        }
    }

    # Ghunna (Nasal sound)
    GHUNNA_RULES = {
        'noon_mushaddada': {'letter': 'نّ', 'duration': 2},
        'meem_mushaddada': {'letter': 'مّ', 'duration': 2},
        'name_ar': '[translate:غنة]',
        'description': 'Nasal sound from nose for 2 counts'
    }

    # Ra rules (complex conditional)
    RA_RULES = {
        'tafkhim': [
            'When Ra has fatha (رَ)',
            'When Ra has damma (رُ)',
            'When Ra has sukoon after fatha/damma',
            'At beginning of word with sukoon'
        ],
        'tarqeeq': [
            'When Ra has kasra (رِ)',
            'When Ra has sukoon after kasra',
            'When followed by Ya with kasra'
        ]
    }

    # Lam rules
    LAM_RULES = {
        'tafkhim': 'Only in [translate:ٱللَّٰهُ] (Allah) when not preceded by kasra',
        'tarqeeq': 'All other cases and in Allah after kasra'
    }

    # Common mistakes by letter
    COMMON_MISTAKES = {
        'ص': ['Too soft - should be heavy from throat', 'Not emphatic enough'],
        'ض': ['Tongue position wrong - touch upper molars', 'Not heavy enough'],
        'ط': ['Not heavy enough', 'Should be explosive from throat'],
        'ظ': ['Confused with ذ - should be heavier', 'Tongue between teeth'],
        'ق': ['Too soft - from back of throat', 'Not using uvula properly'],
        'ح': ['Too breathy', 'Should be clear from middle throat'],
        'ع': ['Not deep enough from throat', 'Confused with hamza'],
        'خ': ['Too soft', 'Should be from back of throat like gargling'],
        'غ': ['Not enough vibration from throat', 'Too similar to خ'],
        'ر': ['Not rolling enough', 'Trill should be present'],
        'ل': ['Tongue position wrong', 'Tip should touch upper palate'],
        'ث': ['Confused with س - tongue between teeth'],
        'ذ': ['Confused with ز - tongue between teeth'],
    }

    def analyze_word(self, word: str, context: str = '') -> List[Dict]:
        """
        Analyze a single word for Tajweed rules

        Returns:
            List of applicable Tajweed rules with guidance
        """
        rules_found = []

        # Check for Madd (elongation)
        for madd_type, rule in self.MADD_RULES.items():
            if re.search(rule['pattern'], word):
                rules_found.append({
                    'type': 'madd',
                    'subtype': madd_type,
                    'name_ar': rule['name_ar'],
                    'word': word,
                    'duration': rule['duration'],
                    'guidance': f"Hold for {rule['duration']} counts: {rule['description']}"
                })

        # Check for Qalqala
        for letter in self.QALQALA_LETTERS['letters']:
            if letter + 'ْ' in word or letter == word[-1]:  # Sukoon or end
                rules_found.append({
                    'type': 'qalqala',
                    'letter': letter,
                    'word': word,
                    'guidance': f"Make {letter} bounce with echo sound (Qalqala)"
                })

        # Check for Tafkhim (heavy letters)
        for letter in self.TAFKHIM_LETTERS['primary']:
            if letter in word:
                rules_found.append({
                    'type': 'tafkhim',
                    'letter': letter,
                    'word': word,
                    'guidance': f"Pronounce {letter} with heavy/full sound from back of throat"
                })

        # Check for Ghunna (نّ or مّ)
        if 'نّ' in word or 'مّ' in word:
            rules_found.append({
                'type': 'ghunna',
                'word': word,
                'duration': 2,
                'guidance': "[translate:غنة] - Nasal sound from nose for 2 counts"
            })

        # Check for Shadda (general)
        if 'ّ' in word:
            rules_found.append({
                'type': 'shadda',
                'word': word,
                'guidance': "[translate:شدّة] - Double/emphasize the letter with shadda"
            })

        return rules_found

    def analyze_full_text(self, arabic_text: str) -> Dict:
        """
        Analyze complete Arabic text for all Tajweed rules

        Returns:
            Comprehensive analysis with rule counts and guidance
        """
        words = arabic_text.split()
        analysis = {
            'total_words': len(words),
            'rules_by_type': {},
            'all_rules': [],
            'difficulty_score': 0
        }

        for idx, word in enumerate(words):
            word_rules = self.analyze_word(word, context=arabic_text)

            for rule in word_rules:
                rule['word_index'] = idx
                analysis['all_rules'].append(rule)

                # Count by type
                rule_type = rule['type']
                if rule_type not in analysis['rules_by_type']:
                    analysis['rules_by_type'][rule_type] = 0
                analysis['rules_by_type'][rule_type] += 1

        # Calculate difficulty
        total_rules = len(analysis['all_rules'])
        analysis['difficulty_score'] = min(10, total_rules // 2)

        return analysis

    def get_pronunciation_guide(self, arabic_text: str) -> Dict:
        """
        Get complete pronunciation guide for text
        """
        words = arabic_text.split()
        full_analysis = {
            'text': arabic_text,
            'word_count': len(words),
            'rules': [],
            'difficulty_level': 'beginner',
            'estimated_duration': len(words) * 2  # seconds per word
        }

        for word in words:
            word_rules = self.analyze_word(word)
            if word_rules:
                full_analysis['rules'].extend(word_rules)

        # Determine difficulty based on rule count
        rule_count = len(full_analysis['rules'])
        if rule_count > 15:
            full_analysis['difficulty_level'] = 'advanced'
        elif rule_count > 8:
            full_analysis['difficulty_level'] = 'intermediate'

        return full_analysis

    def get_common_mistakes(self, letter: str) -> List[str]:
        """Get common pronunciation mistakes for a specific letter"""
        return self.COMMON_MISTAKES.get(letter, [])


def detect_tajweed_hints(
        expected_arabic: str,
        ref_tokens: List[str],
        hyp_tokens: List[str]
) -> List[Dict]:
    """
    Detect Tajweed rule violations by comparing reference and hypothesis

    Focus on practical mistakes children make:
    - Missing Shadda (شدّة)
    - Missing Qalqala (قلقلة)
    - Wrong Madd duration
    - Tafkhim/Tarqeeq mistakes
    """
    hints = []

    # Simple lexicon patterns
    QALQALA_LETTERS = set(['ق', 'ط', 'ب', 'ج', 'د'])
    SHADDA = 'ّ'

    # 1. Check Shadda presence/omission
    for idx, ref in enumerate(ref_tokens):
        ref_has_shadda = SHADDA in ref
        hyp = hyp_tokens[idx] if idx < len(hyp_tokens) else ""
        hyp_has_shadda = SHADDA in hyp

        if ref_has_shadda and not hyp_has_shadda:
            hints.append({
                'type': 'shadda',
                'wordIndex': idx,
                'word': ref,
                'hint': f"[translate:شدّة مطلوبة هنا — إشباع الحرف المشدد] in {ref}"
            })

    # 2. Qalqala check (قلقلة) - naive check for word-final qalqala letters
    for idx, ref in enumerate(ref_tokens):
        # Strip diacritics for checking
        base = ''.join([c for c in ref if c.isalpha()])
        if base and base[-1] in QALQALA_LETTERS:
            hints.append({
                'type': 'qalqala',
                'wordIndex': idx,
                'word': ref,
                'hint': f"[translate:قلقلة خفيفة على الحرف الأخير] ({base[-1]}) in {ref}"
            })

    # 3. Madd (مدّ) - check for madd letters (elongation)
    MADD_MARKERS = ['ا', 'و', 'ي', 'آ', 'ى']
    for idx, ref in enumerate(ref_tokens):
        hyp = hyp_tokens[idx] if idx < len(hyp_tokens) else ""
        if any(m in ref for m in MADD_MARKERS):
            # If hypothesis is much shorter, may have skipped madd
            if len(hyp) <= max(1, len(ref) - 2):
                hints.append({
                    'type': 'madd',
                    'wordIndex': idx,
                    'word': ref,
                    'hint': f"[translate:مدّ الحرف قليلاً (إطالة الصوت)] in {ref}"
                })

    # 4. Tafkhim hints for next word starting with ر or ل after ال
    for idx in range(len(ref_tokens) - 1):
        nxt = ref_tokens[idx + 1]
        if nxt.startswith('الر') or nxt.startswith('الل'):
            hints.append({
                'type': 'tafkhim',
                'wordIndex': idx + 1,
                'word': nxt,
                'hint': f"[translate:تفخيم] (heavy pronunciation) in {nxt}"
            })

    logger.info(f"Detected {len(hints)} Tajweed hints")
    return hints
