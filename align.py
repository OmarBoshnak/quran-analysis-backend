"""
Text alignment and error rate calculation
Handles Arabic text normalization and comparison
"""

import difflib
import logging
from typing import List, Tuple

from jiwer import wer, cer

from arabic_norm import normalize_letters, strip_tashkeel

logger = logging.getLogger(__name__)


def tokenize_arabic(text: str) -> List[str]:
    """
    Tokenize and normalize Arabic text

    Steps:
    1. Normalize letter forms (alif variants, taa marbuta)
    2. Strip diacritical marks (tashkeel) for stability
    3. Remove extra whitespace
    4. Split into tokens
    """

    # Normalize letters (unify alifs, etc.)
    normalized = normalize_letters(text)

    # Strip tashkeel (harakat) to reduce ASR comparison noise
    cleaned = strip_tashkeel(normalized)

    # Tokenize on whitespace
    tokens = [tok for tok in cleaned.split() if tok]

    logger.debug(f"Tokenized '{text[:30]}...' into {len(tokens)} tokens")

    return tokens


def wer_and_alignment(
        ref_tokens: List[str],
        hyp_tokens: List[str]
) -> Tuple[float, float, List[dict]]:
    """
    Calculate Word Error Rate, Character Error Rate, and alignment

    Returns:
        - WER (Word Error Rate): 0.0 = perfect, 1.0 = completely wrong
        - CER (Character Error Rate): character-level accuracy
        - alignment_hints: list of specific mistakes (substitution/omission/insertion)
    """

    # Calculate WER
    ref_str = " ".join(ref_tokens)
    hyp_str = " ".join(hyp_tokens)

    try:
        wer_value = wer(ref_str, hyp_str) if ref_str else 0.0
        cer_value = cer(ref_str, hyp_str) if ref_str else 0.0
    except Exception as e:
        logger.error(f"Error calculating WER/CER: {e}")
        wer_value = 1.0
        cer_value = 1.0

    # Detailed alignment using difflib
    matcher = difflib.SequenceMatcher(a=ref_tokens, b=hyp_tokens)
    hints = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            # Substitution: wrong word(s)
            hints.append({
                "type": "substitution",
                "position": i1,
                "ref": " ".join(ref_tokens[i1:i2]),
                "hyp": " ".join(hyp_tokens[j1:j2]),
                "hint": f"[translate:قلت] '{hyp_tokens[j1:j2][0] if j1 < j2 else ''}' [translate:لكن يجب أن تكون] '{ref_tokens[i1:i2][0] if i1 < i2 else ''}'"
            })

        elif tag == "delete":
            # Omission: missing word(s)
            hints.append({
                "type": "omission",
                "position": i1,
                "ref": " ".join(ref_tokens[i1:i2]),
                "hyp": "",
                "hint": f"[translate:نسيت كلمة:] {' '.join(ref_tokens[i1:i2])}"
            })

        elif tag == "insert":
            # Insertion: extra word(s)
            hints.append({
                "type": "insertion",
                "position": j1,
                "ref": "",
                "hyp": " ".join(hyp_tokens[j1:j2]),
                "hint": f"[translate:أضفت كلمة زائدة:] {' '.join(hyp_tokens[j1:j2])}"
            })

    logger.info(f"WER: {wer_value:.2f}, CER: {cer_value:.2f}, Mistakes: {len(hints)}")

    return float(wer_value), float(cer_value), hints
