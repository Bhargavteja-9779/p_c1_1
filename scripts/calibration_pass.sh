#!/usr/bin/env bash
# Parallel calibration-only pass (all models must already be cached by `ex.train_only('full')`).
# Each worker is single-threaded to avoid OpenMP oversubscription. Blocks until all workers finish.
set -e
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
run() { python3 -u -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src import experiments as ex
ex.execute('full', select=lambda j: $1)
" > results/experiment_logs/calib_$2.log 2>&1 < /dev/null & }
run "(j['kind']=='main') or j['kind'] in ('tsplit','weak')" w1
run "(j['kind']=='loso' and j['fold']<5) or j['kind']=='xds'" w2
run "(j['kind']=='loso' and j['fold']>=5) or j['kind']=='pools'" w3
run "j['kind']=='robust'" w4
echo "started 4 calibration workers"; wait; echo "all calibration workers finished"
