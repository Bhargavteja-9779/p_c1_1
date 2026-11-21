# Resume protocol (read first)

This project is worked on across many sessions/accounts that hit usage limits. When the user says
"continue" (or similar), do NOT ask what to do:

1. Read `PROJECT_STATE.md` — section **Exact next step** is authoritative. Also skim the tail of
   `CHANGELOG.md` and `REVIEW_HISTORY.md`.
2. Work on branch `claude/jolly-meitner-850g1y` (pull it first).
3. Fresh container: `pip install -r requirements.txt`. Data in `data/raw` is gitignored and re-downloads
   automatically on the first experiment run (`src/data/datasets.py::download`); only needed if
   experiments must be rerun. Trained models are not in git: reruns retrain (~2 h on 4 cores).
4. Review cycles: `REVIEW/review_workflow.js` (10 reviewer agents; args `{cycle, packet}`), one cycle at a
   time (user choice). Raw reviewer output is saved to `REVIEW/review_XX_raw.json`, consolidation to
   `REVIEW/review_XX.md`. If `review_XX_raw.json` exists, do not rerun that cycle's reviewers.
   After each cycle's fixes, ask the user before starting the next cycle.

# Saving progress (usage limits)
- Commit and push after every meaningful step (review saved, each fix batch, each rebuild), and update
  `PROJECT_STATE.md` → **Exact next step** before each push, so a new session can pick up with "continue".
- Keep token use modest: targeted reads, no re-reading large packets unless needed.
