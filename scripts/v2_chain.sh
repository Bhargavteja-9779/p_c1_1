#!/usr/bin/env bash
cd "$(dirname "$0")/.."
while pgrep -f "train_only" > /dev/null; do sleep 60; done
echo "training finished $(date)"; grep -c FAILED results/experiment_logs/train_v2b.out
bash scripts/calibration_pass.sh
echo "calibration finished $(date)"
OMP_NUM_THREADS=4 python3 -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src import experiments as ex
ex.sensitivity('full'); ex.collect()
" > results/experiment_logs/sensitivity_v2.log 2>&1
OMP_NUM_THREADS=1 python3 -m src.statistics.latency > results/experiment_logs/latency.log 2>&1
echo "chain finished $(date)"; grep -l "FAILED" results/experiment_logs/calib_*.log results/experiment_logs/sensitivity_v2.log
