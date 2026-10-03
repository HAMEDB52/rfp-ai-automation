"""rfp-ai-automation — أتمتة إعداد طلبات العروض (RFP) وتقييم عروض المورّدين."""

from .generator import build_rfp
from .graph import END, StateGraph
from .parser import load_proposal, split_sections
from .report import to_json, to_markdown, to_pdf
from .schema import CriterionScore, ProjectBrief, Requirement, RFPDocument, ScoreCard, Section
from .scoring import rank, score_proposal
from .workflow import build_workflow, run

__version__ = "0.1.0"
__all__ = ["CriterionScore", "END", "ProjectBrief", "RFPDocument", "Requirement", "ScoreCard",
           "Section", "StateGraph", "build_rfp", "build_workflow", "load_proposal", "rank",
           "run", "score_proposal", "split_sections", "to_json", "to_markdown", "to_pdf"]
