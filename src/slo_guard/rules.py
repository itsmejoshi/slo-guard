"""Render burn-rate policies as Prometheus alerting rule YAML."""
from __future__ import annotations

from typing import Any

import yaml

from .burnrate import DEFAULT_POLICY, BurnRateWindow, evaluate_policy
from .core import SLO


def _hours_to_promql_duration(hours: float) -> str:
    """Format an hour count as a Prometheus duration string."""
    if hours < 1:
        minutes = round(hours * 60)
        return f"{minutes}m"
    if hours == int(hours):
        return f"{int(hours)}h"
    return f"{hours}h"


def _ratio_expr(window_str: str, error_selector: str, total_selector: str) -> str:
    """Build a PromQL expression for the bad-event ratio over a window."""
    return (
        f"(sum(rate({error_selector}[{window_str}])) / "
        f"sum(rate({total_selector}[{window_str}])))"
    )


def build_alert_group(
    slo: SLO,
    error_selector: str,
    total_selector: str,
    policy: tuple[BurnRateWindow, ...] = DEFAULT_POLICY,
    extra_labels: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a single Prometheus rule group for an SLO's burn-rate alerts.

    Args:
        slo: The SLO the alerts protect.
        error_selector: PromQL selector for "bad" events, e.g.
            'http_requests_total{job="checkout",code=~"5.."}'.
        total_selector: PromQL selector for all events, e.g.
            'http_requests_total{job="checkout"}'.
        policy: The burn-rate windows to alert on.
        extra_labels: Additional labels merged into every alert rule.
    """
    thresholds = evaluate_policy(slo, policy)
    rules = []
    for window, threshold in zip(policy, thresholds):
        long_w = _hours_to_promql_duration(window.long_window_hours)
        short_w = _hours_to_promql_duration(window.short_window_hours)
        long_expr = _ratio_expr(long_w, error_selector, total_selector)
        short_expr = _ratio_expr(short_w, error_selector, total_selector)
        burn_threshold = threshold["burn_rate_threshold"] * slo.error_budget

        expr = f"{long_expr} > {burn_threshold:.6g} and {short_expr} > {burn_threshold:.6g}"

        labels = {"severity": window.severity, "slo": slo.name}
        if extra_labels:
            labels.update(extra_labels)

        rules.append(
            {
                "alert": f"{slo.name}_burn_rate_{window.name}",
                "expr": expr,
                "for": f"{int(window.for_duration_minutes)}m",
                "labels": labels,
                "annotations": {
                    "summary": (
                        f"{slo.name}: burning error budget >{threshold['burn_rate_threshold']:.1f}x "
                        f"over {long_w} (confirmed over {short_w})"
                    ),
                    "description": (
                        f"Error ratio over {long_w} and {short_w} both exceed the "
                        f"budget-neutral threshold for the {slo.target:.4%} / "
                        f"{slo.period_days}d SLO. Severity: {window.severity}."
                    ),
                },
            }
        )

    return {"groups": [{"name": f"{slo.name}-burn-rate", "rules": rules}]}


def render_yaml(slo: SLO, error_selector: str, total_selector: str, **kwargs) -> str:
    """Convenience wrapper: build the alert group and dump it as YAML text."""
    group = build_alert_group(slo, error_selector, total_selector, **kwargs)
    return yaml.dump(group, sort_keys=False, default_flow_style=False)
