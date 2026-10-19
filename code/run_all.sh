#!/usr/bin/env bash
# Rerun the whole study from data/ (CPU only). Usage: code/run_all.sh
# Needs Python 3 with numpy (the published results were made with Python 3.13 and numpy 2.5.4):
#   uv run --no-project --python 3.13 --with numpy==2.5.4 code/run_all.sh
# The rule search takes about an hour on 6 processes; PROCS sets the number of processes
# (the results do not depend on it). Every other step takes seconds.
# The Claude API witness reads (results/claude_reads*.json) are recorded results and are not rerun.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
PROCS="${PROCS:-6}"
"$PY" -c "import numpy" || { echo "numpy is needed (see the comment at the top of this script)" >&2; exit 1; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
"$PY" -I "$HERE/build_cells.py"          # data/cells.csv, results/read_disagreements.json
"$PY" -I "$HERE/compare_witnesses.py"    # results/witness_compare.json
nice -n 19 "$PY" -I "$HERE/hints.py"     # results/hints.json (100,000 shuffles)
nice -n 19 "$PY" -I "$HERE/rules.py" --procs "$PROCS"   # results/rules.json (about an hour on 6)
"$PY" -I "$HERE/placements.py"           # results/placements.json
"$PY" -I "$HERE/figure.py"               # results/seven_tables_cross.svg
