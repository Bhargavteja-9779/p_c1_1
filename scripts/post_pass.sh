#!/usr/bin/env bash
# Revision-1 additions run after scripts/full_pass.sh: downstream case study, then the isolated timing
# benchmark (single process, one thread, nothing else running).
cd "$(dirname "$0")/.."
until grep -q FULL_PASS_DONE results/experiment_logs/train.log 2>/dev/null; do sleep 120; done
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 -u -c "
import sys; sys.path.insert(0,'.')
import warnings; warnings.filterwarnings('ignore')
from src.statistics import case_study, timing
print(case_study.run()); print(timing.run())
" > results/experiment_logs/post_pass.log 2>&1
echo POST_PASS_DONE >> results/experiment_logs/post_pass.log
