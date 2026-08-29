import yaml

from slo_guard.core import SLO
from slo_guard.rules import build_alert_group, render_yaml

ERROR_SEL = 'http_requests_total{job="checkout",code=~"5.."}'
TOTAL_SEL = 'http_requests_total{job="checkout"}'


def test_build_alert_group_structure():
    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    group = build_alert_group(slo, ERROR_SEL, TOTAL_SEL)

    assert "groups" in group
    assert len(group["groups"]) == 1
    rules = group["groups"][0]["rules"]
    assert len(rules) == 3
    names = {r["alert"] for r in rules}
    assert names == {
        "checkout-availability_burn_rate_fast",
        "checkout-availability_burn_rate_medium",
        "checkout-availability_burn_rate_slow",
    }


def test_alert_expr_contains_selectors_and_and_clause():
    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    group = build_alert_group(slo, ERROR_SEL, TOTAL_SEL)
    rule = group["groups"][0]["rules"][0]
    assert ERROR_SEL in rule["expr"]
    assert TOTAL_SEL in rule["expr"]
    assert " and " in rule["expr"]


def test_alert_labels_include_severity_and_slo():
    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    group = build_alert_group(slo, ERROR_SEL, TOTAL_SEL)
    for rule in group["groups"][0]["rules"]:
        assert rule["labels"]["slo"] == "checkout-availability"
        assert rule["labels"]["severity"] in {"page", "ticket"}


def test_render_yaml_is_valid_yaml_and_roundtrips():
    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    text = render_yaml(slo, ERROR_SEL, TOTAL_SEL)
    parsed = yaml.safe_load(text)
    assert parsed["groups"][0]["name"] == "checkout-availability-burn-rate"


def test_extra_labels_are_merged():
    slo = SLO(name="checkout-availability", target=0.999, period_days=30)
    group = build_alert_group(
        slo, ERROR_SEL, TOTAL_SEL, extra_labels={"team": "payments"}
    )
    for rule in group["groups"][0]["rules"]:
        assert rule["labels"]["team"] == "payments"
