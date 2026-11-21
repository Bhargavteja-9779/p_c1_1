# Resume protocol (read first)

This project is worked on across many sessions/accounts that hit usage limits. When the user says
"continue" (or similar), do NOT ask what to do:

1. Read `PROJECT_STATE.md` — section **RESUME HERE** is authoritative. Also skim the tail of
   `CHANGELOG.md` and `REVIEW_HISTORY.md`.
2. Work on branch `claude/jolly-meitner-850g1y` (pull it first). Before starting, `git fetch` and check whether
   another `claude/*` branch has newer progress on this line; if so, continue from the most advanced one.
3. Fresh container: `pip install -r requirements.txt`. Data re-downloads automatically; trained models are not in
   git (retrain per PROJECT_STATE "How to resume"; never run calibration while training runs).
4. Review cycles: one cycle at a time; raw reviews in `REVIEW/cycleXX_raw/`, consolidation in `REVIEW/review_XX.md`.
   If raw reviews for a cycle exist, do not rerun them. After each cycle's fixes, ask the user before the next cycle.

# Saving progress (usage limits)
- Commit and push after every meaningful step, and update `PROJECT_STATE.md` → **RESUME HERE** before each push.
- Keep token use modest: targeted reads, no re-reading large packets unless needed.
