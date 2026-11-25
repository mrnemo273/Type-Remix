# Type specimens

One template, one settings file per font. The build script reads the font itself
(axes, metrics, characters, OpenType features, outlines) and writes a specimen page,
then refreshes the catalogue (`index.html`) that lists every font.

## Add a font
1. Put the variable TTF in `Type/fonts/<slug>/fonts/`.
2. Write `specimen/configs/<slug>.json`. Only two fields are required:
   ```json
   { "name": "My Font", "font": "../../fonts/my-font/fonts/MyFont[wght].ttf" }
   ```
3. Build it:
   ```
   cd ~/Desktop/Experiments/Type/specimen
   python3 tools/build_specimen.py configs/my-font.json
   ```
4. Preview (pages load their data, so they need a local server, not a double-click):
   ```
   python3 -m http.server 8000
   ```
   then open http://localhost:8000

Needs `pip install fonttools brotli`. TrueType (glyf) variable fonts; static fonts work but
skip the axis sections.

## What fills itself in
- Hero: the name, sized to the page, every letter cycling through every axis.
- What's in the font: one cell per axis, character count, feature count.
- Scroll test, outline loupe with a pad over the first two axes, axis matrix, print run.
- Features: every stylistic set, character variant and common feature in the font, with
  samples picked automatically (override in `features.samples`).
- In use (a set of mockups chosen per font) and overprint (6 compositions), set in the font.
- Characters: every mapped glyph with its point count.

Sections only appear when the font supports them.

## Optional settings (see configs/grex-sans.json for a full example)
| Key | What it does |
|---|---|
| `slug`, `version`, `tagline` | Folder name, version label, line under the name |
| `axes.<tag>` | `label`, `from`, `to`, `desc` for each axis |
| `ui`, `display` | Axis settings for running text and for headlines |
| `base` | `{name, path}` of the font it was built from, for point-count comparisons |
| `heroMotion` | `style: "smooth"` (continuous wave, `speed`) or `"staccato"`: the whole name clicks to one new random setting, letter by letter, then pauses. `hold` seconds between clicks, `stagger` ms between letters, `press` depth in em, `duration` ms, `steps` positions per axis, `floor` minimum per axis (e.g. `{"GRAN": 25}`) |
| `heroTracking` | Letter spacing for the hero name in em (default 0); pair kerning is always kept |
| `drawn` | `{word, axes}` for the outline loupe |
| `size` | `{axis, fromPx, toPx, reverse, title, text, sentence}` adds the "follows size" ladder; `reverse:true` puts the top of the axis on the small sizes |
| `matrix`, `run`, `inuse`, `overprint`, `features`, `characters`, `scroll`, `loupe` | Titles and copy; `inuse.axis` picks the axis the mockups vary (`inuse.min`/`inuse.max` limit its range); `show:false` hides a section. `overprint.style:"edges"` swaps the six compositions for edge proofs: one letter printed twice in register at two settings of `overprint.axis` (`from`/`to`, default the axis min and max; `mid` for the three-pass card), cropped on corners, stems and counters. Use it for fonts whose character is in the outline rather than texture. `overprint.style:"news"` swaps them for newspaper print artifacts on newsprint (off register, show-through, press run, the fold, spot colour, Extra!), with optional `headlines`, `masthead`, `body` and `extra`. `inuse.cards` lists which mockups to show, by id (default: the original fourteen). Sets in `template/inuse.js`: general (coffee, gig, book, record, ticket, editorial, can, sign, tee, card, menu, stamp, post, app), newspaper (front, bill, letters, crossword, scores, markets, listings, review, classifieds, forecast, subscribe, tote) and handmade (seeds, jam, studio, marker, zine, pricecard, repairtag, workshop, notebook, carelabel, cider, window). Give each font its own set so specimens don't repeat |
| `italic` | Path to the italic font: adds an Italic section |
| `italicSection` | `{title, text, sample}` for that section |
| `files`, `license` | Footer text |
