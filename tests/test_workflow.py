import json

from rfp_automation import run
from rfp_automation.parser import split_sections

from .conftest import STRONG, WEAK


def test_full_workflow_produces_reports(brief, tmp_path):
    proposals = tmp_path / "proposals"
    proposals.mkdir()
    (proposals / "قوي.md").write_text(STRONG, encoding="utf-8")
    (proposals / "ضعيف.md").write_text(WEAK, encoding="utf-8")

    out = tmp_path / "out"
    state = run(brief, str(proposals), str(out))

    assert state["trace"] == ["generate_rfp", "load_proposals", "score", "report"]
    assert (out / "rfp.md").exists()
    assert (out / "evaluation.md").exists()
    payload = json.loads((out / "evaluation.json").read_text(encoding="utf-8"))
    assert payload["winner"] == "قوي"
    assert len(payload["vendors"]) == 2


def test_workflow_without_proposals_takes_fallback_branch(brief, tmp_path):
    state = run(brief, None, str(tmp_path / "out"))
    assert state["trace"] == ["generate_rfp", "load_proposals", "no_proposals"]
    assert "لم يتم العثور" in state["report_markdown"]


def test_split_sections_detects_numbered_headings():
    sections = split_sections(STRONG)
    assert any("تصنيف المراسلات" in k for k in sections)


def test_markdown_bold_is_rendered_not_printed_raw():
    from rfp_automation.report import _markdown_to_html

    out = _markdown_to_html("**ملاحظات:** إغفال R5\n| أ | ب |\n|---|---|\n| **x** | <y> |", "t")
    assert "<strong>ملاحظات:</strong>" in out and "**" not in out
    assert "&lt;y&gt;" in out


def test_pdf_is_skipped_when_chromium_is_missing(monkeypatch, tmp_path, capsys):
    import playwright.sync_api as pw_api

    from rfp_automation.report import to_pdf

    class _Launcher:
        def launch(self):
            raise pw_api.Error("BrowserType.launch: Executable doesn't exist at /x")

    class _PW:
        chromium = _Launcher()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    monkeypatch.setattr(pw_api, "sync_playwright", lambda: _PW())
    assert to_pdf("# t", tmp_path / "r.pdf") is None
    assert "playwright install chromium" in capsys.readouterr().err
