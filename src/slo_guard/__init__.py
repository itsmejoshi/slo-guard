"""slo-guard: SLO error-budget tracking and multi-window burn-rate alerting.

Quick start:

    from slo_guard import SLO, evaluate_policy

    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    print(slo.budget_consumed(bad_event_ratio=0.0015))
    print(evaluate_policy(slo))
"""
from .burnrate import DEFAULT_POLICY, BurnRateWindow, evaluate_policy
from .config import SLOConfig, load_config
from .core import SLO
from .rules import build_alert_group, render_yaml

__version__ = "0.2.0"

__all__ = [
    "DEFAULT_POLICY",
    "SLO",
    "BurnRateWindow",
    "SLOConfig",
    "__version__",
    "build_alert_group",
    "evaluate_policy",
    "load_config",
    "render_yaml",
]
