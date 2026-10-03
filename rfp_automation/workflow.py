"""سير العمل الكامل كرسم بياني للحالة: موجز ← RFP ← عروض ← تقييم ← تقرير."""
from __future__ import annotations

from pathlib import Path

from .generator import build_rfp
from .graph import END, StateGraph
from .parser import load_proposal
from .report import to_json, to_markdown, to_pdf
from .scoring import rank, score_proposal
from .schema import ProjectBrief


def node_generate_rfp(state: dict) -> dict:
    brief: ProjectBrief = state["brief"]
    rfp = build_rfp(brief)
    state["rfp"] = rfp
    out = Path(state["output_dir"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "rfp.md").write_text(rfp.to_markdown(), encoding="utf-8")
    state["rfp_path"] = str(out / "rfp.md")
    return state


def node_load_proposals(state: dict) -> dict:
    proposals = []
    directory = state.get("proposals_dir")
    if directory and Path(directory).is_dir():
        for path in sorted(Path(directory).iterdir()):
            if path.suffix.lower() in {".txt", ".md", ".pdf"}:
                vendor, text, sections = load_proposal(path)
                proposals.append({"vendor": vendor, "text": text, "sections": sections})
    state["proposals"] = proposals
    return state


def node_score(state: dict) -> dict:
    brief: ProjectBrief = state["brief"]
    state["scorecards"] = rank(
        [score_proposal(brief, p["vendor"], p["text"]) for p in state["proposals"]]
    )
    return state


def node_report(state: dict) -> dict:
    out = Path(state["output_dir"])
    cards = state["scorecards"]
    markdown = to_markdown(cards)
    (out / "evaluation.md").write_text(markdown, encoding="utf-8")
    to_json(cards, out / "evaluation.json")
    if state.get("pdf"):
        state["pdf_path"] = str(to_pdf(markdown, out / "evaluation.pdf") or "")
    state["report_markdown"] = markdown
    return state


def node_no_proposals(state: dict) -> dict:
    state["report_markdown"] = "لم يتم العثور على عروض لتقييمها — تم توليد مستند RFP فقط."
    return state


def route_after_load(state: dict) -> str:
    return "score" if state.get("proposals") else "no_proposals"


def build_workflow() -> StateGraph:
    graph = StateGraph()
    graph.add_node("generate_rfp", node_generate_rfp)
    graph.add_node("load_proposals", node_load_proposals)
    graph.add_node("score", node_score)
    graph.add_node("report", node_report)
    graph.add_node("no_proposals", node_no_proposals)

    graph.set_entry("generate_rfp")
    graph.add_edge("generate_rfp", "load_proposals")
    graph.add_conditional_edge("load_proposals", route_after_load)
    graph.add_edge("score", "report")
    graph.add_edge("report", END)
    graph.add_edge("no_proposals", END)
    return graph


def run(brief: ProjectBrief, proposals_dir: str | None, output_dir: str = "out",
        pdf: bool = False) -> dict:
    graph = build_workflow()
    state = graph.run({"brief": brief, "proposals_dir": proposals_dir,
                       "output_dir": output_dir, "pdf": pdf})
    state["trace"] = graph.trace
    return state
