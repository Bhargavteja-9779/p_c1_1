#!/usr/bin/env bash
# Periodic checkpoint so a new session (even on another account) can resume after an interruption.
# Every 10 min: copy finished result parts + logs into the tracked folder results/checkpoint/, write a
# status file, commit and push to the development branch. Stops after both passes have finished.
cd "$(dirname "$0")/.."
BR=$(git rev-parse --abbrev-ref HEAD)
while true; do
  mkdir -p results/checkpoint/parts results/checkpoint/logs
  cp -u results/parts/* results/checkpoint/parts/ 2>/dev/null
  cp results/experiment_logs/*.log results/checkpoint/logs/ 2>/dev/null
  {
    echo "checkpoint: $(date -u '+%Y-%m-%d %H:%M UTC')"
    echo "finished result parts: $(ls results/parts 2>/dev/null | grep -c 'a0\.\|_f[0-9]\.csv$\|robust.*\.csv$\|xds.*\.csv$' )"
    echo "trained model sets cached locally: $(ls results/cache 2>/dev/null | grep -c '^MODELS_')"
    echo "full pass done: $(grep -q FULL_PASS_DONE results/experiment_logs/train.log 2>/dev/null && echo yes || echo no)"
    echo "post pass done: $(grep -q POST_PASS_DONE results/experiment_logs/post_pass.log 2>/dev/null && echo yes || echo no)"
    echo "last run.log lines:"; tail -5 results/experiment_logs/run.log 2>/dev/null
  } > results/checkpoint/STATUS.txt
  git add results/checkpoint >/dev/null 2>&1
  if grep -q FULL_PASS_DONE results/experiment_logs/train.log 2>/dev/null; then
    git add results tables figures >/dev/null 2>&1   # final outputs (gitignored intermediates excluded)
  fi
  if ! git diff --cached --quiet; then
    git commit -q -m "Checkpoint of revision-1 recompute ($(date -u '+%H:%M UTC'))" >/dev/null 2>&1
    for i in 1 2 3 4; do git push -q origin "$BR" >/dev/null 2>&1 && break; sleep $((5 * i)); done
  fi
  grep -q POST_PASS_DONE results/experiment_logs/post_pass.log 2>/dev/null && break
  sleep 600
done
