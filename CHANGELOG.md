# CHANGELOG

## 2026-11-15
- Initial implementation (data, features, forecasters, calibration, metrics, tests).
- Fix: float32 tolerance in grid quantile search (unit test exposed 1-grid-step discrepancy).
- Data-quality fix (before any full experiment): runs of >=24 identical readings (stuck meters,
  incl. constant non-zero values) are now treated as missing (previously only zero runs). Found via
  smoke-test diagnostics: Lamb-site meters flat-lined at 0.0002-0.0046 kWh in 2017 produced
  normalised errors of ~80x. BDG2 buildings after filter: 984 -> 842; UCI 316 -> 315.
- Training-only filter: drop rows with normalised target y/s > 20 (meter restarts after outages).
- Onboarding windows drawn only where >= 80 % of hours are valid (all methods identical).
- HSC-CQR moved out of the ablation-only block so that it is evaluated in all experiments.
