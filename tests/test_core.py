import pytest

from slo_guard.core import SLO


def test_error_budget():
    slo = SLO(name="test", target=0.999, period_days=30)
    assert slo.error_budget == pytest.approx(0.001)


def test_budget_consumed_half():
    slo = SLO(name="test", target=0.999, period_days=30)
    # Half the budget: bad ratio = error_budget / 2
    assert slo.budget_consumed(0.0005) == pytest.approx(0.5)


def test_budget_remaining():
    slo = SLO(name="test", target=0.99, period_days=30)
    assert slo.budget_remaining(0.0) == pytest.approx(1.0)
    assert slo.budget_remaining(0.01) == pytest.approx(0.0)


def test_budget_exhausted_goes_negative():
    slo = SLO(name="test", target=0.99, period_days=30)
    assert slo.budget_remaining(0.02) < 0


def test_budget_remaining_minutes():
    slo = SLO(name="test", target=0.999, period_days=30)
    total_minutes = 30 * 24 * 60
    assert slo.budget_remaining_minutes(0.0) == pytest.approx(total_minutes)


@pytest.mark.parametrize("bad_ratio", [-0.1, 1.1])
def test_invalid_bad_ratio_raises(bad_ratio):
    slo = SLO(name="test", target=0.999)
    with pytest.raises(ValueError):
        slo.budget_consumed(bad_ratio)


@pytest.mark.parametrize("target", [0.0, 1.0, -0.5, 1.5])
def test_invalid_target_raises(target):
    with pytest.raises(ValueError):
        SLO(name="test", target=target)


def test_invalid_period_raises():
    with pytest.raises(ValueError):
        SLO(name="test", target=0.99, period_days=0)
