#!/usr/bin/env bash
# Unattended chain: wait for training -> calibration pass (4 workers) -> sensitivity + frontier.
# Marker lines go to results/experiment_logs/chain_c2.log. Safe to rerun (finished parts are skipped).
cd "$(dirname "$0")/.."
L=results/experiment_logs/chain_c2.log
echo "[$(date -u +%T)] chain start" >> $L
while ! grep -q "all trainings cached" results/experiment_logs/train_c2.log 2>/dev/null; do sleep 60; done
if grep -q FAILED results/experiment_logs/train_c2.log; then echo "[$(date -u +%T)] TRAINING FAILURES - stop" >> $L; exit 1; fi
echo "[$(date -u +%T)] training done; calibration pass" >> $L
bash scripts/calibration_pass.sh >> $L 2>&1
sleep 20
while pgrep -f "ex.execute" > /dev/null; do sleep 60; done
echo "[$(date -u +%T)] calibration done; sensitivity+frontier" >> $L
OMP_NUM_THREADS=4 python3 -u -c "import sys;sys.path.insert(0,'.');import warnings;warnings.filterwarnings('ignore');from src import experiments as ex;ex.sensitivity('full');ex.frontier('full')" >> results/experiment_logs/sens_c2.log 2>&1
echo "[$(date -u +%T)] CHAIN DONE (next: timing benchmark alone, then run_all --skip-experiments)" >> $L
