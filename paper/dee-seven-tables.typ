// Working paper for the dee-seven-tables repository. Build: paper/build.sh
#set document(title: "The lost cells of John Dee's Seven Tables of Creation cannot be placed: a test of 20 layout rules", author: "Brett Burford")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), numbering: "1")
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt, lang: "en", region: "au")
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")
#show heading: set block(above: 1.3em, below: 0.7em)
#show link: set text(fill: rgb("#1a4f8b"))
#set table(stroke: 0.4pt + luma(150), inset: 5pt)
#show table: set text(size: 9.2pt)
#show table: set par(justify: false)

#align(center)[
  #text(size: 16pt, weight: "bold")[The lost cells of John Dee's Seven Tables of Creation cannot be placed: a test of 20 layout rules]
  #v(0.5em)
  #text(size: 11pt)[Brett Burford]
  #v(0.2em)
  #text(size: 9pt)[ORCID #link("https://orcid.org/0009-0003-6599-8297")[0009-0003-6599-8297] · Independent researcher, Australia]
  #v(0.2em)
  #text(size: 9pt)[Working paper, version 1.0.1, 21 October 2026 (version 1.0, 19 October 2026) · not peer reviewed]
  #v(0.2em)
  #text(size: 9pt)[Code, data and results: #link("https://github.com/BravoBravoIX/dee-seven-tables")[github.com/BravoBravoIX/dee-seven-tables]]
]

#v(0.8em)
#block(inset: (x: 1.2cm))[
  #text(weight: "bold")[Abstract.] On 29 April 1582 John Dee drew seven $7 times 7$ tables, joined as a cross, from which the names of 49 angels are read (British Library, Sloane MS 3188 ff. 37v–38r). The leaf is broken along its fold, and cells of tables 2 and 3 are lost. Every name is known, so the number and letter of each lost entry are known; what is lost is which cell each stood in. Whitby (1982) wrote that the positions "cannot be ascertained" because "there is no rule for individual placings". This note tests that statement. From a cell-by-cell transcription of Whitby's drawing (two reads by Claude, which differ at 2 of 343 cells; a machine witness agrees on 337 of 343 entries), the lost entries are 13R, 30R, 36N and 41A in table 2 and ten entries in table 3; the surviving fragments allow 6 and 1,080 placements. Twenty families of layout rules, fixed in advance, were scored on 720 legible cells hidden from them, against 20,000 copies of the tables with their numbers shuffled. No family passes after a Holm correction (best: $p = 0.013$, Holm $0.25$), so by the pre-registered stop rule no lost cell is placed. Two patterns seen earlier (consecutive numbers a knight's move apart in table 2, and king-adjacent in table 4) survive the checked transcription but not an allowance for how they were found, and remain leads only. The evidence does not decide where the lost entries stood, which agrees with Whitby.
]

= The problem

The figure is in Dee's record of his "actions" for 29 April 1582 (Sloane MS 3188 ff. 37b–38a, British Library foliation ff. 37v–38r). Seven $7 times 7$ tables form a cross: table 1 in the centre, tables 2 and 3 above it, 7 to the left, 4 to the right, 6 and 5 below (Figure 1). Each cell holds a number from 1 to 49 and a letter. Table 1 is 1B … 49B in reading order; table _t_ holds letter _t_ of each of the 49 names, tagged with the name's number, so name _k_ is read by collecting the cells numbered _k_ from the seven tables.

The leaf is broken along the fold, at the inner edges of tables 2 and 3 (and slightly in tables 1 and 5). When Elias Ashmole copied it in 1672 (Sloane MS 3677 ff. 57b–58a) he noted that "the spaces not filled up were decaied and broken away in the Originall". Some entries he could still read have since been destroyed.

The name-reading rule uses only the numbers, so it says nothing about where a cell sits. Only a rule for how the tables were laid out could place the lost entries. Christopher Whitby, who transcribed and drew the figure in his 1982 thesis, judged that there is none: "It is possible to an extent to reconstruct the missing parts of the table, but since there is no rule for individual placings within each small square in tables 2-7, the correct positions of the missing letters in the original cannot be ascertained" (vol. I p. 340). This note turns his judgment into a test.

= Sources and transcription

Every cell was read from Whitby's drawing (vol. II p. 121; a colour scan at 416 ppi in the open-access thesis), and the names from Dee's own list of the same day, the _Tabula Collecta_ (f. 40a; Whitby vol. II pp. 127–129). Whitby's commentary (vol. I p. 339) says he drew in red the entries that appear in Ashmole's copy but have since been lost from Dee's leaf. The red is therefore not Dee's ink, and it lies along the fold; cells left empty were already lost in 1672.

Two separate reads by Claude, with different crops, zoom and order, differ at 2 of 343 cells, both settled at higher zoom (22O, not 22D, in table 6; a red 6 in table 3's 46S). As a machine witness the Claude API read each table from a crop (12 calls; five of the first seven were refused, and a plainer prompt was answered). It agrees on 337 of 343 entries; 3 differences are notation for a lost digit and 3 are one letter shape, Whitby's flat-sided O, read as C or D. Its answers never change a reading. Anomalies are kept as read: table 2 43R (Dee's margin note corrects it), table 3 35R, table 5 39O, and table 6 19M (19 twice, 17 absent) and 23D. In the analysis an anomalous cell stays in place and its number is not used.

= The lost entries

#figure(
  image("../results/seven_tables_cross.svg", width: 100%),
  placement: top,
  caption: [The cross as Whitby drew it (our drawing, from `data/cells.csv`; no manuscript or thesis image is reproduced). Shaded: lost or fragmentary cells, with what survives and the entries that could stand there. Purple frame: anomalous entry (not fitting Dee's name list, or a number read twice). Red: known only from Ashmole's copy. No cell is restored.],
)

A placement puts each number absent from a table into one damaged cell, consistent with what survives there (a digit or a letter). Enumerating all of them gives Table 1.

#figure(
  table(
    columns: (auto, 1.5fr, 1.4fr, auto),
    align: (center, left, left, center),
    table.header([*Table*], [*Lost entries*], [*Fixed or narrowed by fragments*], [*Placements*]),
    [2], [13R, 30R, 36N, 41A], [the "N" is 36N], [6],
    [3], [4S, 5U, 6A, 13I, 19A, 28I, 37A, 38R, 44G, 48R], [5U and 37A fixed; the "A" is 6A or 19A; the "8" is 28I, 38R or 48R; the "1" is 13I or 19A], [1,080],
  ),
  caption: [Lost entries and the placements the fragments allow (`results/placements.json`). With Dee's margin correction applied, table 2 still has 6; if table 3's "35R" is a slip for 38R, table 3 has 720.],
)

Table 2's red "15", "17" and "23" keep their numbers and lose only their letters, so their cells are known. Whitby's own list is right for table 2; for table 3 it leaves out 13I and 28I and gives the "8" as 38R, though the "8" fits 28I and 48R as well. The only other list we found, by "Alan" in a comment on Cipher Mysteries (20 June 2025), has 15A, 30R, 41A and 18I, 19A, 38R, 44G, 48R. Its counts match the wholly empty cells, but 15A is not lost as an entry (only its letter is), 13R is missing although no 13 survives in table 2, and 18I is legible; it reads as a partial reading of Whitby's commentary, not a second witness. Our own unpublished first pass is also corrected: it took the red entries for Dee's ink, and it flagged table 7's 40L using a later spelling of the name (Dee's 1582 list has Bminpol).


= Method

The design was written down and committed before any rule was scored (`results/preregistration.md`); every random process uses the seed 20261019.

*Twenty rule families* each turn the visible cells of a table into a prediction for hidden cells: consecutive numbers placed by a chess-piece move (king, knight, wazir, ferz, dabbaba, alfil, camel, zebra; king and knight also on a wrap-around board); _k_ and _k_+7 side by side; Latin-square and clustering tendencies of the group of seven and the place in the group; a magic-square tendency; affine maps mod 7 (two numberings); reading orders with a stride (row, boustrophedon, spiral, diagonal, in all rotations and reflections); and one table copying another, rotated, reflected, shifted or with its numbers offset.

*Held-out test.* In each of tables 2–7, 20 folds each hide 6 legible cells (720 in all); each family predicts them from the rest, scoring the expected number right. *Controls:* 20,000 copies of the six tables with each table's legible numbers shuffled among its legible cells, damaged and anomalous cells fixed, scored the same way. *Decision:* a family passes if its pooled score beats the controls at a Holm-corrected $p < 0.05$ over the 20 families; only then may it place lost cells, and only in a table where it also beats its controls alone and gets at least half the hidden cells right. If none passes, stop.

= Results

#figure(
  table(
    columns: (1.6fr, 1fr, 1.2fr, auto, auto),
    align: (left, center, center, center, center),
    table.header([*Family*], [*Hidden cells right*], [*Controls (mean ± sd)*], [*p*], [*Holm p*]),
    [groups of seven kept together], [150.7], [119.9 ± 12.9], [0.013], [0.25],
    [knight walk], [147.0], [120.0 ± 14.7], [0.039], [0.75],
    [knight walk, wrap-around], [143.5], [119.9 ± 15.4], [0.069], [1],
    [ferz walk (diagonal)], [139.2], [120.0 ± 13.7], [0.087], [1],
    [16 other families], [at or near controls], [], [≥ 0.21], [1],
  ),
  caption: [The rule search, pooled over 720 hidden cells (`results/rules.json`). Chance is about 120 for the completion families and about 17 for the map families.],
)

No family passes, so by the stop rule no lost cell is placed. Per table (secondary), 8 of 120 tests reach $p < 0.05$, about what chance gives; the strongest are the knight walk in table 2 (39.4 of 120 hidden cells right against 20.1, $p = 0.0055$, a hit rate of 0.33, below the gate's 0.5) and _k_, _k_+7 side by side in table 3 (42.1 against 20.0, $p = 0.0030$).

*Two leads.* A first pass on a provisional reading had seen consecutive numbers a knight's move apart in table 2 (11 pairs against about 4, $p = 0.001$) and king-adjacent in table 4 (12 against about 6.4, $p = 0.019$). Re-tested as fixed tests on the checked transcription (100,000 shuffles, `results/hints.json`), table 2 has 10 knight pairs of 38 against 3.9 ($p = 0.0034$; 0.0068 for two tests) and table 4 has 12 king pairs of 48 against 6.4 ($p = 0.019$; 0.039). But both were picked from 12 looks (two moves in six tables) at nearly the same cells; allowing for all 12 leaves about 0.04 and 0.23. On hidden cells the knight walk gets a third of table 2 right and is not seen in the other tables. They are leads, not evidence of a rule.

= Discussion

*Verdict.* Which entries are lost is settled, with 6 placements in table 2 and 1,080 in table 3. No layout rule among the 20 families predicts hidden cells better than shuffled tables, and the evidence does not decide where the lost entries stood. This is Whitby's conclusion of 1982, now measured; his drawing and commentary are the basis of everything here. "Alan" (2025) tried to place the cells and found the line of inquiry "futile". Searches of the web, GitHub, Zenodo and Crossref (18–19 October 2026) found no positional reconstruction; Peterson's edition (2003) and studies by Harkness, Asprem and Laycock were not read. What is new is the machine-readable transcription with its witnesses, the exact lists and placement counts, and the pre-registered, controlled test.

*What a second witness could settle.* British Library images of Sloane 3188 and of Ashmole's copy, or Peterson's edition, might decide the three narrowed cells of table 3 (the "8", the "A" and the "1"), Dee's margin note, and whether the anomalies in tables 3, 5 and 6 are slips by Dee, Ashmole or Whitby. No witness can place an entry in a cell already empty in 1672; only a rule could.

*Limits.* The transcription is of Whitby's drawing, not the manuscript, so his slips would carry through; the machine witness checks our reading of his drawing, not his reading of Dee. A rule outside the 20 families could exist; the test shows only that the usual constructions (walks, squares, maps, reading orders, copies) are not supported. Even a strong rule could only weigh toward a placement, since the cells are physically gone.

= Data and code availability

Code (MIT), our transcription and all results (CC BY 4.0) are at #link("https://github.com/BravoBravoIX/dee-seven-tables")[github.com/BravoBravoIX/dee-seven-tables]. Whitby's thesis is not redistributed; a script downloads it and checks its SHA-256. From `data/` the pipeline rebuilds every results file byte for byte, apart from two run-record fields (the commit and the run time); the API witness reads are recorded results and are not rerun.

= How AI was used

The 343 cells were read from crops of Whitby's figure by Claude in two passes, with different crops, zoom and order; they differ at 2 cells, both settled at higher zoom. As a check, Claude (Anthropic, model Opus 5.5) read each table once more from a crop; it agrees on 337 of 343 entries and never changes a reading. An AI coding assistant (Claude Code) was used. Every step reruns without any AI service; Claude's readings are stored as data.

= Acknowledgements

This note stands on Christopher Whitby's transcription, drawing and commentary. The author is responsible for any errors.

= References

#set par(hanging-indent: 1.2em, justify: false)
#set text(size: 9.5pt)

"Alan" (2025). Comment of 20 June 2025 on N. Pelling, "John Dee's Tabula Angelorum Bonorum 49", _Cipher Mysteries_, 8 June 2025. #link("https://ciphermysteries.com/2025/06/08/john-dees-tabula-angelorum-bonorum-49")[ciphermysteries.com/2025/06/08/john-dees-tabula-angelorum-bonorum-49].

British Library, Sloane MS 3188, ff. 37b–38a, 40a; Sloane MS 3677, ff. 57b–58a.

Peterson, J. H. (ed.) (2003). _John Dee's Five Books of Mystery_. Boston: Weiser. (Not read for this note.)

Whitby, C. (1982). _John Dee's actions with spirits, 22 December 1581 to 23 May 1583_. PhD thesis, University of Birmingham, 2 vols. #link("https://etheses.bham.ac.uk/id/eprint/3149/")[etheses.bham.ac.uk/id/eprint/3149].
