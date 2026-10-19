#!/usr/bin/env bash
# Download the sources this study was read from, into SOURCE_DIR, and check them against the
# SHA-256 sums of the copies used for the published transcription.
# They are not redistributed here: Whitby's thesis is open access, but copyright stays with
# the author. The analysis itself (code/run_all.sh) reads only data/; these files are for
# checking the transcription against the drawing.
# Needs curl; pdfimages (poppler) to extract the figure.
# Usage: scripts/fetch_sources.sh SOURCE_DIR
set -euo pipefail
SUMS="$(cd "$(dirname "$0")/.." && pwd)/sources/SHA256SUMS"
OUT="$1"
mkdir -p "$OUT"
get() { [ -s "$2" ] || curl -fsSL --retry 3 -o "$2" "$1"; }

# Christopher Whitby, "John Dee's actions with spirits, 22 December 1581 to 23 May 1583",
# PhD thesis, University of Birmingham, 1982. University of Birmingham eTheses Repository,
# https://etheses.bham.ac.uk/id/eprint/3149/
#   vol. I: introduction and commentary (ff. 37b-38a on pp. 339-340, PDF pp. 354-355)
#   vol. II: the transcription; the cross figure on p. 121 (PDF p. 132); Dee's list of the
#            49 names (Tabula Collecta, f. 40a) on pp. 127-129 (PDF pp. 138-140)
get https://etheses.bham.ac.uk/id/eprint/3149/1/Whitby82PhD1.pdf "$OUT/Whitby82PhD1.pdf"
get https://etheses.bham.ac.uk/id/eprint/3149/2/Whitby82PhD2.pdf "$OUT/Whitby82PhD2.pdf"

# The figure as embedded in the PDF: a colour JPEG, 4380 x 3438 pixels (416 ppi)
if command -v pdfimages >/dev/null; then
  pdfimages -f 132 -l 132 -j "$OUT/Whitby82PhD2.pdf" "$OUT/p132"
  mv -f "$OUT/p132-000.jpg" "$OUT/vol2_p121_figure.jpg"
else
  echo "pdfimages not found: the figure was not extracted" >&2
fi

cd "$OUT"
if sha256sum --quiet -c "$SUMS"; then
  echo "all sources match the copies used for the published transcription"
else
  echo "WARNING: a source differs from the copy used for the published transcription." >&2
fi
