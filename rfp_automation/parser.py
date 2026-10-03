"""قراءة عروض المورّدين من PDF أو نص وتقطيعها إلى أقسام."""
from __future__ import annotations

import re
from pathlib import Path

HEADING = re.compile(r"^\s{0,3}(?:#{1,6}\s+|\d+[.)]\s+|[-•]\s+)?(.{3,80})\s*$")


def read_text(path: str | Path) -> str:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        import pdfplumber

        with pdfplumber.open(str(path)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return path.read_text(encoding="utf-8")


def split_sections(text: str) -> dict[str, str]:
    """تقسيم العرض إلى أقسام بعناوينها — يتعامل مع ترقيم ماركداون والعناوين المرقّمة."""
    sections: dict[str, str] = {}
    current = "مقدمة"
    buf: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        is_heading = bool(stripped) and (
            stripped.startswith("#")
            or re.match(r"^\d+[.)]\s+\S", stripped)
            or (len(stripped) < 60 and stripped.endswith(":"))
        )
        if is_heading:
            if buf:
                sections[current] = "\n".join(buf).strip()
                buf = []
            current = stripped.lstrip("#").strip().rstrip(":")
        else:
            buf.append(line)
    if buf:
        sections[current] = "\n".join(buf).strip()
    return {k: v for k, v in sections.items() if v}


def load_proposal(path: str | Path) -> tuple[str, str, dict[str, str]]:
    """إرجاع (اسم المورّد، النص الكامل، الأقسام). الاسم يُشتق من اسم الملف."""
    text = read_text(path)
    return Path(path).stem, text, split_sections(text)
