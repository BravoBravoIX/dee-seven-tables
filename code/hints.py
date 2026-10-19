"""Pre-registered re-tests of the two first-pass hints (H1, H2), plus the full
12-test grid they came from (reported for context only).

H1: table 2, consecutive numbers k, k+1 a knight's move apart (plain board).
H2: table 4, consecutive numbers k, k+1 king-adjacent (plain board).
Statistic: number of such pairs among scorable cells. Null: the numbers of the
scorable cells shuffled among the scorable positions (damaged and uncertain
cells fixed), 100,000 shuffles, seed 20261019. One-sided p = (1 + #null >= real)/(1 + N).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import st_data  # noqa: E402
from rules import ADJ, CELLS  # noqa: E402

N = 100_000


def count(num: np.ndarray, adj: np.ndarray) -> int:
    pos = np.full(51, CELLS, dtype=np.int64)
    nz = np.nonzero(num)[0]
    pos[num[nz]] = nz
    return int(adj[pos[1:49], pos[2:50]].sum())


def count_batch(nums: np.ndarray, adj: np.ndarray) -> np.ndarray:
    pos = np.full((nums.shape[0], 51), CELLS, dtype=np.int64)
    for i, num in enumerate(nums):
        nz = np.nonzero(num)[0]
        pos[i, num[nz]] = nz
    return adj[pos[:, 1:49], pos[:, 2:50]].sum(axis=1)


def main() -> None:
    names = st_data.load_names()
    tabs = st_data.classify(st_data.load_cells(), names)
    rng = np.random.default_rng(st_data.SEED)
    out = {"grid": {}}
    for t in range(2, 8):
        num = np.array(tabs[t]["num"], dtype=np.int64)
        sc = np.nonzero(num)[0]
        sh = np.repeat(num[None, :], N, axis=0)
        for i in range(N):
            sh[i, sc] = rng.permutation(num[sc])
        pairs_possible = int(
            sum(1 for k in range(1, 49) if (num == k).any() and (num == k + 1).any())
        )
        for mv in ("walk_knight", "walk_king"):
            real = count(num, ADJ[mv])
            null = count_batch(sh, ADJ[mv])
            out["grid"][f"T{t}_{mv}"] = {
                "real": real,
                "pairs_with_both_scorable": pairs_possible,
                "null_mean": float(null.mean()),
                "p": (1 + int((null >= real).sum())) / (1 + N),
            }
    h1, h2 = out["grid"]["T2_walk_knight"], out["grid"]["T4_walk_king"]
    out["H1_table2_knight"] = dict(h1, p_bonferroni2=min(1.0, 2 * h1["p"]))
    out["H2_table4_king"] = dict(h2, p_bonferroni2=min(1.0, 2 * h2["p"]))
    out.update(
        what="Pre-registered re-tests of the first-pass hints H1 and H2",
        code_commit=st_data.code_commit(),
        inputs_sha256={n: st_data.sha256(st_data.DATA / n) for n in ("cells.csv", "names.csv")},
        seed=st_data.SEED,
        shuffles=N,
    )
    (st_data.RESULTS / "hints.json").write_text(json.dumps(out, indent=1))
    for k, v in out["grid"].items():
        print(f"{k:18s} real {v['real']:3d}  null {v['null_mean']:.2f}  p {v['p']:.4f}")
    print("H1", out["H1_table2_knight"])
    print("H2", out["H2_table4_king"])


if __name__ == "__main__":
    main()
