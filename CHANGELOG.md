# Changelog

## [0.1.0] - 2026-08-29

### Added
- Core `SLO` model with error-budget and budget-remaining calculations.
- Multi-window, multi-burn-rate policy engine (`evaluate_policy`), generalized
  so it reproduces the standard Google SRE Workbook constants (14.4 / 6 / 1)
  for a 99.9%/30-day SLO and scales correctly for other targets/periods.
- Prometheus alerting rule generator (`build_alert_group`, `render_yaml`).
- YAML-based SLO config loader.
- CLI (`slo-guard rules`, `slo-guard budget`).
- Full test suite (pytest) covering core math, burn-rate policy, rule
  generation, and config loading.
