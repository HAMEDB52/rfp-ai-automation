"""أدوات نص عربي خفيفة — مكتفية ذاتياً بلا اعتماديات."""
from __future__ import annotations

import re
import unicodedata

_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭ]")
_ALEF = re.compile(r"[آأإٱ]")
_YA = re.compile(r"[ىی]")
_SPACES = re.compile(r"\s+")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

_PREFIXES = ("وال", "فال", "بال", "كال", "لل", "ال", "و", "ب", "ك", "ل")
_SUFFIXES = ("اتها", "ات", "ون", "ين", "ان", "ية", "يه", "ها", "ه", "ة", "ي")

STOPWORDS = {"في", "من", "على", "الى", "إلى", "عن", "مع", "هذا", "التي", "الذي",
             "ما", "لا", "ان", "أن", "كان", "هو", "هي", "قد", "او", "أو", "و", "كل"}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").translate(_DIGITS)
    text = _DIACRITICS.sub("", text).replace("ـ", "")
    text = _ALEF.sub("ا", text)
    text = _YA.sub("ي", text)
    text = text.replace("ة", "ه")
    return _SPACES.sub(" ", text).strip()


def stem(token: str, min_len: int = 3) -> str:
    if len(token) <= min_len:
        return token
    for p in _PREFIXES:
        if token.startswith(p) and len(token) - len(p) >= min_len:
            token = token[len(p):]
            break
    for s in _SUFFIXES:
        if token.endswith(s) and len(token) - len(s) >= min_len:
            token = token[: -len(s)]
            break
    return token


def keywords(text: str) -> set[str]:
    """مفاتيح المطابقة: كلمات مطبّعة مجذّرة بلا كلمات وقف."""
    tokens = [t for t in re.split(r"[^\w؀-ۿ]+", normalize(text)) if t]
    content = [t for t in tokens if t not in STOPWORDS] or tokens
    return {stem(t) for t in content}


def coverage(requirement: str, text: str) -> float:
    """نسبة مفاتيح المتطلب الظاهرة في النص — مقياس تغطية بسيط وقابل للتفسير."""
    need = keywords(requirement)
    if not need:
        return 0.0
    return len(need & keywords(text)) / len(need)
