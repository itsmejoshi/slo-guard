import pytest

from slo_guard.burnrate import DEFAULT_POLICY, evaluate_policy
from slo_guard.core import SLO


def test_default_policy_matches_known_constants_for_999_30d():
    """For a 99.9% / 30-day SLO, the default policy should reproduce the
    well-known 14.4 / 6 / 1 burn-rate multipliers from the Google SRE
    Workbook's 'Alerting on SLOs' chapter."""
    slo = SLO(name="checkout", target=0.999, period_days=30)
    results = {r["name"]: r["burn_rate_threshold"] for r in evaluate_policy(slo)}

    assert results["fast"] == pytest.approx(14.4, rel=1e-9)
    assert results["medium"] == pytest.approx(6.0, rel=1e-9)
    assert results["slow"] == pytest.approx(1.0, rel=1e-9)


def test_burn_rate_scales_with_different_period():
    """A 90-day period should scale burn-rate thresholds proportionally
    (same budget fraction consumed in the same window is a faster burn
    relative to a longer total period)."""
    slo_30 = SLO(name="a", target=0.999, period_days=30)
    slo_90 = SLO(name="b", target=0.999, period_days=90)

    fast_30 = evaluate_policy(slo_30)[0]["burn_rate_threshold"]
    fast_90 = evaluate_policy(slo_90)[0]["burn_rate_threshold"]

    assert fast_90 == pytest.approx(fast_30 * 3, rel=1e-9)


def test_burn_rate_scales_with_different_target():
    """A looser target (larger error budget) means the same window burns a
    smaller fraction of a bigger budget for the same multiplier -- so at a
    fixed budget_fraction, the multiplier itself is independent of target;
    it only depends on window/period. This test locks in that invariant."""
    slo_tight = SLO(name="tight", target=0.999, period_days=30)
    slo_loose = SLO(name="loose", target=0.99, period_days=30)

    thresholds_tight = [r["burn_rate_threshold"] for r in evaluate_policy(slo_tight)]
    thresholds_loose = [r["burn_rate_threshold"] for r in evaluate_policy(slo_loose)]

    assert thresholds_tight == pytest.approx(thresholds_loose)


def test_policy_windows_ordered_fast_to_slow():
    windows = [w.long_window_hours for w in DEFAULT_POLICY]
    assert windows == sorted(windows)


def test_evaluate_policy_returns_all_fields():
    slo = SLO(name="x", target=0.995, period_days=28)
    results = evaluate_policy(slo)
    assert len(results) == len(DEFAULT_POLICY)
    for r in results:
        assert set(r.keys()) == {
            "name",
            "long_window_hours",
            "short_window_hours",
            "burn_rate_threshold",
            "for_duration_minutes",
            "severity",
        }
