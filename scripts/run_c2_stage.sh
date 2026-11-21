#!/usr/bin/env bash
# Resumable cycle-2 rerun in one foreground process tree (training -> calibration pass -> sensitivity+frontier).
cd "$(dirname "$0")/.."
export PYTHONWARNINGS=ignore
L=results/experiment_logs/chain_c2.log
if ! grep -q "all trainings cached" results/experiment_logs/train_c2.log 2>/dev/null; then
  echo "[$(date -u +%T)] training (resume)" >> $L
  python3 -u -c "import sys;sys.path.insert(0,'.');from src import experiments as ex;ex.train_only('full')" >> results/experiment_logs/train_c2.log 2>&1
fi
grep -q FAILED results/experiment_logs/train_c2.log && { echo "TRAINING FAILURES" >> $L; exit 1; }
echo "[$(date -u +%T)] calibration pass" >> $L
bash scripts/calibration_pass.sh >> $L 2>&1
sleep 20
while pgrep -f "ex.execute" > /dev/null; do sleep 30; done
echo "[$(date -u +%T)] calibration done; sensitivity+frontier" >> $L
OMP_NUM_THREADS=4 python3 -u -c "import sys;sys.path.insert(0,'.');from src import experiments as ex;ex.sensitivity('full');ex.frontier('full')" >> results/experiment_logs/sens_c2.log 2>&1
echo "[$(date -u +%T)] CHAIN DONE" >> $L
