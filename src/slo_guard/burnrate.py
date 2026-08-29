"""Multi-window, multi-burn-rate alert threshold calculations.

Based on the technique described in the Google SRE Workbook chapter
"Alerting on SLOs": rather than alerting on raw error ratio, alert on the
*rate* at which the error budget is being burned relative to a constant,
budget-neutral pace over the SLO period. A short window catches fast burns
quickly; a long window (paired with the same threshold) filters out noise
from brief blips, so both must fire together for a page-worthy alert.

This module computes the burn-rate threshold for an arbitrary window size
and SLO period from first principles, rather than hard-coding the constants
(14.4, 6, 1, ...) that appear in the workbook for the 99.9%/30-day case --
those fall out of this formula automatically.
"""
from __future__ import annotations

from dataclasses import dataclass

from .core import SLO


@dataclass(frozen=True)
class BurnRateWindow:
    """One entry in a multi-window alerting policy.

    Attributes:
        name: Short label, e.g. "fast", "medium", "slow".
        long_window_hours: The long lookback window, in hours.
        short_window_hours: The short lookback window, in hours (used to
            confirm the alert has not already recovered).
        budget_fraction: Fraction of the *total* error budget this window is
            allowed to consume before paging, e.g. 0.02 for "2% of budget".
        for_duration_minutes: How long the condition must hold before firing,
            to suppress flapping.
        severity: Free-text severity label, e.g. "page" or "ticket".
    """

    name: str
    long_window_hours: float
    short_window_hours: float
    budget_fraction: float
    for_duration_minutes: float
    severity: str = "page"

    def burn_rate_threshold(self, slo: SLO) -> float:
        """The burn-rate multiplier that exhausts `budget_fraction` of the
        error budget in exactly `long_window_hours`.

        burn_rate = budget_fraction / (long_window / period)

        A burn rate of 1.0 means "consuming the budget at exactly the
        uniform pace needed to exhaust it right at the end of the period".
        A burn rate of 14.4 means consuming it 14.4x faster than that.
        """
        period_hours = slo.period_days * 24
        window_fraction_of_period = self.long_window_hours / period_hours
        return self.budget_fraction / window_fraction_of_period


# The canonical 3-window policy from the SRE Workbook, generalized so it
# still produces the well-known 14.4 / 6 / 1 multipliers for a 99.9%/30-day
# SLO, but adapts correctly to any other target or period.
DEFAULT_POLICY: tuple[BurnRateWindow, ...] = (
    BurnRateWindow(
        name="fast",
        long_window_hours=1,
        short_window_hours=5 / 60,
        budget_fraction=0.02,
        for_duration_minutes=2,
        severity="page",
    ),
    BurnRateWindow(
        name="medium",
        long_window_hours=6,
        short_window_hours=0.5,
        budget_fraction=0.05,
        for_duration_minutes=15,
        severity="page",
    ),
    BurnRateWindow(
        name="slow",
        long_window_hours=72,
        short_window_hours=6,
        budget_fraction=0.10,
        for_duration_minutes=60,
        severity="ticket",
    ),
)


def evaluate_policy(
    slo: SLO, policy: tuple[BurnRateWindow, ...] = DEFAULT_POLICY
) -> list[dict]:
    """Resolve a policy into concrete thresholds for a given SLO.

    Returns a list of dicts (one per window) ready to feed into a rules
    generator or to print as a report.
    """
    results = []
    for window in policy:
        results.append(
            {
                "name": window.name,
                "long_window_hours": window.long_window_hours,
                "short_window_hours": window.short_window_hours,
                "burn_rate_threshold": window.burn_rate_threshold(slo),
                "for_duration_minutes": window.for_duration_minutes,
                "severity": window.severity,
            }
        )
    return results
