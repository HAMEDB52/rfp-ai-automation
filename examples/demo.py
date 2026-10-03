"""عرض كامل: موجز العميل ← مستند RFP ← تقييم ثلاثة عروض ← تقرير."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rfp_automation import ProjectBrief, run  # noqa: E402

state = run(
    ProjectBrief.from_json(ROOT / "data" / "brief.json"),
    str(ROOT / "data" / "proposals"),
    str(ROOT / "out"),
)

print("المسار المنفَّذ:", " ← ".join(state["trace"]), "\n")
print("الترتيب النهائي:")
for i, card in enumerate(state["scorecards"], 1):
    missing = "، ".join(card.missing_mandatory) or "لا يوجد"
    print(f"  {i}. {card.vendor:<26} {card.total:6.2f}   مفقود إلزامي: {missing}")
print(f"\nالمخرجات في: {ROOT / 'out'}")
