"""نماذج البيانات لدورة طلب العروض."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Requirement:
    id: str
    title: str
    description: str
    category: str = "عام"
    weight: float = 1.0
    mandatory: bool = True

    def text(self) -> str:
        return f"{self.title} {self.description}"


@dataclass
class ProjectBrief:
    """مدخلات العميل — نقطة البداية لكل شيء."""

    project_name: str
    organization: str
    summary: str
    requirements: list[Requirement]
    budget_sar: float | None = None
    duration_weeks: int | None = None
    contact: str = ""
    submission_deadline: str = ""

    @classmethod
    def from_json(cls, path: str | Path) -> "ProjectBrief":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        raw["requirements"] = [Requirement(**r) for r in raw.get("requirements", [])]
        return cls(**raw)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Section:
    heading: str
    body: str


@dataclass
class RFPDocument:
    brief: ProjectBrief
    sections: list[Section]

    def to_markdown(self) -> str:
        lines = [f"# طلب عرض فني ومالي — {self.brief.project_name}", ""]
        for s in self.sections:
            lines += [f"## {s.heading}", "", s.body, ""]
        return "\n".join(lines)


@dataclass
class CriterionScore:
    requirement_id: str
    title: str
    weight: float
    coverage: float
    score: float
    evidence: str = ""
    mandatory: bool = True


@dataclass
class ScoreCard:
    vendor: str
    criteria: list[CriterionScore]
    total: float
    missing_mandatory: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
