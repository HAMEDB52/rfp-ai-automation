"""توليد مستند طلب العروض من موجز العميل."""
from __future__ import annotations

from .schema import ProjectBrief, RFPDocument, Section


def _requirements_table(brief: ProjectBrief) -> str:
    rows = ["| الرقم | المتطلب | التصنيف | الوزن | إلزامي |",
            "|---|---|---|---|---|"]
    for r in brief.requirements:
        rows.append(f"| {r.id} | {r.title} | {r.category} | {r.weight:g} | "
                    f"{'نعم' if r.mandatory else 'لا'} |")
    details = "\n\n".join(f"**{r.id} — {r.title}**\n\n{r.description}" for r in brief.requirements)
    return "\n".join(rows) + "\n\n" + details


def build_rfp(brief: ProjectBrief) -> RFPDocument:
    """بناء مستند RFP كامل بأقسامه المعيارية."""
    budget = f"{brief.budget_sar:,.0f} ريال سعودي" if brief.budget_sar else "يُحدَّد في العرض المالي"
    duration = f"{brief.duration_weeks} أسبوعاً" if brief.duration_weeks else "يُقترح من المورّد"
    total_weight = sum(r.weight for r in brief.requirements) or 1.0

    sections = [
        Section("نبذة عن الجهة والمشروع",
                f"الجهة الطالبة: {brief.organization}\n\n{brief.summary}"),
        Section("نطاق العمل",
                "يشمل نطاق العمل تنفيذ المتطلبات الواردة في جدول المتطلبات أدناه، "
                "وتسليم المخرجات موثّقة وقابلة للتشغيل في بيئة الجهة، "
                "مع نقل المعرفة وتدريب الفريق التشغيلي."),
        Section("المتطلبات التفصيلية", _requirements_table(brief)),
        Section("معايير التقييم",
                "تُقيَّم العروض وفق أوزان المتطلبات أعلاه (مجموع الأوزان "
                f"{total_weight:g}). ويُستبعد العرض الذي يغفل أي متطلب إلزامي.\n\n"
                "| المحور | الوزن |\n|---|---|\n"
                "| المطابقة الفنية للمتطلبات | 60% |\n"
                "| الخبرة والمشاريع المماثلة | 20% |\n"
                "| الجدول الزمني وخطة التنفيذ | 10% |\n"
                "| العرض المالي | 10% |"),
        Section("الميزانية والمدة", f"الميزانية التقديرية: {budget}\n\nالمدة المتوقعة: {duration}"),
        Section("تعليمات تقديم العرض",
                f"يُقدَّم العرض الفني والمالي في ملفين منفصلين قبل "
                f"{brief.submission_deadline or 'الموعد المعلن'}، "
                f"ويُرسل إلى {brief.contact or 'جهة الاتصال المعتمدة'}. "
                "ويجب أن يعالج العرض الفني كل متطلب برقمه الوارد في الجدول."),
    ]
    return RFPDocument(brief=brief, sections=sections)
