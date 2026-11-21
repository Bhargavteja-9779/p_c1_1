# Archive: SSC-CQR revision line (branch jolly-meitner-850g1y, 2026-11-21, up to commit d763a3a)

A third parallel revision-1 of the v1 manuscript (primary = one-parameter score-shrinkage "SSC-CQR", reliability-aware
LOBO rule "sharpest setting with <=5 % under-covered pseudo-targets"). On 2026-11-21 the project continued from the
more advanced funny-euler/great-ride line (manuscript v2, review cycle 2 done), whose tree was adopted by merge.

Reusable for cycle-2 fixes of the adopted line (reviewer R5 data issues), all in git history at d763a3a:
- `src/data/datasets.py`: no interpolation (only >=24-h stuck runs masked), `long_gap_share`/`eligible` computed on the
  TRAINING period only (no target-year filter; BDG2 842 -> 1,042 eligible buildings), UCI DST hours masked (`dst_hours`).
- `src/experiments.py::prepared`: targets without a window of >=80 % valid hours are dropped (non-look-ahead rule).
- ACI level clipped to [alpha/10, 1] with gamma grid up to 0.05; TQA-B ranks from calibration only; Self-CQR with
  minimum-history fallback (72/168/336 h); site-level sign-flip tests; `scripts/duplicate_check.py` (0 pairs r>0.99
  in BDG2 and UCI with these rules); `scripts/benchmark_timing.py`.
- Consolidated cycle-1 review for this line: REVIEW/review_01.md at d763a3a (20 themes).
Seed-0..4 calibration results of this line were computed but not analysed (not committed; data/caches not in git).
