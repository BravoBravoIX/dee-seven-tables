"""Load the Seven Tables cell transcription and the 49 names.

Cells: data/cells.csv (table,row,col,number,letter,ink,state,reading_note,source),
rows and columns 1-based. Names: data/names.csv (number,name,source).

Cell classes used by the analysis (pre-registered, results/preregistration.md):
- scorable: number fully legible (state intact, or a fragment that lost only its letter),
  the letter (if legible) equals letter t of name k, and the number occurs once in the table;
- uncertain: intact but anomalous (letter does not fit the name, or a number read
  twice); kept in place, never hidden, number not used by any rule;
- damaged: lost, or a fragment whose number is not fully legible.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
SEED = 20261019


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def code_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
        ).stdout.strip()
        return out + ("+dirty" if dirty else "")
    except Exception:  # noqa: BLE001
        return "unknown"


def norm(s: str) -> str:
    return s.upper().replace("U", "V")


def load_names(path: Path = DATA / "names.csv") -> list[str]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    names = [""] * 49
    for r in rows:
        names[int(r["number"]) - 1] = r["name"].strip().upper()
    assert all(len(n) == 7 for n in names), names
    return names


def load_cells(path: Path = DATA / "cells.csv") -> list[dict]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        num = r["number"].strip()
        out.append(
            {
                "table": int(r["table"]),
                "row": int(r["row"]),
                "col": int(r["col"]),
                "number": int(num) if num.isdigit() else None,
                "number_raw": num,
                "letter": r["letter"].strip(),
                "ink": r["ink"].strip(),
                "state": r["state"].strip(),
                "note": r["reading_note"].strip(),
            }
        )
    return out


def classify(cells: list[dict], names: list[str], anomalies: str = "exclude") -> dict[int, dict]:
    """Per table: grid of numbers (0 = unusable), class per cell, sets of numbers.

    anomalies="exclude" (primary): anomalous cells are 'uncertain'. anomalies="asread"
    (sensitivity): a letter that does not fit the name is ignored, and of a number read twice
    the first in reading order is kept."""
    tables: dict[int, dict] = {}
    for t in range(1, 8):
        tc = [c for c in cells if c["table"] == t]
        assert len(tc) == 49, (t, len(tc))
        counts: dict[int, int] = {}
        for c in tc:
            if c["number"] is not None:
                counts[c["number"]] = counts.get(c["number"], 0) + 1
        num = [0] * 49
        cls = [""] * 49
        seen: set[int] = set()
        for c in sorted(tc, key=lambda c: (c["row"], c["col"])):
            i = (c["row"] - 1) * 7 + (c["col"] - 1)
            k = c["number"]
            if c["state"] == "lost" or (c["state"] == "fragment" and (k is None or c["letter"])):
                # lost, or a fragment whose number is not fully legible
                cls[i] = "damaged"
            elif k is None or not (1 <= k <= 49):
                cls[i] = "uncertain"
            elif anomalies == "asread" and k not in seen:
                cls[i] = "scorable"
                num[i] = k
            elif counts[k] > 1 or (c["letter"] and norm(c["letter"]) != norm(names[k - 1][t - 1])):
                cls[i] = "uncertain"
            else:
                cls[i] = "scorable"
                num[i] = k
            if k is not None:
                seen.add(k)
        present = {c["number"] for c in tc if c["number"] is not None}
        tables[t] = {
            "num": num,
            "cls": cls,
            "absent": sorted(set(range(1, 50)) - present),
            "cells": tc,
        }
    return tables
