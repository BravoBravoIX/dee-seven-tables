# Sources of the data

| What | Where | Rights |
|---|---|---|
| Whitby, *John Dee's actions with spirits, 22 December 1581 to 23 May 1583* (PhD, University of Birmingham, 1982), vol. II | https://etheses.bham.ac.uk/id/eprint/3149/2/Whitby82PhD2.pdf, fetched 19 Oct 2026; SHA-256 in `sources/SHA256SUMS` | Open-access thesis; copyright with the author. Not redistributed; `scripts/fetch_sources.sh` downloads it. |
| The cross figure, vol. II p. 121 (Sloane MS 3188 ff. 37b–38a; BL ff. 37v–38r) | PDF page 132, its embedded colour JPEG (4380 × 3438, 416 ppi), extracted with `pdfimages -j` | as above; no image of it is in this repository |
| Dee's list of the 49 names, *Tabula Collecta* (Sloane MS 3188 f. 40a) | vol. II pp. 127–129 (PDF pp. 138–140) | the names are facts of a sixteenth-century text |
| Whitby's conventions | vol. II p. vi §§14–16: red ink noted in the commentary (§15); readings from Ashmole's transcript (Sloane MS 3677) in pointed brackets (§16); Dee's own brackets are square | as above |
| Whitby vol. I (introduction and commentary) | https://etheses.bham.ac.uk/id/eprint/3149/1/Whitby82PhD1.pdf, fetched 19 Oct 2026. Commentary to ff. 37b–38a on pp. 339–340 (PDF pp. 354–355): red in the drawing marks entries in Ashmole's copy (Sloane MS 3677 ff. 57b–58a) since destroyed in Dee's leaf | as above; quoted briefly |
| "Alan", comment of 20 June 2025 on Cipher Mysteries, "John Dee's Tabula Angelorum Bonorum 49" | https://ciphermysteries.com/2025/06/08/john-dees-tabula-angelorum-bonorum-49 (read 19 Oct 2026) | cited for comparison only |

Files here:
- `reads.txt`: two independent eye reads of the figure, cell by cell (our own work).
- `cells.csv`: the reconciled transcription, 343 cells, rebuilt from `reads.txt` by `code/build_cells.py`.
- `names.csv`: Dee's 49 names as listed on f. 40a, with page references.

All three are our own record of a sixteenth-century table, published under CC BY 4.0. Please cite Whitby's drawing as their source as well as this repository.
