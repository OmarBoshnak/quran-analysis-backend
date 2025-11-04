"""
AI-powered feedback generation for Quran recitation
Uses Google Gemini for child-friendly guidance
Version: 2.0.0
"""

import logging
from typing import List, Dict

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Gemini AI
USE_GEMINI = bool(settings.GEMINI_API_KEY)
_gemini_model = None

if USE_GEMINI:
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
        logger.info(f"✓ Gemini AI initialized successfully: {settings.GEMINI_MODEL}")
    except ImportError:
        logger.warning("⚠ google-generativeai package not installed. Using fallback feedback.")
        USE_GEMINI = False
    except Exception as e:
        logger.warning(f"⚠ Gemini initialization failed: {e}. Using fallback feedback.")
        USE_GEMINI = False
else:
    logger.info("ℹ Gemini API key not configured. Using fallback feedback system.")


async def generate_kid_feedback(
        expected_arabic: str,
        transcript: str,
        wer: float,
        cer: float,
        rule_hints: List[Dict]
) -> str:
    """
    Generate encouraging, child-friendly feedback for Quran recitation

    This function uses Google Gemini AI to create personalized, age-appropriate
    feedback in Arabic. If Gemini is unavailable, it falls back to template-based
    feedback.

    Parameters:
        expected_arabic: The correct Arabic text the child should recite
        transcript: What the child actually recited (from ASR)
        wer: Word Error Rate (0.0-1.0, lower is better)
        cer: Character Error Rate (0.0-1.0, lower is better)
        rule_hints: List of Tajweed rule hints detected

    Returns:
        str: Encouraging feedback message in Arabic with emoji

    Example:
        >>> feedback = await generate_kid_feedback(
        ...     expected_arabic="بسم الله الرحمن الرحيم",
        ...     transcript="بسم الله الرحمان الرحيم",
        ...     wer=0.25,
        ...     cer=0.15,
        ...     rule_hints=[{"word": "الرحمن", "hint": "مد طبيعي"}]
        ... )
        >>> print(feedback)
        'قراءة جيدة! 👍 انتبه لكلمة "الرحمن" - مد الألف قليلاً...'
    """

    # Calculate accuracy for easier understanding
    accuracy = (1 - wer) * 100

    # If Gemini not available, use fallback
    if not USE_GEMINI or _gemini_model is None:
        logger.info("Using fallback feedback system")
        return _fallback_feedback(accuracy, wer, cer, rule_hints)

    # Prepare context for Gemini
    try:
        feedback = await _generate_gemini_feedback(
            expected_arabic=expected_arabic,
            transcript=transcript,
            accuracy=accuracy,
            wer=wer,
            cer=cer,
            rule_hints=rule_hints
        )
        return feedback
    except Exception as e:
        logger.exception(f"✗ Gemini feedback generation failed: {e}")
        logger.info("Falling back to template-based feedback")
        return _fallback_feedback(accuracy, wer, cer, rule_hints)


def _fallback_feedback(
        accuracy: float,
        wer: float,
        cer: float,
        rule_hints: List[Dict]
) -> str:
    """
    Template-based fallback feedback when Gemini is unavailable

    Provides encouraging, age-appropriate feedback based on accuracy score
    and detected Tajweed issues.

    Parameters:
        accuracy: Accuracy percentage (0-100)
        wer: Word Error Rate
        cer: Character Error Rate
        rule_hints: List of Tajweed hints

    Returns:
        str: Template-based feedback message in Arabic
    """

    # Base encouragement by accuracy level
    if accuracy >= 95:
        base_message = "قراءة ممتازة جداً! 🌟 ما شاء الله، أحسنت!"
        extra = "استمر بهذا الأداء الرائع."
    elif accuracy >= 85:
        base_message = "قراءة جيدة جداً! 👏 أحسنت!"
        extra = "مع بعض التحسينات الصغيرة ستكون ممتازاً."
    elif accuracy >= 70:
        base_message = "جيد! 👍"
        extra = "جرّب التركيز على المدّ والشدّة في الكلمات. حاول مرة أخرى."
    elif accuracy >= 50:
        base_message = "لا بأس، بداية جيدة! 😊"
        extra = "استمع للتسجيل النموذجي وحاول مرة أخرى ببطء."
    else:
        base_message = "حاول مرة أخرى! 💪"
        extra = "استمع جيداً للتسجيل واقرأ ببطء. أنت تستطيع!"

    # Add specific Tajweed hint if available
    if rule_hints and len(rule_hints) > 0:
        first_hint = rule_hints[0]
        word = first_hint.get('word', '')
        hint_text = first_hint.get('hint', '')

        if word and hint_text:
            # Extract simple hint (remove technical details)
            if 'مد' in hint_text:
                tajweed_tip = f"تذكر: مد الحرف في كلمة '{word}'"
            elif 'شدة' in hint_text or 'شدّة' in hint_text:
                tajweed_tip = f"تذكر: تشديد الحرف في كلمة '{word}'"
            elif 'قلقلة' in hint_text:
                tajweed_tip = f"تذكر: قلقلة الحرف في كلمة '{word}'"
            else:
                tajweed_tip = f"انتبه لكلمة '{word}'"

            return f"{base_message} {tajweed_tip}. {extra}"

    return f"{base_message} {extra}"


async def _generate_gemini_feedback(
        expected_arabic: str,
        transcript: str,
        accuracy: float,
        wer: float,
        cer: float,
        rule_hints: List[Dict]
) -> str:
    """
    Generate personalized feedback using Google Gemini AI

    Creates child-friendly, encouraging feedback in Arabic based on
    the recitation quality and detected mistakes.

    Parameters:
        expected_arabic: Expected Arabic text
        transcript: Actual transcribed text
        accuracy: Accuracy percentage
        wer: Word Error Rate
        cer: Character Error Rate
        rule_hints: Tajweed hints

    Returns:
        str: AI-generated feedback in Arabic

    Raises:
        Exception: If Gemini API call fails
    """

    # Limit rule hints to avoid prompt being too long
    rule_summary = "\n".join([
        f"- {h.get('word', '')}: {h.get('hint', '')}"
        for h in rule_hints[:5]  # Top 5 hints only
    ])

    # Construct the prompt for Gemini
    prompt = f"""
أنت معلم قرآن كريم لطيف ومشجّع للأطفال من عمر 5-15 سنوات.

الطفل حاول قراءة الآية التالية:
**النص المتوقع**: {expected_arabic}

ما قاله الطفل بالفعل:
**النص المقروء**: {transcript}

**نسبة الدقة**: {accuracy:.1f}%
**معدل الخطأ في الكلمات**: WER={wer:.2f}
**معدل الخطأ في الحروف**: CER={cer:.2f}

**ملاحظات تجويد**:
{rule_summary if rule_summary else 'لا توجد ملاحظات خاصة'}

المطلوب منك:
اكتب رسالة تشجيعية قصيرة (50-80 كلمة فقط) باللغة العربية الفصحى البسيطة تتضمن:

1. كلمات تشجيعية مناسبة لعمر الطفل (هم يتعلمون ويجب تشجيعهم!)
2. إذا كانت هناك أخطاء، أذكر توجيهاً واحداً محدداً وبسيطاً لما يجب تحسينه
3. نصيحة واحدة عملية للنطق الأفضل
4. استخدم الإيموجي المناسب (🌟 للممتاز، 👏 للجيد جداً، 👍 للجيد، 😊 للمقبول، 💪 للتشجيع)

ملاحظات مهمة:
- كن إيجابياً جداً ومشجعاً حتى مع الأخطاء الكثيرة
- استخدم أسلوباً بسيطاً يفهمه الأطفال
- لا تكتب أكثر من 80 كلمة
- ركز على التشجيع أكثر من النقد
"""

    try:
        # Generate with Gemini
        response = _gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,  # Some creativity, but controlled
                "max_output_tokens": 200,  # Limit response length
                "top_p": 0.9,
                "top_k": 40,
            }
        )

        feedback = response.text.strip()

        # Ensure not too long (hard limit)
        if len(feedback) > 300:
            feedback = feedback[:297] + "..."

        logger.info(f"✓ Generated AI feedback: {len(feedback)} characters")
        return feedback

    except Exception as e:
        logger.error(f"✗ Gemini API error: {str(e)}")
        raise


def get_encouragement_by_score(score: int) -> str:
    """
    Get quick encouragement message based on numerical score

    Provides a simple, emoji-enhanced encouragement message based on
    the recitation score. Useful for quick feedback in UI.

    Parameters:
        score: Numerical score from 0-100

    Returns:
        str: Short encouragement message with emoji

    Example:
        >>> get_encouragement_by_score(95)
        'ممتاز جداً! 🌟'
        >>> get_encouragement_by_score(75)
        'جيد! 👍'
    """
    if score >= 95:
        return "ممتاز جداً! 🌟"
    elif score >= 85:
        return "جيد جداً! 👏"
    elif score >= 70:
        return "جيد! 👍"
    elif score >= 50:
        return "لا بأس! 😊"
    else:
        return "حاول مرة أخرى! 💪"


def get_detailed_encouragement(score: int, mistakes_count: int = 0) -> dict:
    """
    Get detailed encouragement with additional context

    Provides structured feedback including emoji, title, message,
    and suggestions based on score and mistake count.

    Parameters:
        score: Numerical score from 0-100
        mistakes_count: Number of mistakes detected (optional)

    Returns:
        dict: Structured feedback with multiple fields

    Example:
        >>> feedback = get_detailed_encouragement(85, mistakes_count=2)
        >>> print(feedback['title'])
        'جيد جداً!'
        >>> print(feedback['emoji'])
        '👏'
    """
    if score >= 95:
        return {
            "emoji": "🌟",
            "title": "ممتاز جداً!",
            "message": "ما شاء الله، أحسنت! قراءة رائعة.",
            "color": "green",
            "suggestion": "استمر بهذا الأداء الممتاز"
        }
    elif score >= 85:
        return {
            "emoji": "👏",
            "title": "جيد جداً!",
            "message": "أحسنت! قراءة جيدة مع بعض التحسينات البسيطة.",
            "color": "blue",
            "suggestion": "راجع الكلمات التي بها أخطاء صغيرة"
        }
    elif score >= 70:
        return {
            "emoji": "👍",
            "title": "جيد!",
            "message": "بداية جيدة، لكن هناك بعض الأخطاء.",
            "color": "orange",
            "suggestion": "ركز على التجويد والمخارج"
        }
    elif score >= 50:
        return {
            "emoji": "😊",
            "title": "لا بأس!",
            "message": "قراءة جيدة! تحتاج إلى المزيد من التدريب.",
            "color": "yellow",
            "suggestion": "استمع للتسجيل النموذجي وحاول مرة أخرى"
        }
    else:
        return {
            "emoji": "💪",
            "title": "حاول مرة أخرى!",
            "message": "لا تستسلم! التعلم يحتاج إلى صبر.",
            "color": "red",
            "suggestion": "استمع جيداً للتسجيل واقرأ ببطء"
        }


def is_gemini_available() -> bool:
    """
    Check if Gemini AI is available and configured

    Returns:
        bool: True if Gemini is available, False otherwise
    """
    return USE_GEMINI and _gemini_model is not None


def get_feedback_system_info() -> dict:
    """
    Get information about the feedback system configuration

    Returns:
        dict: System configuration details
    """
    return {
        "gemini_enabled": USE_GEMINI,
        "gemini_available": is_gemini_available(),
        "gemini_model": settings.GEMINI_MODEL if USE_GEMINI else None,
        "fallback_mode": not is_gemini_available()
    }
