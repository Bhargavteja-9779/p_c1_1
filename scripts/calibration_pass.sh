#!/usr/bin/env bash
# Parallel calibration-only pass (all models must already be cached by `ex.train_only('full')`).
# Each worker is single-threaded to avoid OpenMP oversubscription.
set -e
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
run() { setsid nohup python3 -u -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src import experiments as ex
ex.execute('full', select=lambda j: $1)
" > results/experiment_logs/calib_$2.log 2>&1 < /dev/null & }
run "j['kind']=='main' and j['ds']=='BDG2' and j['seed'] in (0,1,2)" w1
run "(j['kind']=='main' and j['ds']=='BDG2' and j['seed'] in (3,4)) or j['kind']=='weak' or (j['kind']=='robust' and j['ds']=='UCI')" w2
run "(j['kind']=='main' and j['ds']=='UCI') or j['kind'] in ('lso','xds')" w3
run "j['kind']=='robust' and j['ds']=='BDG2'" w4
echo "started 4 calibration workers"
