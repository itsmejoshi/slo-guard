"""Command-line interface for slo-guard.

Usage:
    slo-guard rules --config examples/slo.yaml --out rules.yml
    slo-guard budget --config examples/slo.yaml --bad-ratio 0.0015
"""
from __future__ import annotations

import argparse
import sys

from .config import load_config
from .rules import render_yaml


def _cmd_rules(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    text = render_yaml(cfg.slo, cfg.error_selector, cfg.total_selector)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote Prometheus rules to {args.out}")
    else:
        print(text)
    return 0


def _cmd_budget(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    slo = cfg.slo
    consumed = slo.budget_consumed(args.bad_ratio)
    remaining = slo.budget_remaining(args.bad_ratio)
    remaining_minutes = slo.budget_remaining_minutes(args.bad_ratio)

    print(f"SLO: {slo.name} (target={slo.target:.4%}, period={slo.period_days}d)")
    print(f"Observed bad-event ratio: {args.bad_ratio:.4%}")
    print(f"Error budget consumed:    {consumed:.2%}")
    print(f"Error budget remaining:   {remaining:.2%}")
    print(f"Remaining budget (time):  {remaining_minutes:.1f} minutes")
    if remaining < 0:
        print("STATUS: SLO VIOLATED -- error budget exhausted.", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="slo-guard")
    sub = parser.add_subparsers(dest="command", required=True)

    p_rules = sub.add_parser("rules", help="Generate Prometheus burn-rate alert rules")
    p_rules.add_argument("--config", required=True, help="Path to SLO YAML config")
    p_rules.add_argument("--out", help="Output file (default: stdout)")
    p_rules.set_defaults(func=_cmd_rules)

    p_budget = sub.add_parser("budget", help="Report current error-budget status")
    p_budget.add_argument("--config", required=True, help="Path to SLO YAML config")
    p_budget.add_argument(
        "--bad-ratio", required=True, type=float, help="Observed bad-event ratio, e.g. 0.0015"
    )
    p_budget.set_defaults(func=_cmd_budget)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
