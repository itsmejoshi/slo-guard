"""Core SLO and error-budget math.

Implements the error-budget model described in the Google SRE Workbook
("Implementing SLOs" and "Alerting on SLOs" chapters): an SLO defines an
acceptable ratio of bad events over a rolling period; the error budget is
the complementary "allowance" of bad events; and burn rate measures how
quickly that allowance is being consumed relative to a uniform, budget-neutral
pace.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SLO:
    """A single Service Level Objective.

    Attributes:
        name: Human-readable identifier, e.g. "checkout-availability".
        target: The objective as a fraction, e.g. 0.999 for "99.9%".
        period_days: Rolling compliance window in days (commonly 28 or 30).
    """

    name: str
    target: float
    period_days: int = 30

    def __post_init__(self) -> None:
        if not (0 < self.target < 1):
            raise ValueError(f"target must be between 0 and 1, got {self.target}")
        if self.period_days <= 0:
            raise ValueError(f"period_days must be positive, got {self.period_days}")

    @property
    def error_budget(self) -> float:
        """Fraction of events allowed to be 'bad' over the period."""
        return 1.0 - self.target

    def budget_consumed(self, bad_event_ratio: float) -> float:
        """Fraction of the total error budget consumed so far.

        Args:
            bad_event_ratio: Observed ratio of bad events over the period
                (e.g. 5xx responses / total responses), between 0 and 1.

        Returns:
            0.0 means no budget spent; 1.0 means the budget is exhausted;
            values above 1.0 mean the SLO has already been violated.
        """
        if not (0 <= bad_event_ratio <= 1):
            raise ValueError("bad_event_ratio must be between 0 and 1")
        return bad_event_ratio / self.error_budget

    def budget_remaining(self, bad_event_ratio: float) -> float:
        """Fraction of error budget remaining (can go negative if exhausted)."""
        return 1.0 - self.budget_consumed(bad_event_ratio)

    def budget_remaining_minutes(self, bad_event_ratio: float) -> float:
        """Convenience: remaining budget expressed in minutes of the period."""
        total_minutes = self.period_days * 24 * 60
        return self.budget_remaining(bad_event_ratio) * total_minutes
