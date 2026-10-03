"""تقييم العروض مقابل متطلبات طلب العرض.

المنطق مقصود أن يكون قابلاً للتفسير: لكل متطلب نسبة تغطية ودليل نصي،
بحيث يستطيع المراجع البشري مراجعة الدرجة لا قبولها على عِلّاتها.
"""
from __future__ import annotations

from .arabic_text import coverage, keywords, normalize
from .schema import CriterionScore, ProjectBrief, ScoreCard

# صيغ تدل على التزام صريح بالتنفيذ
COMMITMENT = ("نلتزم", "سننفذ", "نوفر", "يشمل", "نقدم", "تم تنفيذ", "لدينا", "ندعم", "نضمن")
# صيغ تدل على تحفّظ أو استثناء
HEDGING = ("خارج النطاق", "غير مشمول", "لاحقا", "عند الطلب", "اختياري", "مقابل رسوم اضافيه")


def _best_evidence(requirement_text: str, text: str, window: int = 220) -> tuple[str, float]:
    """اختيار أقرب فقرة تدعم المتطلب مع نسبة تغطيتها."""
    best, best_score = "", 0.0
    for para in [p.strip() for p in text.split("\n") if p.strip()]:
        score = coverage(requirement_text, para)
        if score > best_score:
            best, best_score = para[:window], score
    return best, best_score


def score_proposal(brief: ProjectBrief, vendor: str, text: str) -> ScoreCard:
    normalized = normalize(text)
    criteria: list[CriterionScore] = []
    missing: list[str] = []
    notes: list[str] = []

    for req in brief.requirements:
        doc_cov = coverage(req.text(), text)
        evidence, para_cov = _best_evidence(req.text(), text)
        cov = max(doc_cov, para_cov)
        if para_cov < 0.34:
            evidence = ""   # لا دليل مقنع — أفضل من عرض سطر عشوائي

        score = cov
        if any(word in normalized for word in map(normalize, COMMITMENT)) and cov >= 0.5:
            score = min(1.0, score + 0.1)       # التزام صريح يرفع الثقة
        if evidence and any(h in normalize(evidence) for h in map(normalize, HEDGING)):
            score *= 0.5                         # تحفّظ صريح يخفض الدرجة
            notes.append(f"تحفّظ على المتطلب {req.id}")

        criteria.append(
            CriterionScore(
                requirement_id=req.id,
                title=req.title,
                weight=req.weight,
                coverage=round(cov, 3),
                score=round(score, 3),
                evidence=evidence,
                mandatory=req.mandatory,
            )
        )
        if req.mandatory and cov < 0.34:
            missing.append(req.id)

    total_weight = sum(c.weight for c in criteria) or 1.0
    total = sum(c.score * c.weight for c in criteria) / total_weight
    if missing:
        total *= 0.6                             # عقوبة إغفال متطلب إلزامي
        notes.append("إغفال متطلبات إلزامية: " + "، ".join(missing))

    return ScoreCard(vendor=vendor, criteria=criteria, total=round(total * 100, 2),
                     missing_mandatory=missing, notes=notes)


def rank(scorecards: list[ScoreCard]) -> list[ScoreCard]:
    return sorted(scorecards, key=lambda s: (-s.total, len(s.missing_mandatory)))
