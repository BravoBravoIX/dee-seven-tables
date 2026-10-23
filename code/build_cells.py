"""Build data/cells.csv from the two reads (data/reads.txt) and list where they differ.

Settlements of disagreements are written here, in SETTLE, with the reason; nothing is
emended. Anomalies are kept exactly as read.

Usage: python -I build_cells.py   -> data/cells.csv, results/read_disagreements.json
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import st_data  # noqa: E402

SOURCE = "Whitby 1982 vol. II p. 121 (Sloane MS 3188 ff. 37b-38a), PDF p. 132"

# (table, row, col) -> (settled token, reason)
SETTLE = {
    (6, 3, 1): (
        "22O",
        "read 1 undecided D/O at 1x; at 2x the letter has the same shape as the O of 29O beside it",
    ),
    (3, 7, 2): (
        "46S*",
        "read 1 missed that the 6 is red; 2.2x zoom shows the 6 in red, 4 and S black",
    ),
}

# Extra notes per cell (what is red, brackets, where the glyphs sit).
NOTES = {
    (1, 1, 4): "B red",
    (1, 1, 5): "5 red",
    (1, 2, 4): "B red",
    (1, 2, 5): "first 1 red",
    (1, 3, 4): "B red",
    (1, 3, 5): "first 1 red",
    (1, 4, 4): "B red",
    (1, 5, 4): "B red",
    (2, 1, 7): "15 in red; letter lost",
    (2, 2, 7): "all red; the E is cut by the ruled line",
    (2, 3, 4): "4 black, 0M red",
    (2, 3, 5): "all red",
    (2, 3, 6): "all red",
    (2, 3, 7): "23 in red; letter lost",
    (2, 4, 4): "all red",
    (2, 4, 5): "empty",
    (2, 4, 6): "only a red N, number lost",
    (2, 4, 7): "empty",
    (2, 5, 4): "3 black, 7R red",
    (2, 5, 5): "all red",
    (2, 5, 6): "17 in red; letter lost",
    (2, 5, 7): "empty",
    (3, 1, 1): "only a red A at the right of the cell; number lost",
    (3, 1, 2): "all red",
    (3, 1, 3): "29 red, A black",
    (3, 2, 1): "all red",
    (3, 2, 2): "all red",
    (3, 2, 3): "all red",
    (3, 2, 4): "30 red, O black",
    (3, 3, 1): "only a red V at the right of the cell; number lost",
    (3, 3, 2): "all red",
    (3, 3, 3): "all red",
    (3, 3, 4): "4 red, 5B black",
    (3, 3, 7): "two dots above the P",
    (3, 4, 1): "empty",
    (3, 4, 2): "a red 8 set in from the left edge; the digit before it and the letter lost",
    (3, 4, 3): "empty",
    (3, 4, 4): "empty",
    (3, 5, 1): "empty",
    (3, 5, 2): "empty",
    (3, 5, 3): "a red 7A at the right of the cell; a digit before the 7 lost",
    (3, 6, 1): "all red",
    (3, 7, 1): "a red 1 at the left of the cell; rest lost",
    (3, 7, 2): "6 red, 4 and S black",
    (5, 2, 1): "2 red",
    (5, 3, 1): "7 red",
    (5, 4, 1): "31 red",
    (5, 6, 1): "37 red",
    (5, 7, 1): "36 red",
    (4, 7, 5): "[11N] written above 34O",
    (4, 7, 6): "[48F] written above 11N",
    (7, 5, 6): "[34] written above 30",
    (7, 7, 1): "[14] written above 24",
}

TOKEN = re.compile(r"^(?:\[(?P<br>[^\]]*)\])?(?P<num>[0-9?]*)(?P<let>[A-Z~]?)(?P<red>\*?)$")


def parse_reads(path: Path) -> dict[str, dict[int, list[list[str]]]]:
    reads: dict[str, dict[int, list[list[str]]]] = {}
    cur = None
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        m = re.match(r"== (read\d) T(\d)", line)
        if m:
            cur = reads.setdefault(m.group(1), {}).setdefault(int(m.group(2)), [])
            continue
        cur.append(line.split())
    for rd in reads.values():
        for t, rows in rd.items():
            assert len(rows) == 7 and all(len(r) == 7 for r in rows), (t, rows)
    return reads


def cell_record(t: int, r: int, c: int, tok: str) -> dict:
    note = NOTES.get((t, r, c), "")
    if tok == "-":
        return dict(
            table=t,
            row=r,
            col=c,
            number="",
            letter="",
            ink="unknown",
            state="lost",
            reading_note=note or "empty",
            source=SOURCE,
        )
    m = TOKEN.match(tok)
    assert m, tok
    num, let, red, br = m.group("num"), m.group("let"), m.group("red"), m.group("br")
    if br:
        note = (
            note + "; " if note else ""
        ) + f"Dee's bracket [{br}] kept as a note, not as the cell's entry"
    frag = "?" in num or let in ("~", "")
    state = "fragment" if frag else "intact"
    return dict(
        table=t,
        row=r,
        col=c,
        number=num,
        letter=let.replace("~", ""),
        ink="red" if red else "black",
        state=state,
        reading_note=note,
        source=SOURCE,
    )


def main() -> None:
    reads = parse_reads(st_data.DATA / "reads.txt")
    r1, r2 = reads["read1"], reads["read2"]
    disagreements, rows = [], []
    for t in range(1, 8):
        for r in range(7):
            for c in range(7):
                a, b = r1[t][r][c], r2[t][r][c]
                key = (t, r + 1, c + 1)
                if a != b:
                    settled, why = SETTLE.get(key, (None, None))
                    assert settled is not None, f"unsettled disagreement at {key}: {a} vs {b}"
                    disagreements.append(
                        {
                            "table": t,
                            "row": r + 1,
                            "col": c + 1,
                            "read1": a,
                            "read2": b,
                            "settled": settled,
                            "reason": why,
                        }
                    )
                    tok = settled
                else:
                    tok = a
                rows.append(cell_record(t, r + 1, c + 1, tok))
    with open(st_data.DATA / "cells.csv", "w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "table",
                "row",
                "col",
                "number",
                "letter",
                "ink",
                "state",
                "reading_note",
                "source",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    (st_data.RESULTS / "read_disagreements.json").write_text(
        json.dumps(
            {
                "what": "Cells where the two reads differ, and how each was settled",
                "inputs_sha256": {"reads.txt": st_data.sha256(st_data.DATA / "reads.txt")},
                "code_commit": st_data.code_commit(),
                "n_cells": len(rows),
                "disagreements": disagreements,
            },
            indent=1,
        )
    )
    print(f"{len(rows)} cells; {len(disagreements)} disagreements")
    for d in disagreements:
        print(d)


if __name__ == "__main__":
    main()
