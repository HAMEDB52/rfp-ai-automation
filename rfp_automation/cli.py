"""rfp-automation — توليد مستند RFP وتقييم العروض من سطر الأوامر."""
from __future__ import annotations

import argparse
import sys

from .schema import ProjectBrief
from .workflow import run


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rfp-automation",
                                description="أتمتة إعداد طلبات العروض وتقييمها")
    p.add_argument("--brief", required=True, help="ملف JSON لموجز المشروع")
    p.add_argument("--proposals", help="مجلد عروض المورّدين (txt/md/pdf)")
    p.add_argument("--out", default="out", help="مجلد المخرجات")
    p.add_argument("--pdf", action="store_true", help="توليد نسخة PDF (يتطلب playwright)")
    args = p.parse_args(argv)

    state = run(ProjectBrief.from_json(args.brief), args.proposals, args.out, args.pdf)
    print(f"المسار المنفَّذ: {' → '.join(state['trace'])}", file=sys.stderr)
    print(f"مستند RFP: {state.get('rfp_path')}", file=sys.stderr)
    for card in state.get("scorecards", []):
        print(f"  {card.vendor:<28} {card.total:6.2f}"
              f"{'  (ينقصه: ' + '، '.join(card.missing_mandatory) + ')' if card.missing_mandatory else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
