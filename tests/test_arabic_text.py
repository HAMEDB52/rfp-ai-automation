from rfp_automation.arabic_text import coverage, keywords, normalize


def test_normalize_unifies_forms():
    assert normalize("الإجازةُ") == normalize("الاجازه")
    assert normalize("٢٠٢٦") == "2026"


def test_keywords_ignore_definite_article():
    assert keywords("المراسلات") & keywords("مراسلات")


def test_coverage_is_fraction_between_zero_and_one():
    req = "استخراج النصوص العربية من المستندات الممسوحة ضوئياً"
    assert coverage(req, "نستخرج النصوص العربية من المستندات الممسوحة ضوئياً") > 0.8
    assert coverage(req, "نقدم خدمات تصميم الجرافيك") < 0.2
    assert 0.0 <= coverage(req, "") <= 1.0
