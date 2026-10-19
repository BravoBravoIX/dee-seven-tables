# Seven Tables of Creation: pre-registration of the rule search (T1)

> Public copy. The text is as committed in the author's working repository on 19 October 2026 at 11:30 UTC, before any rule was scored, except that a reference to an unpublished internal file is replaced by a description of it, and "Brett's request" reads "the author's request". Section 9's reference to `README.md` means the study's README.

Written 19 October 2026, before any rule was scored on the checked transcription (`data/cells.csv`). Committed to git before `code/rules.py`, `code/hints.py` or `code/placements.py` was run on real data. Control counts were raised (20,000 rule-search shuffles, 100,000 for the hints) at the author's request before any real run. The only runs before this commit were timing and sanity runs of `code/rules.py --synthetic` on random and constructed tables (no Dee data).

What was known before writing this: the first-pass hints in the author's unpublished first-pass note of 18 October 2026, §A (no affine fit; table 4 king-adjacent pairs 12 against about 6.4, p = 0.019; table 2 knight-move pairs 11 against about 4, p = 0.001), all on a provisional transcription. Those hints were found by looking, so they cannot confirm themselves; see H1 and H2 below.

## 1. Data and cell classes

- Input: `data/cells.csv` (343 cells) and `data/names.csv` (49 names), SHA-256 recorded in every results file.
- Each cell of tables 2–7 is put in one class (`code/st_data.py`):
  - **scorable**: the number is fully legible (state `intact`, or a `fragment` that lost only its letter, such as table 2's red "15", "17" and "23"), the letter, where legible, equals letter *t* of name *k* (table *t*, number *k*; U and V count as one letter), and the number occurs once in that table;
  - **uncertain**: intact but anomalous (the letter does not fit the name, or the number is read twice in the table, or the number is unreadable). It stays in place, is never hidden, and its number is not used by any rule;
  - **damaged**: state `lost`, or a `fragment` whose number is not fully legible. Position fixed; number treated as unknown.
- Names: Dee's own list of 29 April 1582 (Sloane 3188 f. 40a, Whitby vol. II pp. 127–129), `data/names.csv`.
- Table 1 (1B … 49B in reading order) is used only as a source table for the shared-layout family.
- Anomalies are kept exactly as read in `cells.csv`. No emendation is used in the primary analysis.

## 2. Rule families (20, fixed here)

Every family turns the visible cells of one table into a prediction of which number stood in each hidden cell.

**Completion families.** The hidden numbers are known as a set (they are the numbers missing from the visible cells). Every assignment of the hidden numbers to the hidden cells is scored by an objective on the whole table; the best assignments are kept (all ties).

| Family | Objective (maximised) |
|---|---|
| `walk_king` | consecutive numbers *k*, *k*+1 king-adjacent (plain board) |
| `walk_knight` | *k*, *k*+1 a knight's move apart |
| `walk_wazir` | *k*, *k*+1 orthogonally adjacent |
| `walk_ferz` | *k*, *k*+1 diagonally adjacent |
| `walk_dabbaba` | *k*, *k*+1 two steps orthogonally |
| `walk_alfil` | *k*, *k*+1 two steps diagonally |
| `walk_camel` | *k*, *k*+1 a (1,3) leap |
| `walk_zebra` | *k*, *k*+1 a (2,3) leap |
| `walk_king_torus` | king-adjacent with wrap-around edges |
| `walk_knight_torus` | knight's move with wrap-around edges |
| `step7_king` | *k*, *k*+7 king-adjacent (the names come in planetary groups of seven) |
| `latin_q` | Latin-square tendency of the group index q = (k−1) div 7: distinct q values per row and column, summed |
| `latin_s` | the same for the place-in-group s = (k−1) mod 7 |
| `cluster_q` | the opposite of `latin_q` (groups kept together in rows and columns) |
| `cluster_s` | the opposite of `latin_s` |
| `magic` | magic-square tendency: −Σ over rows and columns of n·(mean − 25)², n the known cells in the line |

**Map families.** A map from position to number is fitted on the visible cells (the map that matches the most visible cells wins; all tied maps kept) and read off at the hidden cells.

| Family | Maps |
|---|---|
| `affine_base0` | cell (r, c) = A·(q, s) + b mod 7, A any invertible 2×2 matrix mod 7 (2,016), b any of 49 offsets; q, s from k−1 |
| `affine_base1` | the same with q = (k div 7) mod 7, s = k mod 7 (numbering from 0 or 1 is not affine-equivalent) |
| `order_stride` | number at place *i* of a reading order = (a·*i* + b) mod 49 + 1, a a unit mod 49 (42 values), b any; reading orders: row, boustrophedon, inward spiral, diagonal, zigzag diagonal, each in all 8 rotations and reflections (reverse orders are a = −1) |
| `shared_layout` | the table copies another table (1–7, as read): number_t(p) = number_s(g(p)) + c mod 49, g one of the 8 rotations/reflections combined with one of 49 wrap-around shifts, c any of 49 |

Why these: affine maps, walks, Latin and magic squares and reading orders are how 16th-century number squares were built (magic squares of the planets, Agrippa's tables, knight tours, the Soyga tables); a layout shared or shifted between tables would be the simplest "one rule for seven tables"; `step7_king` and the q/s families test whether the planetary grouping of the names shaped the layout.

## 3. Held-out scheme

- Tables 2–7 each get 20 folds. A fold hides 6 scorable cells chosen at random (numpy `default_rng([20261019, 0])`, drawn once, in table order 2…7).
- Score per fold: the expected number of hidden cells predicted correctly, averaging over tied best fits.
- Statistic per family: the sum over the 120 folds (720 hidden cells). Chance for a completion family is about 1 per fold.

## 4. Controls

- For each control replicate, each table's scorable numbers are shuffled among its scorable positions (damaged and uncertain cells stay fixed, so each table keeps its damage pattern). The same folds (hidden positions) are used.
- 20,000 replicates, in work units of 100; unit *u* uses `default_rng([20261019, 1, u])`, so the result does not depend on how many processes run it (6 processes, `nice -n 19`). For `shared_layout` the source tables are left as read.
- p = (1 + number of replicates scoring at least the real value) / 20,001, one-sided. The smallest possible p (5 × 10⁻⁵) is well below the smallest Holm threshold (0.0025).

## 5. Multiple testing and the decision rule

- **Primary test:** per family, the pooled statistic over tables 2–7. Holm correction over the 20 families, family-wise α = 0.05. A family **passes** if its Holm-adjusted p < 0.05.
- **Gate for applying a rule to the lost cells** of table 2 or table 3 (both needed):
  1. in that table alone, the family beats its controls at p < 0.05 / (2 × number of passing families) (Bonferroni over the passing families and the two damaged tables);
  2. in that table, it predicts at least half of the hidden cells correctly (held-out accuracy ≥ 0.5). A rule that beats chance but gets most cells wrong cannot place lost cells.
- Per-table results for all families are reported in full but are secondary.

## 6. The two first-pass hints, as fixed tests

- **H1:** table 2, the count of pairs *k*, *k*+1 (both scorable) a knight's move apart on the plain board.
- **H2:** table 4, the count of pairs *k*, *k*+1 king-adjacent.
- Null: 100,000 shuffles of each table's scorable numbers among its scorable positions (`code/hints.py`, `default_rng(20261019)`). One-sided p, reported raw and Bonferroni ×2.
- These two hints were found by looking at 12 tests on almost the same cells. Re-running them on the checked transcription tests whether they survive the checking. It is **not** an independent replication and cannot by itself support a rule. Only the held-out test in §5 can do that. The full 12-test grid is reported for context.

## 7. Outcome and stop rule

- **No family passes (§5):** stop. Outcome (c), "the evidence does not decide". The write-up lists the lost entries, the possible placements (enumerated exhaustively, with the fragments as the only constraint, `code/placements.py`) and the anomalies.
- **A family passes but fails the gate for a damaged table:** outcome (c) for that table, with the rule reported as structure only.
- **A family passes the gate:** enumerate every placement of that table's lost entries consistent with the fragments, score each with the family's objective (completion family) or check it against the fitted maps (map family), and report:
  - (a) a unique reconstruction if one placement is best;
  - (b) the best-supported of several, with the count of tied placements and how they differ.
  - Wording: "the evidence weighs toward"; the cells are physically lost and nothing can confirm a placement.
- No new family, objective, fold size or control may be added after the first real run without a new, dated pre-registration section, and any such later result is labelled exploratory.

## 8. Sensitivity (reported, does not change the decision)

- Rerun §5 with the anomalous cells included at their numbers as read (the first of a duplicated number kept as scorable, by reading order). Reported only if a family passes the primary test, as a check that the anomaly handling does not drive it.

## 9. Transcription variants (reported, do not change the decision)

- The placement counts in §7 are also given for two variants, without changing the primary data:
  - table 3 "35R" read as a slip for 38R (then 35 is the lost number and 38 is not);
  - the lost-entry lists "Alan" gives (Cipher Mysteries, 20 June 2025), which differ from Whitby's drawing (see `README.md`).
