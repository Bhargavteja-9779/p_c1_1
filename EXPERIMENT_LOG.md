# EXPERIMENT_LOG

## 2026-11-15 — Smoke test (BDG2, seed 0, 15 % training rows; NOT a reported result)
Purpose: pipeline verification only.
Observations:
* Pipeline runs end-to-end (train 70 s, predictions 8 s, calibration incl. all LOBO tuning 59 s).
* Methods built on the LightGBM point forecast (SCP, ACI, Self-CP, HSC) show mean relative interval
  scores of 11–19 versus ~0.75 for quantile-based methods; Raw-SCP width ~10^4 x mean load.
  -> indicates extreme point forecasts / scores on a few buildings: diagnosed before any full run.
* Per-building calibration (MACD) already differs strongly between pooled and HSC calibration.

## 2026-11-15/16 — Full run
* Trainings: main (BDG2 5 seeds, UCI 5 seeds), leave-site-out (5 folds), cross-dataset (BDG2→UCI, UCI→BDG2,
  BDG2→BDG2 without weather; 3 seeds; source models shared via model cache), weak forecaster (3 seeds).
* Interrupted twice by usage limits / container restarts; resumed from caches (no result reused across code
  versions: all result parts were recomputed with the final calibration code on 2026-11-16).
* Interim (superseded) observations used only for design decisions, all logged in CHANGELOG: evaluation-mask
  bug; component ablation showing no benefit of kNN prior/stage matching; prior-art audit; code audit.
* Final calibration pass 2026-11-16 17:19 UTC: 30 main parts, 5 LSO, 9 cross-dataset, 30 robustness parts,
  sensitivity (E7) and example extraction.
