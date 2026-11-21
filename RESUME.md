# How to resume after an interruption (usage limit, container restart, new account)

The revision-1 recompute (review cycle 1 → action plan in REVIEW/review_01.md) runs in the background and is
**checkpointed to this branch every 10 minutes** by `scripts/checkpoint.sh`:

* `results/checkpoint/STATUS.txt` – time of the last checkpoint, number of finished result parts, whether the
  full pass (training → calibration → sensitivity → analysis) and the post pass (case study, timing) finished,
  and the last log lines.
* `results/checkpoint/parts/` – every finished experiment part (CSV + info JSON). Finished parts are skipped
  on rerun, so no calibration work is lost.
* `results/checkpoint/logs/` – run/train/calibration/sensitivity/analysis logs.

Trained models (~1.5 GB) are not in git. Training is deterministic (fixed seeds, LightGBM deterministic
mode), so a resumed run retrains identical models (~2 h on 4 cores, background compute only).

## Resume in a new session
1. Check out branch `claude/nifty-ride-yih0im` of this repository.
2. Read `PROJECT_STATE.md` (exact next step) and `results/checkpoint/STATUS.txt`.
3. If the passes are not both done, run:
   ```bash
   bash scripts/resume.sh
   ```
   (installs requirements, restores finished parts, restarts the full pass, post pass and checkpointing).
4. When `POST_PASS_DONE` appears in `results/experiment_logs/post_pass.log`, rerun
   `python3 run_all.py --mode full --skip-experiments` once more (so the cost table includes the timing
   benchmark), then continue with the manuscript rewrite and review cycle 2 as described in PROJECT_STATE.md.
