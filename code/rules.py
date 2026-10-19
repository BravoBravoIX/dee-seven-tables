"""T2 rule search with held-out cells and shuffled controls (as pre-registered).

Every family is scored the same way: hide H scorable cells of a table, let the
family predict which number stood in each hidden cell from the rest, and count
the expected number of correct cells (ties between equally good fits are
averaged). Real tables are compared with the same tables with the numbers of
their scorable cells shuffled among the scorable positions (damaged and
uncertain cells stay where they are).

Usage: python -I rules.py [--shuffles N] [--folds F] [--hide H] [--out PATH]
       python -I rules.py --synthetic   (timing on a random table; no real data)
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import st_data  # noqa: E402

N7 = 7
CELLS = 49
RC = np.array([(i // 7, i % 7) for i in range(CELLS)])
LINES = [list(range(r * 7, r * 7 + 7)) for r in range(7)] + [
    list(range(c, 49, 7)) for c in range(7)
]
LINES = np.array(LINES)


# ---------------------------------------------------------------- move sets
def adjacency(moves: set[tuple[int, int]], torus: bool) -> np.ndarray:
    a = np.zeros((CELLS + 1, CELLS + 1), dtype=np.int8)  # index 49 = unknown
    for i in range(CELLS):
        for j in range(CELLS):
            dr, dc = RC[j] - RC[i]
            if torus:
                dr, dc = min(abs(dr), 7 - abs(dr)), min(abs(dc), 7 - abs(dc))
            else:
                dr, dc = abs(dr), abs(dc)
            if (dr, dc) in moves:
                a[i, j] = 1
    return a


def leaper(m: int, n: int) -> set[tuple[int, int]]:
    return {(m, n), (n, m)}


KING = {(0, 1), (1, 0), (1, 1)}
WALKS = {
    "walk_king": (KING, False, 1),
    "walk_knight": (leaper(1, 2), False, 1),
    "walk_wazir": ({(0, 1), (1, 0)}, False, 1),
    "walk_ferz": ({(1, 1)}, False, 1),
    "walk_dabbaba": (leaper(0, 2), False, 1),
    "walk_alfil": ({(2, 2)}, False, 1),
    "walk_camel": (leaper(1, 3), False, 1),
    "walk_zebra": (leaper(2, 3), False, 1),
    "walk_king_torus": (KING, True, 1),
    "walk_knight_torus": (leaper(1, 2), True, 1),
    "step7_king": (KING, False, 7),
}
ADJ = {name: adjacency(m, tor) for name, (m, tor, _) in WALKS.items()}

COMPLETION = list(WALKS) + ["latin_q", "latin_s", "cluster_q", "cluster_s", "magic"]
MAPS = ["affine_base0", "affine_base1", "order_stride", "shared_layout"]
FAMILIES = COMPLETION + MAPS


# ---------------------------------------------------------- completion families
def completion_objectives(pos: np.ndarray, grid: np.ndarray) -> dict[str, np.ndarray]:
    """pos: (P, 51) cell of number k (49 = unknown); grid: (P, 49) number per cell (0 unknown)."""
    out = {}
    for name, (_, _, step) in WALKS.items():
        a = pos[:, 1 : 50 - step]
        b = pos[:, 1 + step : 50]
        out[name] = ADJ[name][a, b].sum(1).astype(float)
    known = grid > 0
    q = np.where(known, (grid - 1) // 7, -1)
    s = np.where(known, (grid - 1) % 7, -1)
    for lab, arr in (("q", q), ("s", s)):
        lv = arr[:, LINES]  # (P, 14, 7)
        distinct = np.zeros(arr.shape[0])
        for v in range(7):
            distinct += (lv == v).any(axis=2).sum(axis=1)
        out["latin_" + lab] = distinct
        out["cluster_" + lab] = -distinct
    g = grid[:, LINES].astype(float)
    kn = (g > 0).sum(axis=2)
    sm = g.sum(axis=2)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(kn > 0, sm / np.maximum(kn, 1), 25.0)
    out["magic"] = -(kn * (mean - 25.0) ** 2).sum(axis=1)
    return out


PERM_CACHE: dict[int, np.ndarray] = {}


def perms(h: int) -> np.ndarray:
    if h not in PERM_CACHE:
        PERM_CACHE[h] = np.array(list(itertools.permutations(range(h))), dtype=np.int64)
    return PERM_CACHE[h]


def completion_scores(num: np.ndarray, hidden: np.ndarray) -> dict[str, float]:
    """num: 49 numbers (0 = unusable). hidden: cell indices hidden. Expected correct per family."""
    vis = num.copy()
    hid_nums = num[hidden]
    vis[hidden] = 0
    P = perms(len(hidden))
    npm = P.shape[0]
    grid = np.repeat(vis[None, :], npm, axis=0)
    # assignment: hidden number j goes to hidden cell P[i, j]
    cells_for = hidden[P]  # (npm, h)
    rows = np.arange(npm)[:, None]
    grid[rows, cells_for] = hid_nums[None, :]
    pos = np.full((npm, 51), CELLS, dtype=np.int64)
    vis_cells = np.nonzero(vis)[0]
    pos[:, vis[vis_cells]] = vis_cells[None, :]
    pos[rows, hid_nums[None, :]] = cells_for
    correct = (cells_for == hidden[None, :]).sum(axis=1)  # identity perm is the truth
    out = {}
    for name, obj in completion_objectives(pos, grid).items():
        best = obj >= obj.max() - 1e-9
        out[name] = float(correct[best].mean())
    return out


# ------------------------------------------------------------------ map families
def _gl2_7() -> np.ndarray:
    mats = []
    for a, b, c, d in itertools.product(range(7), repeat=4):
        if (a * d - b * c) % 7:
            mats.append((a, b, c, d))
    return np.array(mats)


GL = _gl2_7()


def _affine_tables(base: int):
    k = np.arange(1, 50)
    if base == 0:
        q, s = (k - 1) // 7, (k - 1) % 7
    else:
        q, s = (k // 7) % 7, k % 7
    r = (GL[:, 0:1] * q[None] + GL[:, 1:2] * s[None]) % 7
    c = (GL[:, 2:3] * q[None] + GL[:, 3:4] * s[None]) % 7
    aq = r * 7 + c  # (nA, 49): cell of number k (index k-1) before offset
    inv = np.zeros_like(aq)
    for ai in range(aq.shape[0]):
        inv[ai, aq[ai]] = k
    return aq, inv


AFF = {0: _affine_tables(0), 1: _affine_tables(1)}


def _cell_sub(p: np.ndarray, b: np.ndarray) -> np.ndarray:
    """(p - b) mod 7 componentwise for cell indices."""
    return ((p // 7 - b // 7) % 7) * 7 + (p % 7 - b % 7) % 7


def _cell_add(p: np.ndarray, b: np.ndarray) -> np.ndarray:
    return ((p // 7 + b // 7) % 7) * 7 + (p % 7 + b % 7) % 7


def affine_score(num: np.ndarray, hidden: np.ndarray, base: int) -> float:
    aq, inv = AFF[base]
    vis = num.copy()
    vis[hidden] = 0
    vc = np.nonzero(vis)[0]
    ks = vis[vc]
    b = _cell_sub(vc[None, :], aq[:, ks - 1])  # (nA, nv)
    nA = aq.shape[0]
    votes = np.bincount((np.arange(nA)[:, None] * 49 + b).ravel(), minlength=nA * 49)
    best = np.nonzero(votes == votes.max())[0]
    ai, bi = best // 49, best % 49
    pred = inv[ai[:, None], _cell_sub(hidden[None, :], bi[:, None])]  # (nt, h)
    return float((pred == num[hidden][None, :]).sum(axis=1).mean())


def _dihedral() -> list[np.ndarray]:
    g = np.arange(49).reshape(7, 7)
    out = []
    for k in range(4):
        r = np.rot90(g, k)
        out.append(r.ravel())
        out.append(r.T.ravel())
    return out


D8 = _dihedral()  # each: new_cell_index -> old cell index (a permutation of cells)


def _base_orders() -> list[np.ndarray]:
    g = np.arange(49).reshape(7, 7)
    row = g.ravel()
    bous = np.concatenate([g[r] if r % 2 == 0 else g[r][::-1] for r in range(7)])
    # spiral inward, clockwise from top-left
    sp, m = [], g.copy()
    while m.size:
        sp.extend(m[0])
        m = np.rot90(m[1:], 1)
    spiral = np.array(sp)
    diag, diagz = [], []
    for d in range(13):
        cells = [g[r, d - r] for r in range(7) if 0 <= d - r < 7]
        diag.extend(cells)
        diagz.extend(cells if d % 2 == 0 else cells[::-1])
    return [row, bous, spiral, np.array(diag), np.array(diagz)]


def _orders() -> np.ndarray:
    seen, out = set(), []
    for o in _base_orders():
        for d in D8:
            oo = d[o]
            key = tuple(oo)
            if key not in seen:
                seen.add(key)
                out.append(oo)
    return np.array(out)


ORDERS = _orders()  # (nO, 49): order index i -> cell
RANK = np.argsort(ORDERS, axis=1)  # cell -> order index
UNITS = np.array([a for a in range(1, 49) if a % 7])


def order_score(num: np.ndarray, hidden: np.ndarray) -> float:
    vis = num.copy()
    vis[hidden] = 0
    vc = np.nonzero(vis)[0]
    ks = vis[vc] - 1
    i = RANK[:, vc]  # (nO, nv)
    nO, nU = ORDERS.shape[0], len(UNITS)
    b = (ks[None, None, :] - UNITS[None, :, None] * i[:, None, :]) % 49  # (nO, nU, nv)
    idx = (np.arange(nO * nU).reshape(nO, nU)[:, :, None] * 49 + b).ravel()
    votes = np.bincount(idx, minlength=nO * nU * 49)
    best = np.nonzero(votes == votes.max())[0]
    oi, ui, bi = best // (nU * 49), (best // 49) % nU, best % 49
    ih = RANK[oi[:, None], hidden[None, :]]
    pred = (UNITS[ui][:, None] * ih + bi[:, None]) % 49 + 1
    return float((pred == num[hidden][None, :]).sum(axis=1).mean())


def _torus_dihedral() -> np.ndarray:
    out = []
    for d in D8:
        for sh in range(49):
            out.append(_cell_add(d, np.full(49, sh)))
    return np.array(out)  # (392, 49): g(p) for each map


TD = _torus_dihedral()


def shared_score(num: np.ndarray, hidden: np.ndarray, sources: list[np.ndarray]) -> float:
    vis = num.copy()
    vis[hidden] = 0
    vc = np.nonzero(vis)[0]
    ks = vis[vc]
    nG = TD.shape[0]
    votes_all, meta = [], []
    for si, src in enumerate(sources):
        m = src[TD[:, vc]]  # (nG, nv)
        ok = m > 0
        c = (ks[None, :] - m) % 49
        idx = (np.arange(nG)[:, None] * 49 + c)[ok]
        votes_all.append(np.bincount(idx, minlength=nG * 49))
        meta.append(si)
    votes = np.stack(votes_all)  # (nS, nG*49)
    mx = votes.max()
    sbest, gb = np.nonzero(votes == mx)
    gi, ci = gb // 49, gb % 49
    tot = 0.0
    for p in hidden:
        m = np.array([sources[s][TD[g, p]] for s, g in zip(sbest, gi, strict=True)])
        pred = np.where(m > 0, (m - 1 + ci) % 49 + 1, -1)
        tot += float((pred == num[p]).mean())
    return tot


# ------------------------------------------------------------------ driver
def fold_scores(num: np.ndarray, hidden: np.ndarray, sources: list[np.ndarray]) -> dict[str, float]:
    out = completion_scores(num, hidden)
    out["affine_base0"] = affine_score(num, hidden, 0)
    out["affine_base1"] = affine_score(num, hidden, 1)
    out["order_stride"] = order_score(num, hidden)
    out["shared_layout"] = shared_score(num, hidden, sources)
    return out


def table_scores(
    num: np.ndarray, folds: list[np.ndarray], sources: list[np.ndarray]
) -> dict[str, float]:
    tot = dict.fromkeys(FAMILIES, 0.0)
    for h in folds:
        for k, v in fold_scores(num, h, sources).items():
            tot[k] += v
    return tot


def synthetic(args) -> None:
    rng = np.random.default_rng(1)
    num = rng.permutation(np.arange(1, 50))
    num[[3, 4, 5]] = 0
    sources = [rng.permutation(np.arange(1, 50)) for _ in range(6)]
    folds = [rng.choice(np.nonzero(num)[0], args.hide, replace=False) for _ in range(args.folds)]
    t0 = time.time()
    s = table_scores(num, folds, sources)
    dt = time.time() - t0
    print(json.dumps(s, indent=1))
    print(
        f"one table, {args.folds} folds: {dt:.2f} s; est. full run 6 tables x {args.shuffles + 1}: "
        f"{dt * 6 * (args.shuffles + 1) / 60:.1f} min"
    )
    # sanity: a table built by a knight walk should be recovered by walk_knight
    tour = knight_tour()
    num2 = np.zeros(49, dtype=np.int64)
    num2[tour] = np.arange(1, 50)
    s2 = table_scores(num2, folds, sources)
    print("knight-tour table:", {k: round(v, 2) for k, v in s2.items()})
    aq, _ = AFF[0]
    num3 = np.zeros(49, dtype=np.int64)
    num3[_cell_add(aq[5], np.full(49, 10))] = np.arange(1, 50)
    s3 = table_scores(num3, folds, sources)
    print("affine table:", {k: round(v, 2) for k, v in s3.items()})


def knight_tour() -> np.ndarray:
    """Warnsdorff knight tour on 7x7 from corner (for the synthetic check only)."""
    adj = ADJ["walk_knight"][:49, :49]
    for start in range(49):
        path, used = [start], {start}
        while len(path) < 49:
            nb = [j for j in np.nonzero(adj[path[-1]])[0] if j not in used]
            if not nb:
                break
            nxt = min(nb, key=lambda j: sum(1 for x in np.nonzero(adj[j])[0] if x not in used))
            path.append(nxt)
            used.add(nxt)
        if len(path) == 49:
            return np.array(path)
    raise RuntimeError("no tour")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shuffles", type=int, default=20000)
    ap.add_argument("--folds", type=int, default=20)
    ap.add_argument("--hide", type=int, default=6)
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--anomalies", choices=["exclude", "asread"], default="exclude")
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--out", default=str(st_data.RESULTS / "rules.json"))
    args = ap.parse_args()
    if args.synthetic:
        synthetic(args)
        return
    run(args)


def holm(pvals: dict[str, float]) -> dict[str, float]:
    items = sorted(pvals.items(), key=lambda x: x[1])
    m, out, run_max = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        run_max = max(run_max, min(1.0, (m - i) * p))
        out[k] = run_max
    return out


CHUNK = (
    100  # shuffles per work unit; unit u uses default_rng([SEED, 1, u]) whatever the worker count
)


def _null_chunk(job):
    u, nums, folds, n = job
    rng = np.random.default_rng([st_data.SEED, 1, u])
    out = {t: {f: [] for f in FAMILIES} for t in range(2, 8)}
    for _ in range(n):
        for t in range(2, 8):
            sh = nums[t].copy()
            sc = np.nonzero(sh)[0]
            sh[sc] = rng.permutation(sh[sc])
            s = table_scores(sh, folds[t], [nums[s] for s in range(1, 8) if s != t])
            for f in FAMILIES:
                out[t][f].append(s[f])
    return u, out


def run(args) -> None:
    import multiprocessing as mp

    names = st_data.load_names()
    cells = st_data.load_cells()
    tabs = st_data.classify(cells, names, anomalies=args.anomalies)
    rng = np.random.default_rng([st_data.SEED, 0])
    nums = {t: np.array(tabs[t]["num"], dtype=np.int64) for t in range(1, 8)}
    folds = {}
    for t in range(2, 8):
        sc = np.nonzero(nums[t])[0]
        folds[t] = [np.sort(rng.choice(sc, args.hide, replace=False)) for _ in range(args.folds)]
    t0 = time.time()
    real = {
        t: table_scores(nums[t], folds[t], [nums[s] for s in range(1, 8) if s != t])
        for t in range(2, 8)
    }
    units = [
        (u, nums, folds, min(CHUNK, args.shuffles - u * CHUNK))
        for u in range((args.shuffles + CHUNK - 1) // CHUNK)
    ]
    parts = {}
    with mp.get_context("fork").Pool(args.procs) as pool:
        for u, part in pool.imap_unordered(_null_chunk, units):
            parts[u] = part
            print(f"unit {len(parts)}/{len(units)}  {time.time() - t0:.0f}s", flush=True)
    null = {
        t: {f: [x for u in sorted(parts) for x in parts[u][t][f]] for f in FAMILIES}
        for t in range(2, 8)
    }
    per_table, pooled, pooled_p = {}, {}, {}
    for f in FAMILIES:
        rv = sum(real[t][f] for t in range(2, 8))
        nv = np.sum([null[t][f] for t in range(2, 8)], axis=0)
        p = (1 + int((nv >= rv - 1e-9).sum())) / (1 + args.shuffles)
        pooled[f] = {
            "real": rv,
            "null_mean": float(nv.mean()),
            "null_sd": float(nv.std()),
            "null_max": float(nv.max()),
            "p": p,
            "hidden_cells": args.hide * args.folds * 6,
        }
        pooled_p[f] = p
        for t in range(2, 8):
            arr = np.array(null[t][f])
            pt = (1 + int((arr >= real[t][f] - 1e-9).sum())) / (1 + args.shuffles)
            per_table.setdefault(str(t), {})[f] = {
                "real": real[t][f],
                "null_mean": float(arr.mean()),
                "null_max": float(arr.max()),
                "p": pt,
                "accuracy": real[t][f] / (args.hide * args.folds),
            }
    adj = holm(pooled_p)
    for f in FAMILIES:
        pooled[f]["p_holm"] = adj[f]
        pooled[f]["passes"] = adj[f] < 0.05
    inputs = {n: st_data.sha256(st_data.DATA / n) for n in ("cells.csv", "names.csv")}
    rec = {
        "what": "T2 rule search, held-out cells against shuffled controls (pre-registered)",
        "code_commit": st_data.code_commit(),
        "inputs_sha256": inputs,
        "seed": st_data.SEED,
        "params": {
            "shuffles": args.shuffles,
            "folds": args.folds,
            "hide": args.hide,
            "anomalies": args.anomalies,
            "procs": args.procs,
            "chunk": CHUNK,
            "rng": "folds default_rng([seed,0]); shuffle unit u default_rng([seed,1,u])",
        },
        "classes": {
            str(t): {c: tabs[t]["cls"].count(c) for c in ("scorable", "uncertain", "damaged")}
            for t in range(1, 8)
        },
        "folds": {str(t): [f.tolist() for f in folds[t]] for t in range(2, 8)},
        "pooled": pooled,
        "per_table": per_table,
        "passing_families": [f for f in FAMILIES if pooled[f]["passes"]],
        "elapsed_s": round(time.time() - t0, 1),
    }
    # gate (pre-registration section 5): per damaged table, p < 0.05/(2*npass), accuracy >= 0.5
    npass = len(rec["passing_families"])
    gate = {}
    for t in ("2", "3"):
        gate[t] = [
            f
            for f in rec["passing_families"]
            if per_table[t][f]["p"] < 0.05 / (2 * npass) and per_table[t][f]["accuracy"] >= 0.5
        ]
    rec["gate"] = gate
    rec["gate_passed"] = sorted({f for v in gate.values() for f in v})
    Path(args.out).write_text(json.dumps(rec, indent=1))
    for f in FAMILIES:
        x = pooled[f]
        print(
            f"{f:18s} real {x['real']:7.2f}  null {x['null_mean']:6.2f}±{x['null_sd']:.2f} "
            f"max {x['null_max']:6.2f}  p {x['p']:.4f}  holm {x['p_holm']:.4f}"
        )


if __name__ == "__main__":
    main()
