# EXPERIMENT_LOG

## 2026-11-15 — Smoke test (BDG2, seed 0, 15 % training rows; NOT a reported result)
Purpose: pipeline verification only.
Observations:
* Pipeline runs end-to-end (train 70 s, predictions 8 s, calibration incl. all LOBO tuning 59 s).
* Methods built on the LightGBM point forecast (SCP, ACI, Self-CP, HSC) show mean relative interval
  scores of 11–19 versus ~0.75 for quantile-based methods; Raw-SCP width ~10^4 x mean load.
  -> indicates extreme point forecasts / scores on a few buildings: diagnosed before any full run.
* Per-building calibration (MACD) already differs strongly between pooled and HSC calibration.
