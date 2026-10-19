"""Exhaustive enumeration of the placements of the lost entries of tables 2 and 3.

A placement puts each absent number of a table into one damaged cell (a bijection),
consistent with what survives in each cell:
- the number field of a fragment is a pattern; '?' stands for lost digits (zero or more),
  so '?8' allows 8, 28, 38, 48 and '1?' allows 1, 13, 19 ...;
- a surviving letter must equal letter t of the name (U = V).

For every completion family the best placements (ties kept) are also listed. They are
applied only if the family passes the pre-registered gate (results/preregistration.md §5);
otherwise they are descriptive.

Variants (§9 of the pre-registration): table 3 '35R' taken as 38R; Alan's lists.

Usage: python -I placements.py [--rules results/rules.json]
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import st_data  # noqa: E402
from rules import COMPLETION, completion_objectives  # noqa: E402


def allowed(cell: dict, k: int, t: int, names: list[str]) -> bool:
    raw = cell["number_raw"]
    if raw and not re.fullmatch(raw.replace("?", r"\d*"), str(k)):
        return False
    if cell["letter"] and st_data.norm(cell["letter"]) != st_data.norm(names[k - 1][t - 1]):
        return False
    return True


def enumerate_table(
    t: int, tabs: dict, names: list[str], absent: list[int]
) -> list[dict[int, int]]:
    dmg = [
        c
        for c in tabs[t]["cells"]
        if tabs[t]["cls"][(c["row"] - 1) * 7 + c["col"] - 1] == "damaged"
    ]
    idx = [(c["row"] - 1) * 7 + c["col"] - 1 for c in dmg]
    assert len(dmg) == len(absent), (t, len(dmg), absent)
    out = []
    for perm in itertools.permutations(absent):
        if all(allowed(c, k, t, names) for c, k in zip(dmg, perm, strict=True)):
            out.append(dict(zip(idx, perm, strict=True)))
    return out


def label(p: dict[int, int], t: int, names: list[str]) -> str:
    return " ".join(
        f"r{i // 7 + 1}c{i % 7 + 1}={k}{names[k - 1][t - 1]}" for i, k in sorted(p.items())
    )


def family_best(t: int, tabs: dict, placements: list[dict[int, int]]) -> dict[str, dict]:
    base = np.array(tabs[t]["num"], dtype=np.int64)
    grids = np.repeat(base[None, :], len(placements), axis=0)
    for j, p in enumerate(placements):
        for i, k in p.items():
            grids[j, i] = k
    pos = np.full((len(placements), 51), 49, dtype=np.int64)
    for j in range(len(placements)):
        nz = np.nonzero(grids[j])[0]
        pos[j, grids[j, nz]] = nz
    objs = completion_objectives(pos, grids)
    out = {}
    for f in COMPLETION:
        o = objs[f]
        best = np.nonzero(o >= o.max() - 1e-9)[0]
        out[f] = {
            "best_value": float(o.max()),
            "n_best": int(len(best)),
            "best": [int(b) for b in best[:20]],
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default=str(st_data.RESULTS / "rules.json"))
    args = ap.parse_args()
    names = st_data.load_names()
    cells = st_data.load_cells()
    tabs = st_data.classify(cells, names)
    passing = []
    if Path(args.rules).exists():
        passing = json.loads(Path(args.rules).read_text()).get("gate_passed", [])
    res = {
        "what": "Exhaustive placements of the lost entries (tables 2 and 3)",
        "code_commit": st_data.code_commit(),
        "inputs_sha256": {n: st_data.sha256(st_data.DATA / n) for n in ("cells.csv", "names.csv")},
        "seed": None,
        "tables": {},
        "variants": {},
    }
    for t in (2, 3):
        absent = tabs[t]["absent"]
        pl = enumerate_table(t, tabs, names, absent)
        letters = {tuple(sorted((i, names[k - 1][t - 1]) for i, k in p.items())) for p in pl}
        fixed = {i: pl[0][i] for i in pl[0] if all(p[i] == pl[0][i] for p in pl)}
        res["tables"][str(t)] = {
            "absent": [f"{k}{names[k - 1][t - 1]}" for k in absent],
            "n_placements": len(pl),
            "n_distinct_letter_patterns": len(letters),
            "forced_by_fragments": {
                f"r{i // 7 + 1}c{i % 7 + 1}": f"{k}{names[k - 1][t - 1]}" for i, k in fixed.items()
            },
            "options_per_cell": {
                f"r{i // 7 + 1}c{i % 7 + 1}": sorted(
                    {f"{p[i]}{names[p[i] - 1][t - 1]}" for p in pl}
                )
                for i in pl[0]
            },
            "families": family_best(t, tabs, pl),
            "applied": {
                f: [label(pl[b], t, names) for b in family_best(t, tabs, pl)[f]["best"]]
                for f in passing
            },
        }
        print(
            f"T{t}: absent {res['tables'][str(t)]['absent']}  placements {len(pl)}  "
            f"letter patterns {len(letters)}"
        )
    # variant: table 3 '35R' as a slip for 38R -> 38 present, 35 absent
    cells_v = [dict(c) for c in cells]
    for c in cells_v:
        if c["table"] == 3 and c["number"] == 35:
            c["number"], c["number_raw"] = 38, "38"
    tabs_v = st_data.classify(cells_v, names)
    pl = enumerate_table(3, tabs_v, names, tabs_v[3]["absent"])
    res["variants"]["T3_35R_as_38R"] = {"absent": tabs_v[3]["absent"], "n_placements": len(pl)}
    # variant: Dee's marginal note beside table 2 ("alr. R.R. 13 30"), read by Whitby (vol. I
    # p. 340) as correcting 12R to 13R and 43R to 30R
    cells_d = [dict(c) for c in cells]
    for c in cells_d:
        if c["table"] == 2 and (c["row"], c["col"]) == (6, 5):
            c["number"], c["number_raw"] = 13, "13"
        if c["table"] == 2 and (c["row"], c["col"]) == (6, 6):
            c["number"], c["number_raw"] = 30, "30"
    tabs_d = st_data.classify(cells_d, names)
    pl = enumerate_table(2, tabs_d, names, tabs_d[2]["absent"])
    res["variants"]["T2_dee_margin_correction"] = {
        "absent": [f"{k}{names[k - 1][1]}" for k in tabs_d[2]["absent"]],
        "n_placements": len(pl),
    }
    # Alan's lists: lost cells only (no fragments), so k! placements over the empty cells
    res["variants"]["alan"] = {
        "T2_lost": ["15A", "30R", "41A"],
        "T2_placements_if_three_empty_cells": 6,
        "T3_lost": ["18I", "19A", "38R", "44G", "48R"],
        "T3_placements_if_five_empty_cells": 120,
    }
    print(json.dumps(res["variants"]))
    (st_data.RESULTS / "placements.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
