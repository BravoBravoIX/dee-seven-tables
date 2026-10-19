"""Draw the cross of seven tables as an SVG, marking lost, fragmentary and anomalous cells.

Lost or fragmentary cells show what survives and the entries that could stand there
(results/placements.json). If a rule had passed the pre-registered gate, its placement
would be drawn in blue; none did unless rules.json says so.

Usage: python -I figure.py  -> results/seven_tables_cross.svg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import st_data  # noqa: E402

W = 64  # full cell width (tables 1, 4, 7)
H = 46
HW = W / 2  # half-width cells (tables 2, 3, 5, 6)
X0, Y0 = 40, 84
INK = "#1d1d1f"
RED = "#c0392b"
LOST = "#f3e3c3"
FRAG = "#fbefd9"
ANOM = "#7d3c98"


def origin(t: int) -> tuple[float, float, float]:
    """Top-left corner and cell width of table t."""
    mid_y = Y0 + 7 * H
    return {
        2: (X0 + 7 * W, Y0, HW),
        3: (X0 + 7 * W + 7 * HW, Y0, HW),
        7: (X0, mid_y, W),
        1: (X0 + 7 * W, mid_y, W),
        4: (X0 + 14 * W, mid_y, W),
        6: (X0 + 7 * W, mid_y + 7 * H, HW),
        5: (X0 + 7 * W + 7 * HW, mid_y + 7 * H, HW),
    }[t]


def main() -> None:
    names = st_data.load_names()
    cells = st_data.load_cells()
    tabs = st_data.classify(cells, names)
    pl = json.loads((st_data.RESULTS / "placements.json").read_text())
    rules = json.loads((st_data.RESULTS / "rules.json").read_text())
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {X0 * 2 + 21 * W} {Y0 + 21 * H + 120}" '  # noqa: E501
        'font-family="Georgia, serif">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{X0}" y="34" font-size="20" fill="{INK}">Dee\'s Seven Tables of Creation '
        "(Sloane MS 3188 ff. 37v-38r), as drawn by Whitby (1982)</text>",
        f'<text x="{X0}" y="56" font-size="13" fill="#555">Table 1 centre; 2 and 3 above; '
        "7 left, 4 right; 6 and 5 below. Shaded: lost or fragmentary; purple frame: anomalous "
        "entry (does not fit Dee's name list, or number read twice); red: known only from "
        "Ashmole's 1672 copy.</text>",
    ]
    for t in range(1, 8):
        ox, oy, cw = origin(t)
        if t != 1:  # table 1 is the centre square; tables 2 and 3 sit on its top edge
            ly = oy + 7 * H + 18 if t in (5, 6) else oy - 6
            out.append(
                f'<text x="{ox + 3.5 * cw}" y="{ly}" font-size="15" text-anchor="middle" '
                f'fill="{INK}">{t}</text>'
            )
        opts = pl["tables"].get(str(t), {}).get("options_per_cell", {})
        for c in tabs[t]["cells"]:
            i = (c["row"] - 1) * 7 + c["col"] - 1
            x, y = ox + (c["col"] - 1) * cw, oy + (c["row"] - 1) * H
            cls = tabs[t]["cls"][i]
            fill = "#ffffff"
            if c["state"] == "lost":
                fill = LOST
            elif c["state"] == "fragment":
                fill = FRAG
            stroke, sw = (ANOM, 2.2) if cls == "uncertain" else (INK, 0.8)
            out.append(
                f'<rect x="{x}" y="{y}" width="{cw}" height="{H}" fill="{fill}" stroke="{stroke}" '
                f'stroke-width="{sw}"/>'
            )
            colour = RED if c["ink"] == "red" else INK
            text = (c["number_raw"] or "") + (c["letter"] or "")
            fs = 15 if cw == W else 11.5
            if text:
                out.append(
                    f'<text x="{x + cw / 2}" y="{y + (20 if opts.get(f"r{c['row']}c{c['col']}") else 29)}" '  # noqa: E501
                    f'font-size="{fs}" text-anchor="middle" fill="{colour}">{escape(text)}</text>'
                )
            key = f"r{c['row']}c{c['col']}"
            if key in opts and c["state"] != "intact":
                o = opts[key]
                # at most two options per line, so the labels fit the half-width cells
                rows = [" ".join(o[i : i + 2]) for i in range(0, len(o), 2)]
                if len(o) > 3:
                    rows = [f"{len(o)} possible"]
                for j, label in enumerate(rows):
                    out.append(
                        f'<text x="{x + cw / 2}" y="{y + 30 + 8 * j}" font-size="6.5" '
                        f'text-anchor="middle" fill="#7a5a1a">{escape(label)}</text>'
                    )
    by = Y0 + 21 * H + 30
    t2, t3 = pl["tables"]["2"], pl["tables"]["3"]
    lines = [
        f"Table 2 lost entries: {', '.join(t2['absent'])} - {t2['n_placements']} possible placements "  # noqa: E501
        f"({t2['n_distinct_letter_patterns']} different letter patterns).",
        f"Table 3 lost entries: {', '.join(t3['absent'])} - {t3['n_placements']} possible placements "  # noqa: E501
        "allowed by the surviving fragments.",
        (
            "No construction rule passed the pre-registered held-out test, so no cell is restored "
            "(results/rules.json)."
            if not rules["gate_passed"]
            else f"Rules passing the gate: {', '.join(rules['gate_passed'])} (see placements.json)."
        ),
    ]
    for k, s in enumerate(lines):
        out.append(
            f'<text x="{X0}" y="{by + 20 * k}" font-size="13" fill="{INK}">{escape(s)}</text>'
        )
    out.append("</svg>")
    (st_data.RESULTS / "seven_tables_cross.svg").write_text("\n".join(out))
    print("wrote results/seven_tables_cross.svg")


if __name__ == "__main__":
    main()
