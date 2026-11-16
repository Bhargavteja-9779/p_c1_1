# REPRODUCIBILITY_STATUS

Last updated: 2026-11-16 (final calibration pass in progress)

| Item | Status | How to reproduce |
|---|---|---|
| Environment | requirements.txt / environment.yml; tested Python 3.13, LightGBM 4.7, PyTorch 2.15 CPU | `pip install -r requirements.txt` |
| Data | automatic download (BDG2 GitHub LFS media URLs; UCI zip); cleaning in src/data/datasets.py | first run of `run_all.py` |
| Determinism | LightGBM `deterministic=True`, fixed seeds (numpy, torch); partition/onboarding seeds fixed in code | identical results on rerun (verified for cached-model reuse) |
| Unit tests | 11 tests (leakage guards, calibration primitives, audit regressions) | `pytest -q tests/` |
| Quick mode | verified end-to-end on 2026-11-15 (before final code) | `python run_all.py --mode quick` |
| Full mode | trainings: one process (~2 h on 4 cores); calibration: parallel single-threaded workers (`scripts/calibration_pass.sh`) or sequential `run_all.py --mode full` | `python run_all.py --mode full` |
| Statistics/tables/figures | generated from results files only | `python run_all.py --mode full --skip-experiments` |
| Manuscript numbers | every number is a token filled by manuscript/values.py from results files | `python manuscript/build_docx.py` |
| Known caveats | run time dominated by model training; parallel LightGBM processes must not share cores (OpenMP oversubscription stalls) | see CHANGELOG.md |
