from rfp_automation import build_rfp


def test_rfp_contains_all_required_sections(brief):
    md = build_rfp(brief).to_markdown()
    for heading in ["نطاق العمل", "المتطلبات التفصيلية", "معايير التقييم",
                    "الميزانية والمدة", "تعليمات تقديم العرض"]:
        assert heading in md


def test_every_requirement_appears_in_document(brief):
    md = build_rfp(brief).to_markdown()
    for req in brief.requirements:
        assert req.id in md and req.title in md


def test_budget_is_formatted(brief):
    assert "500,000" in build_rfp(brief).to_markdown()
