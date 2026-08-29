import textwrap

import pytest

from slo_guard.config import load_config


def _write_config(tmp_path, content):
    path = tmp_path / "slo.yaml"
    path.write_text(textwrap.dedent(content))
    return path


def test_load_valid_config(tmp_path):
    path = _write_config(
        tmp_path,
        """
        name: checkout-availability
        target: 0.999
        period_days: 30
        error_selector: 'http_requests_total{job="checkout",code=~"5.."}'
        total_selector: 'http_requests_total{job="checkout"}'
        """,
    )
    cfg = load_config(path)
    assert cfg.slo.name == "checkout-availability"
    assert cfg.slo.target == pytest.approx(0.999)
    assert cfg.slo.period_days == 30


def test_load_config_defaults_period_days(tmp_path):
    path = _write_config(
        tmp_path,
        """
        name: x
        target: 0.99
        error_selector: 'a'
        total_selector: 'b'
        """,
    )
    cfg = load_config(path)
    assert cfg.slo.period_days == 30


def test_load_config_missing_keys_raises(tmp_path):
    path = _write_config(tmp_path, "name: x\ntarget: 0.99\n")
    with pytest.raises(ValueError):
        load_config(path)
