from rfp_automation import rank, score_proposal

from .conftest import STRONG, WEAK


def test_strong_proposal_scores_higher(brief):
    strong = score_proposal(brief, "قوي", STRONG)
    weak = score_proposal(brief, "ضعيف", WEAK)
    assert strong.total > weak.total


def test_missing_mandatory_requirement_is_flagged(brief):
    weak = score_proposal(brief, "ضعيف", WEAK)
    assert "R1" in weak.missing_mandatory


def test_hedging_reduces_score(brief):
    hedged = STRONG.replace("نقدم لوحة تعرض زمن المعالجة وعدد المراسلات.",
                            "لوحة تعرض زمن المعالجة وعدد المراسلات خارج النطاق ويمكن توفيرها لاحقا.")
    assert score_proposal(brief, "v", hedged).total < score_proposal(brief, "v", STRONG).total


def test_every_criterion_is_reported_with_evidence_field(brief):
    card = score_proposal(brief, "قوي", STRONG)
    assert len(card.criteria) == len(brief.requirements)
    assert all(0.0 <= c.coverage <= 1.0 for c in card.criteria)


def test_rank_orders_by_total(brief):
    cards = [score_proposal(brief, "ضعيف", WEAK), score_proposal(brief, "قوي", STRONG)]
    assert rank(cards)[0].vendor == "قوي"
