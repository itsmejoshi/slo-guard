"""Load SLO definitions from a YAML config file.

Example config file (see examples/slo.yaml):

    name: checkout-availability
    target: 0.999
    period_days: 30
    error_selector: 'http_requests_total{job="checkout",code=~"5.."}'
    total_selector: 'http_requests_total{job="checkout"}'
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .core import SLO


@dataclass(frozen=True)
class SLOConfig:
    slo: SLO
    error_selector: str
    total_selector: str


def load_config(path: str | Path) -> SLOConfig:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    required = {"name", "target", "error_selector", "total_selector"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing required config keys: {sorted(missing)}")

    slo = SLO(
        name=data["name"],
        target=float(data["target"]),
        period_days=int(data.get("period_days", 30)),
    )
    return SLOConfig(
        slo=slo,
        error_selector=data["error_selector"],
        total_selector=data["total_selector"],
    )
