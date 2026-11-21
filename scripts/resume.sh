#!/usr/bin/env bash
# Resume the revision-1 recompute in a fresh container/session (see RESUME.md).
set -e
cd "$(dirname "$0")/.."
pip install -q -r requirements.txt
python3 -c "import torch" 2>/dev/null || pip install -q torch --index-url https://download.pytorch.org/whl/cpu
mkdir -p results/parts results/experiment_logs
cp -n results/checkpoint/parts/* results/parts/ 2>/dev/null || true   # finished parts are skipped on rerun
# data are downloaded and models retrained automatically (deterministic: identical models)
setsid nohup bash scripts/full_pass.sh > results/experiment_logs/full_pass.out 2>&1 < /dev/null &
setsid nohup bash scripts/post_pass.sh > /dev/null 2>&1 < /dev/null &
setsid nohup bash scripts/checkpoint.sh > /dev/null 2>&1 < /dev/null &
echo "resumed: watch results/experiment_logs/run.log; status in results/checkpoint/STATUS.txt"
