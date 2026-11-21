#!/usr/bin/env bash
# Complete recomputation: (1) all trainings in one 4-thread process, (2) parallel single-threaded
# calibration workers, (3) sensitivity grid + example extraction, (4) collect + statistics + figures.
set -e
cd "$(dirname "$0")/.."
mkdir -p results/experiment_logs
OMP_NUM_THREADS=4 python3 -u -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src import experiments as ex
ex.train_only('full')
" > results/experiment_logs/train.log 2>&1
bash scripts/calibration_pass.sh
sleep 30
while pgrep -f "ex.execute('full'" > /dev/null; do sleep 60; done
OMP_NUM_THREADS=4 python3 -u -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src import experiments as ex
ex.sensitivity('full')
" > results/experiment_logs/sensitivity.log 2>&1
python3 run_all.py --mode full --skip-experiments > results/experiment_logs/analysis.log 2>&1 || true
echo FULL_PASS_DONE >> results/experiment_logs/train.log
