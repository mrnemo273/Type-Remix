# Worked Sans — v8

Work Sans Rough, made variable. The roughening is modelled on JC's original Work Sans Rough
(Medium/Bold, measured point by point): every corner becomes a small round (~30 units), straight
edges are cut into ~47-unit facets each pushed off the line by a little (avg 1.6, max 4.6 units),
and curve points are nudged ~2.5 units. No lean, no waves. At WORK 0 it is exactly Work Sans;
at WORK 100 it matches Work Sans Rough. On the thinnest weights the two sides of a stroke mostly
move together so strokes never pinch.

## Axes
| Axis | Tag | Range | Default | |
|---|---|---|---|---|
| Weight | `wght` | 100–900 | 400 | Work Sans' own weight curve kept |
| Worked | `WORK` | 0–100 | 100 | 0 = exactly Work Sans, 100 = fully worked in |

Roman and italic, each one variable file. Named instances Thin to Black (and Italic
equivalents) at WORK 100. Work Sans' heavy-weight alternates ($, ¢, ¶ and a few others)
still switch in at the same weights.

```css
@font-face { font-family: 'Worked Sans'; src: url(fonts/WorkedSans[WORK,wght].woff2) format('woff2'); font-weight: 100 900; font-style: normal; }
@font-face { font-family: 'Worked Sans'; src: url(fonts/WorkedSans-Italic[WORK,wght].woff2) format('woff2'); font-weight: 100 900; font-style: italic; }
h1 { font-family: 'Worked Sans'; font-variation-settings: 'WORK' 100; }
```

## How it stays variable
Each corner becomes a short curve (on, off, on) in every master; at WORK 0 those points sit
exactly on the original corner. Each long line gets one control point that sits on the line
at WORK 0. Radii are a share of the stem, so they track weight, and each corner draws its
own random share (seeded by glyph name, so builds are repeatable). Accented letters stay
built from shared parts, so they wear exactly like their base letters.

## Changes
- v8: rebuilt to match Work Sans Rough's method exactly (faceted edges, small even rounding), made variable across the whole family. Earlier waves, lean and tilted ends retired. Knobs: `radius`, `facet`, `edge_sd`, `curve_sd`, `light_stem`.
- v7: every corner drifts with the shared hand field (mostly sideways), so verticals lean; stronger S-curves on long lines; stroke-end tilt toned down with fewer extremes. Knobs: `corner_drift`, `bow`, `node_jitter`, `cap_tilt`.
- v6: stroke ends are no longer flat cuts: each end tilts by its own small amount and gets a slight bulge or dent. Knobs: `cap_tilt`, `cap_bulge`, `cap_max`.
- v5: back to v3's overall rounding, with the minimum raised so no corner stays sharp (radius share 0.55–1.1, cap 34, floor 0.25). v4's wide range is retired.
- v4: wider, skewed corner range: most corners stay modest, some round off much more (up to 2.8× the base radius, 72 units). Knobs: `radius_spread`, `radius_skew`, `radius_cap`.
- v3: the wobble comes from one shared 'hand movement' field per letter, so both sides of a stroke move the same way and thin strokes keep their thickness (no pinching). Knob: `field`.
- v2: straight lines become waves of 1–3 pieces sized to the line, not the stroke, so Thin gets as much hand as Black; curve handles nudged slightly. Knobs: `bow`, `wave_len`, `node_jitter`, `curve_jitter`.
- v1: uneven corner fillets and a single subtle bow per line.

## Rebuild
```
pip install fonttools brotli pillow
python3 tools/worked.py            # roman and italic (all knobs in the P dict at the top)
python3 tools/proof.py proofs/new.png
```
Run from this folder; expects `src/WorkSans[wght].ttf` and `src/WorkSans-Italic[wght].ttf`
(github.com/google/fonts, ofl/worksans).

## Licence
SIL Open Font License 1.1. Work Sans has no Reserved Font Name. Keep OFL.txt with the files.
