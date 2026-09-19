"""CLI integration tests: run the actual `slo-guard` entry point as a
subprocess against the example config, mirroring how a real user or CI
pipeline would invoke it.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CONFIG = REPO_ROOT / "examples" / "slo.yaml"


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "slo_guard.cli", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_budget_text_output_passing():
    result = run_cli(
        ["budget", "--config", str(EXAMPLE_CONFIG), "--bad-ratio", "0.0001"]
    )
    assert result.returncode == 0
    assert "SLO: checkout-availability" in result.stdout
    assert "Error budget consumed:" in result.stdout


def test_budget_text_output_violated():
    result = run_cli(
        ["budget", "--config", str(EXAMPLE_CONFIG), "--bad-ratio", "0.05"]
    )
    assert result.returncode == 1
    assert "SLO VIOLATED" in result.stderr


def test_budget_json_output_is_valid_and_well_structured():
    result = run_cli(
        ["budget", "--config", str(EXAMPLE_CONFIG), "--bad-ratio", "0.0001", "--format", "json"]
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["slo"] == "checkout-availability"
    assert payload["violated"] is False
    assert "budget_consumed" in payload
    assert "budget_remaining" in payload
    assert "budget_remaining_minutes" in payload
    assert payload["bad_event_ratio"] == pytest.approx(0.0001)


def test_budget_json_output_reflects_violation_and_exit_code():
    result = run_cli(
        ["budget", "--config", str(EXAMPLE_CONFIG), "--bad-ratio", "0.05", "--format", "json"]
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["violated"] is True
    assert payload["budget_remaining"] < 0
    # JSON mode should never print the human-readable STATUS line to stderr
    assert "STATUS" not in result.stderr


def test_budget_defaults_to_text_format():
    result = run_cli(
        ["budget", "--config", str(EXAMPLE_CONFIG), "--bad-ratio", "0.0001"]
    )
    # stdout should NOT be parseable JSON when --format is omitted
    with pytest.raises(json.JSONDecodeError):
        json.loads(result.stdout)


def test_rules_command_still_works():
    result = run_cli(["rules", "--config", str(EXAMPLE_CONFIG)])
    assert result.returncode == 0
    assert "groups:" in result.stdout
