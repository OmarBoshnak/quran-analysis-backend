"""
AI-powered feedback generation for Quran recitation
Uses Google Gemini for child-friendly guidance
"""

import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Try to import Gemini
USE_GEMINI = bool(os.getenv("GEMINI_API_KEY"))

if USE_GEMINI:
    try:
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        logger.info("Gemini AI initialized successfully")
    except Exception as e:
        logger.warning(f"Gemini initialization failed: {e}. Using fallback feedback.")
        USE_GEMINI = False


async def generate_kid_feedback(
        expected_arabic: str,
        transcript: str,
        wer: float,
        cer: float,
        rule_hints: List[Dict]
) -> str:
    """
    Generate encouraging, child-friendly feedback

    Parameters:
        expected_arabic: The correct Arabic text
        transcript: What the child actually said
        wer: Word Error Rate (0-1)
        cer: Character Error Rate (0-1)
        rule_hints: List of Tajweed rule hints

    Returns:
        Encouraging feedback message in Arabic
    """

    # Fallback function for when Gemini is unavailable
    def fallback_feedback():
        accuracy = (1 - wer) * 100

        if accuracy >= 95:
            return "[translate:قراءة ممتازة جداً! 🌟 ما شاء الله، أحسنت! استمر بهذا الأداء الرائع.]"
        elif accuracy >= 85:
            return "[translate:قراءة جيدة جداً! 👏 أحسنت، مع بعض التحسينات الصغيرة ستكون ممتازاً.]"
        elif accuracy >= 70:
            return "[translate:جيد! 👍 جرّب التركيز على المدّ والشدّة في الكلمات. حاول مرة أخرى.]"
        elif accuracy >= 50:
            return "[translate:لا بأس، بداية جيدة! 😊 استمع للتسجيل النموذجي وحاول مرة أخرى ببطء.]"
        else:
            return "[translate:حاول مرة أخرى! 💪 استمع جيداً للتسجيل واقرأ ببطء. أنت تستطيع!]"

    # If Gemini not available, use fallback
    if not USE_GEMINI:
        return fallback_feedback()

    # Prepare context for Gemini
    accuracy = (1 - wer) * 100

    # Limit rule hints to avoid prompt being too long
    rule_summary = "\n".join([
        f"- {h.get('word', '')}: {h.get('hint', '')}"
        for h in rule_hints[:5]  # Top 5 hints only
    ])

    prompt = f"""
أنت معلم قرآن لطيف ومشجّع للأطفال من عمر 5-15 سنوات.

الطفل حاول قراءة:
**النص المتوقع**: {expected_arabic}

ما قاله الطفل:
**النص المقروء**: {transcript}

**نسبة الدقة**: {accuracy:.1f}%
**معدل الخطأ**: WER={wer:.2f}, CER={cer:.2f}

**ملاحظات تجويد**:
{rule_summary if rule_summary else 'لا توجد ملاحظات خاصة'}

اكتب رسالة قصيرة (50-80 كلمة) باللغة العربية تتضمن:
1. كلمات تشجيعية (هم يتعلمون!)
2. توجيه محدد وبسيط لما يجب تحسينه (إذا كان هناك أخطاء)
3. نصيحة واحدة للنطق الأفضل
4. استخدم الإيموجي وأسلوب بسيط

كن إيجابياً جداً ومشجعاً!
"""

    try:
        # Generate with Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=200,
            )
        )

        feedback = response.text.strip()

        # Ensure not too long
        if len(feedback) > 300:
            feedback = feedback[:297] + "..."

        logger.info(f"Generated AI feedback: {len(feedback)} chars")
        return feedback

    except Exception as e:
        logger.exception(f"Gemini feedback generation failed: {e}")
        return fallback_feedback()


def get_encouragement_by_score(score: int) -> str:
    """
    Get quick encouragement message based on score (0-100)
    """
    if score >= 95:
        return "[translate:ممتاز جداً!] 🌟"
    elif score >= 85:
        return "[translate:جيد جداً!] 👏"
    elif score >= 70:
        return "[translate:جيد!] 👍"
    elif score >= 50:
        return "[translate:لا بأس!] 😊"
    else:
        return "[translate:حاول مرة أخرى!] 💪"
