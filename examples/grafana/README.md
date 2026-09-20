# Grafana integration example

This directory is an **optional, isolated demo** for visualizing the same SLO signals that `slo-guard` uses for Prometheus burn-rate alerting.

It does not change the `slo-guard` Python package or CLI. Everything here runs separately under `examples/grafana/`.

## What the demo includes

- a tiny demo metrics endpoint that exposes `http_requests_total`
- Prometheus scraping and `slo-guard`-style burn-rate rules
- Grafana provisioning for the Prometheus data source
- an importable Grafana dashboard with:
  - SLO target
  - current SLI
  - 30-day error-budget remaining
  - 1-hour burn rate
  - active burn-rate alerts
  - successful vs. failed request rate

## Run the demo

From the repository root:

```bash
docker compose -f examples/grafana/docker-compose.yml up -d
```

Open:

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- demo metrics: http://localhost:8000/metrics

Grafana is provisioned with anonymous viewer access for this **local demo only**, so the dashboard is available immediately.

## Trigger a burn-rate incident

The demo starts in a healthy state. To raise the simulated error rate:

```bash
curl http://localhost:8000/burn
```

Wait a few minutes for the short alert window and `for` duration to evaluate, then watch the Grafana dashboard and Prometheus alerts.

Recover the demo:

```bash
curl http://localhost:8000/recover
```

## Regenerate the Prometheus rules with slo-guard

The committed rule file is included so the Docker demo works without installing the package. To regenerate it from the demo SLO definition:

```bash
python -m pip install -e .
slo-guard rules \
  --config examples/grafana/slo.yaml \
  --out examples/grafana/prometheus/rules/checkout-rules.yml
```

This is the integration boundary:

```text
slo.yaml
   |
   v
slo-guard
   |
   +--> Prometheus burn-rate rules
   |
   v
Prometheus
   |
   v
Grafana dashboard
```

## Stop and clean up

```bash
docker compose -f examples/grafana/docker-compose.yml down -v
```

## Notes

This example intentionally stays outside `src/slo_guard/` and does not add runtime dependencies to the package. It is meant as a reproducible integration example, not a production Grafana deployment.
