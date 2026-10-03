"""مخرجات التقييم: JSON منظّم، تقرير ماركداون، و PDF اختياري."""
from __future__ import annotations

import json
from pathlib import Path

from .schema import ScoreCard


def to_json(scorecards: list[ScoreCard], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "vendors": [s.to_dict() for s in scorecards],
        "winner": scorecards[0].vendor if scorecards else None,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def to_markdown(scorecards: list[ScoreCard]) -> str:
    lines = ["# تقرير تقييم العروض", "", "## الترتيب النهائي", "",
             "| # | المورّد | الدرجة | متطلبات إلزامية مفقودة |", "|---|---|---|---|"]
    for i, s in enumerate(scorecards, 1):
        lines.append(f"| {i} | {s.vendor} | {s.total:.2f} | "
                     f"{'، '.join(s.missing_mandatory) or 'لا يوجد'} |")

    for s in scorecards:
        lines += ["", f"## تفصيل: {s.vendor}", "",
                  "| المتطلب | الوزن | التغطية | الدرجة | الدليل |", "|---|---|---|---|---|"]
        for c in s.criteria:
            evidence = (c.evidence[:90] + "…") if len(c.evidence) > 90 else (c.evidence or "—")
            lines.append(f"| {c.requirement_id} {c.title} | {c.weight:g} | "
                         f"{c.coverage:.0%} | {c.score:.2f} | {evidence} |")
        if s.notes:
            lines += ["", "**ملاحظات:** " + "؛ ".join(s.notes)]
    return "\n".join(lines)


def to_pdf(markdown_text: str, path: str | Path, *, title: str = "تقرير") -> Path | None:
    """تحويل إلى PDF عبر متصفح Chromium — يدعم العربية بشكل صحيح.

    يعيد None إن لم تكن playwright متاحة، فيبقى مخرج الماركداون هو المرجع.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    html = _markdown_to_html(markdown_text, title)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".html")
    tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(tmp.resolve().as_uri())
        page.pdf(path=str(path), format="A4", margin={"top": "18mm", "bottom": "18mm",
                                                      "left": "15mm", "right": "15mm"})
        browser.close()
    return path


def _markdown_to_html(md: str, title: str) -> str:
    body, in_table = [], False
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if not in_table:
                body.append("<table>")
                in_table = True
            tag = "th" if len(body) and body[-1] == "<table>" else "td"
            body.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            body.append("</table>")
            in_table = False
        if line.startswith("## "):
            body.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{line[2:]}</h1>")
        elif line.strip():
            body.append(f"<p>{line}</p>")
    if in_table:
        body.append("</table>")
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>{title}</title><style>
body{{font-family:'IBM Plex Sans Arabic','Noto Kufi Arabic',sans-serif;line-height:1.8;color:#111;padding:0 8px}}
h1{{font-size:22pt;border-bottom:2px solid #2563eb;padding-bottom:6px}}
h2{{font-size:15pt;margin-top:22px;color:#1e3a8a}}
table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:10pt}}
th,td{{border:1px solid #cbd5e1;padding:6px 8px;text-align:right;vertical-align:top}}
th{{background:#eff6ff}}
</style></head><body>{''.join(body)}</body></html>"""
