"""Compare the machine witness (Claude API reads) with the reconciled eye reading.

The machine reading never changes data/cells.csv. Every disagreement is listed for a look.
Usage: python -I compare_witnesses.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_cells  # noqa: E402
import st_data  # noqa: E402


def split(tok: str) -> tuple[str, str, bool]:
    m = re.match(r"^(\[[^\]]*\])?(.*?)(\*?)$", tok)
    return (m.group(1) or ""), m.group(2), bool(m.group(3))


def main() -> None:
    reads = build_cells.parse_reads(st_data.DATA / "reads.txt")
    eye = {}
    for t in range(1, 8):
        for r in range(7):
            for c in range(7):
                key = (t, r + 1, c + 1)
                eye[key] = build_cells.SETTLE.get(key, (reads["read2"][t][r][c],))[0]
    files = ["claude_reads.json", "claude_reads_b.json"]
    machine, used = {}, {}
    for fn in files:
        d = json.loads((st_data.RESULTS / fn).read_text())
        for tb in d["tables"]:
            if tb["schema_ok"]:
                used[tb["table"]] = {
                    "file": fn,
                    "prompt_sha256": d["prompt_sha256"],
                    "crop_sha256": tb["crop_sha256"],
                    "model": tb["meta"].get("model"),
                    "cost_usd": tb["meta"].get("cost_usd"),
                }
                for r in range(7):
                    for c in range(7):
                        machine[(tb["table"], r + 1, c + 1)] = tb["rows"][r][c]
    entry_dis, ink_dis, bracket_dis, agree = [], [], [], 0
    for key, e in sorted(eye.items()):
        m = machine[key]
        eb, ee, er = split(e.replace("|", ""))
        mb, me, mr = split(m)
        rec = {"table": key[0], "row": key[1], "col": key[2], "eye": e, "machine": m}
        if ee != me:
            entry_dis.append(rec)
        else:
            agree += 1
        if er != mr:
            ink_dis.append(rec)
        if eb != mb:
            bracket_dis.append(rec)
    out = {
        "what": "Claude API witness against the reconciled eye reading (advisory; never overrides)",
        "code_commit": st_data.code_commit(),
        "inputs_sha256": {f: st_data.sha256(st_data.RESULTS / f) for f in files}
        | {"reads.txt": st_data.sha256(st_data.DATA / "reads.txt")},
        "tables_used": used,
        "cells": len(eye),
        "entries_agree": agree,
        "entry_disagreements": entry_dis,
        "ink_disagreements": ink_dis,
        "bracket_disagreements": bracket_dis,
    }
    (st_data.RESULTS / "witness_compare.json").write_text(json.dumps(out, indent=1))
    print(
        f"entries agree {agree}/{len(eye)}; ink differs {len(ink_dis)}; "
        f"brackets differ {len(bracket_dis)}"
    )
    for d in entry_dis:
        print("ENTRY", d)
    for d in bracket_dis:
        print("BRACKET", d)


if __name__ == "__main__":
    main()
