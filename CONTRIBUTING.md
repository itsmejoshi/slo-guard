# Contributing to slo-guard

Thanks for considering a contribution! This project is small and focused,
so contributions of any size are welcome — bug reports, docs fixes,
new burn-rate policy presets, additional rule-generator backends
(e.g. Datadog, Grafana Alerting), etc.

## Setup

```bash
git clone https://github.com/itsmejoshi/slo-guard
cd slo-guard
pip install -e ".[dev]"
```

## Running tests

```bash
pytest --cov=slo_guard --cov-report=term-missing
```

## Linting

```bash
ruff check src tests
```

## Submitting changes

1. Fork the repo and create a branch off `main`.
2. Add tests for any new behavior — PRs without tests for new logic will be
   asked to add them.
3. Make sure `pytest` and `ruff check` pass locally.
4. Open a PR with a clear description of the change and why it's needed.

## Design principles

- Keep the core math (`core.py`, `burnrate.py`) dependency-free and provable
  from first principles — no hard-coded magic numbers.
- Keep the library usable both as a CLI and as an importable Python API.
- Prefer clarity over cleverness; this is infrastructure tooling that people
  will read during an incident.
