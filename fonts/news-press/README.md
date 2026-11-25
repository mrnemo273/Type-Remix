# News Press (variable)

Formerly Newsreader Letterpress.

Newsreader by Production Type with a letterpress treatment, for a newspaper look, rebuilt as a variable font from the
static cuts (Display, H1, H2) in `Type/Assets`. Measured from those files and copied onto an axis.

## Axes
| Tag | Name | Range | Default | Notes |
|---|---|---|---|---|
| `wght` | Weight | 200–800 | 400 | from Newsreader |
| `PRES` | Press | 0–100 | 50 | 0 = the Display cut ("Kiss"), 50 = H1 ("Press"), 100 = H2 ("Heavy") |

Roman and italic. Optical size is fixed at 16, the setting all three static cuts were made from
(Newsreader's opsz axis was dropped to keep each web font around 2 MB instead of 6–7 MB).

## Method (tools/press.py)
- Every outline is resampled into ~10-unit straight facets (all on-curve points), identically in every master.
- Facet points move in/out along the edge normal by smoothed gaussian noise, with knots every 11 / 16 / 20 units
  and spread 8 / 12 / 14 units at Press 0 / 50 / 100 (2000 UPM), as measured from the static cuts.
  v2: Press 100 is softer than the H2 cut (knots every 24 units, spread 12.5, rounder smoothing) so it is lumpy rather than jagged.
- Thin strokes: both sides move more together, and no edge moves more than a third of the local stroke.
- Specks (knockouts): 60 / 30 / 14 per million square units, about 12 / 22 / 34 units across, slightly
  elongated 5–8-sided shapes. Every speck exists in every master and collapses to a point where unused.
- Masters: weight 200/400/800 × Press 0/50/100 (9 per style). Composites kept.

    python3 tools/press.py roman italic     # needs src/Newsreader[opsz,wght].ttf and the italic

Licence: SIL Open Font License 1.1 (OFL.txt). Newsreader has no Reserved Font Name.
