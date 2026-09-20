import pytest
from pact_core import stats


def test_wilson_reference_values():
    assert stats.wilson(0, 20) == pytest.approx((0.0, 0.0, 0.1611), abs=0.0001)
    assert stats.wilson(19, 20) == pytest.approx((0.95, 0.7639, 0.9911), abs=0.0001)
    assert stats.wilson(15, 90) == pytest.approx((0.1667, 0.1037, 0.2569), abs=0.0001)
    assert stats.wilson(0, 0) == (0.0, 0.0, 0.0)


def test_summarize_orders_fixed_then_agent_cohorts():
    items = [
        {"cohort": "agent:z:k4", "attempts": 1, "passes": 0, "roundsCorrect": 1, "roundsTotal": 3},
        {"cohort": "local", "attempts": 1, "passes": 1, "roundsCorrect": 3, "roundsTotal": 3},
        {"cohort": "study", "attempts": 1, "passes": 1, "roundsCorrect": 3, "roundsTotal": 3},
        {"cohort": "public", "attempts": 1, "passes": 0, "roundsCorrect": 0, "roundsTotal": 3},
    ]
    assert [item["cohort"] for item in stats.summarize(items)] == ["study", "public", "local", "agent:z:k4"]
