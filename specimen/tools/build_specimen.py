#!/usr/bin/env python3
"""Build a type specimen page for one variable font.

    python3 tools/build_specimen.py path/to/specimen.json

The config only needs "name" and "font"; everything else has defaults or is read
from the font itself (axes, metrics, characters, features, outlines). Output goes to
<specimen root>/<slug>/ and the catalogue (<specimen root>/index.html) is refreshed.

Requires: pip install fonttools brotli
TrueType-flavoured fonts (glyf) only; CFF/OTF outlines are not supported by the outline view.
"""
import json, os, re, shutil, sys, itertools, tempfile
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../specimen
TEMPLATE = os.path.join(ROOT, 'template')

SKIP_FEATURES = {'aalt', 'ccmp', 'locl', 'rvrn', 'mark', 'mkmk', 'kern', 'rlig', 'init', 'medi', 'fina',
                 'isol', 'numr', 'dnom', 'lnum', 'pnum', 'sinf', 'salt', 'dist', 'abvm', 'blwm', 'curs'}
KNOWN = {  # tag: (name, sample, highlight regex)
    'onum': ('Oldstyle figures', 'Since 1974, 2,368 copies', r'\d'),
    'tnum': ('Tabular figures', '1,111.10 / 9,876.54', r'\d'),
    'frac': ('Fractions', 'Add 3/4 cup', r'3/4'),
    'sups': ('Superscript', 'E=mc2', r'2'),
    'subs': ('Subscript', 'H2O and CO2', r'2'),
    'ordn': ('Ordinals', '1a 2o', r'\d[ao]'),
    'liga': ('Ligatures', 'office fish', r'ffi|fi|fl'),
    'dlig': ('Discretionary ligatures', 'Act fast', r'ct|st'),
    'zero': ('Slashed zero', 'Room 1050', r'0'),
    'smcp': ('Small capitals', 'Small Caps', r'[a-z]'),
    'c2sc': ('Capitals to small caps', 'NASA and UNESCO', r'[A-Z]'),
    'case': ('Case-sensitive forms', '(HELLO) [WORLD]', r'[()\[\]]'),
    'calt': ('Contextual alternates', '', ''),
}
WORDS = ('Papaya banana', 'Giggling geography', 'Room 1050', 'Code 0040', 'Straße', 'Illinois 1,111',
         'Quick jumpy fox', 'Rye & caraway', 'Ways to say yes', 'Kept the keys', 'Every year', 'Ready, steady, go')
BUILTIN_SS = {'ss01': 'Stylistic set 1', 'ss02': 'Stylistic set 2', 'ss03': 'Stylistic set 3', 'ss04': 'Stylistic set 4',
              'ss05': 'Stylistic set 5', 'ss06': 'Stylistic set 6', 'ss07': 'Stylistic set 7', 'ss08': 'Stylistic set 8'}

def nm(font, i):
    return font['name'].getDebugName(i) if i is not None else None

def count_pts(glyf, gname):
    g = glyf[gname]
    if g.numberOfContours == 0:
        return 0
    return len(g.getCoordinates(glyf)[0])

def feature_list(font, cfg):
    if 'GSUB' not in font:
        return []
    gsub = font['GSUB'].table
    cmap = font.getBestCmap(); rev = {}
    for u, g in cmap.items():
        rev.setdefault(g, chr(u))
    out, seen = [], set()
    samples = cfg.get('features', {}).get('samples', {})
    names = cfg.get('features', {}).get('names', {})
    for fr in gsub.FeatureList.FeatureRecord:
        tag = fr.FeatureTag
        if tag in seen or (tag in SKIP_FEATURES and tag not in samples):
            continue
        seen.add(tag)
        affected = set()
        for li in fr.Feature.LookupListIndex:
            for st in gsub.LookupList.Lookup[li].SubTable:
                st = getattr(st, 'ExtSubTable', st)
                if hasattr(st, 'mapping'):
                    affected |= {rev[k] for k in st.mapping if k in rev}
                elif hasattr(st, 'alternates'):
                    affected |= {rev[k] for k in st.alternates if k in rev}
                elif hasattr(st, 'ligatures'):
                    affected |= {rev[k] for k in st.ligatures if k in rev}
        uiname = None
        params = getattr(fr.Feature, 'FeatureParams', None)
        if params is not None and getattr(params, 'UINameID', None):
            uiname = nm(font, params.UINameID)
        if tag in samples:
            sample = samples[tag]; hl = re.escape(''.join(sorted(affected))) if affected else '.'
            hl = KNOWN.get(tag, (None, None, None))[2] or ('[' + hl + ']' if affected else '.')
            name = names.get(tag) or uiname or KNOWN.get(tag, (BUILTIN_SS.get(tag, tag),))[0]
        elif tag in KNOWN and KNOWN[tag][1]:
            name, sample, hl = KNOWN[tag]
        elif re.match(r'(ss|cv)\d\d', tag) and affected:
            sample = next((w for w in WORDS if any(c in w for c in affected)), ''.join(sorted(affected))[:14])
            hl = '[' + re.escape(''.join(sorted(affected))) + ']'
            name = names.get(tag) or uiname or (f'Character variant {tag[2:]}' if tag.startswith('cv') else BUILTIN_SS.get(tag, tag))
        else:
            continue
        out.append(dict(tag=tag, name=names.get(tag) or name, sample=sample, hl=hl))
    order = lambda f: (0 if re.match(r'ss\d\d', f['tag']) else 1 if re.match(r'cv\d\d', f['tag']) else 2, f['tag'])
    return sorted(out, key=order)

def outline_grid(path, word, axis_tags, axes):
    """Outline coordinates of `word` at normalized -1/0/+1 on each drawn axis (others at default)."""
    base = TTFont(path)
    cmap = base.getBestCmap()
    chars = [c for c in word if ord(c) in cmap]
    sub = TTFont(path)
    opts = subset.Options(); opts.layout_features = []; opts.notdef_outline = False; opts.glyph_names = True
    ss = subset.Subsetter(opts); ss.populate(unicodes=[ord(c) for c in set(chars)]); ss.subset(sub)
    fd, tmp = tempfile.mkstemp(suffix='.ttf'); os.close(fd); sub.save(tmp)
    stops = {}
    for t in axis_tags:
        a = axes[t]; st = [0]
        if a['min'] < a['default']: st.insert(0, -1)
        if a['max'] > a['default']: st.append(1)
        stops[t] = st
    keys = list(itertools.product(*[stops[t] for t in axis_tags]))
    glyphs = [dict(ch=c, ends=None, flags=None, m={}, adv={}) for c in chars]
    for key in keys:
        loc = {}
        for t, n in zip(axis_tags, key):
            a = axes[t]; loc[t] = a['default'] if n == 0 else (a['min'] if n < 0 else a['max'])
        for t, a in axes.items():
            loc.setdefault(t, a['default'])
        f = instancer.instantiateVariableFont(TTFont(tmp), loc) if axes else TTFont(tmp)
        glyf = f['glyf']; cm = f.getBestCmap(); k = ','.join(str(n) for n in key)
        for g in glyphs:
            gname = cm[ord(g['ch'])]
            gg = glyf[gname]
            if gg.numberOfContours:
                coords, ends, flags = gg.getCoordinates(glyf)
                if g['ends'] is None:
                    g['ends'] = list(ends); g['flags'] = [int(x) & 1 for x in flags]
                g['m'][k] = [int(round(v)) for xy in coords for v in xy]
            else:
                g['ends'] = g['ends'] or []; g['flags'] = g['flags'] or []; g['m'][k] = []
            g['adv'][k] = f['hmtx'][gname][0]
    os.remove(tmp)
    return dict(word=''.join(chars), axes=axis_tags, stops=stops, glyphs=glyphs)

def edge_boxes(font, axes, cfg):
    """Bounding boxes (font units) of A-Z, a-z and & at a few weights, for the edge-proof overprint cards."""
    from fontTools.pens.boundsPen import BoundsPen
    cmap = font.getBestCmap()
    chars = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz&' if ord(c) in cmap]
    w = axes.get('wght')
    weights = sorted({w['min'], min(max(400, w['min']), w['max']), min(max(700, w['min']), w['max']), w['max']}) if w else [None]
    out = {}
    for wt in weights:
        loc = {t: a['default'] for t, a in axes.items()}
        if wt is not None:
            loc['wght'] = wt
        gs = font.getGlyphSet(location=loc)
        row = {}
        for c in chars:
            g = cmap[ord(c)]; bp = BoundsPen(gs); gs[g].draw(bp)
            if bp.bounds:
                row[c] = [round(v) for v in bp.bounds] + [round(gs[g].width)]
        out[str(int(wt)) if wt is not None else 'default'] = row
    return out

def build(cfg_path):
    cfg_dir = os.path.dirname(os.path.abspath(cfg_path))
    cfg = json.load(open(cfg_path))
    name = cfg['name']; slug = cfg.get('slug') or re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    font_path = os.path.normpath(os.path.join(cfg_dir, cfg['font']))
    font = TTFont(font_path)
    if 'glyf' not in font:
        sys.exit('Only TrueType (glyf) fonts are supported for now.')
    axes = {}
    if 'fvar' in font:
        avar = font['avar'].segments if 'avar' in font else {}
        for a in font['fvar'].axes:
            seg = avar.get(a.axisTag)
            seg = sorted([[k, v] for k, v in seg.items()]) if seg and any(abs(k - v) > 1e-6 for k, v in seg.items()) else None
            axes[a.axisTag] = dict(tag=a.axisTag, name=nm(font, a.axisNameID), min=a.minValue, default=a.defaultValue,
                                   max=a.maxValue, avar=seg)
    os2 = font['OS/2']; hh = font['hhea']
    glyf = font['glyf']; cmap = font.getBestCmap()
    base_glyf = base_cmap = None
    if cfg.get('base', {}).get('path'):
        bf = TTFont(os.path.normpath(os.path.join(cfg_dir, cfg['base']['path'])))
        base_glyf, base_cmap = bf['glyf'], bf.getBestCmap()
    glyphs = []
    for u, g in sorted(cmap.items()):
        if u < 33 or 0x7F <= u < 0xA1 or u == 0xAD:
            continue
        bp = count_pts(base_glyf, base_cmap[u]) if base_glyf is not None and u in base_cmap else None
        glyphs.append([u, g, count_pts(glyf, g), bp, font['hmtx'][g][0]])
    drawn_cfg = cfg.get('drawn', {})
    word = drawn_cfg.get('word') or name.split()[0]
    order = list(axes)
    if 'wght' in order:
        order.remove('wght'); order.insert(0, 'wght')
    draw_axes = drawn_cfg.get('axes') or order[:2]
    drawn = outline_grid(font_path, word, draw_axes, axes)
    if base_glyf is not None:
        drawn['basePts'] = sum(count_pts(base_glyf, base_cmap[ord(c)]) for c in drawn['word'] if ord(c) in base_cmap)
    edges = edge_boxes(font, axes, cfg) if cfg.get('overprint', {}).get('style') == 'edges' else None
    data = dict(
        family=name, slug=slug, version=cfg.get('version') or (nm(font, 5) or '').replace('Version ', '').split(';')[0],
        upm=font['head'].unitsPerEm,
        metrics=dict(ascender=hh.ascent, descender=hh.descent, cap=getattr(os2, 'sCapHeight', 0) or 700,
                     xheight=getattr(os2, 'sxHeight', 0) or 500),
        axes=[axes[t] for t in order], glyphs=glyphs, features=feature_list(font, cfg), drawn=drawn, config=cfg)
    if edges:
        data['edges'] = edges
    out = os.path.join(ROOT, cfg.get('outDir') or slug)   # outDir: build somewhere else (explorations)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(TEMPLATE):
        shutil.copy(os.path.join(TEMPLATE, f), os.path.join(out, f))
    web = TTFont(font_path); web.flavor = 'woff2'; web.save(os.path.join(out, 'font.woff2'))
    if cfg.get('italic'):
        it = TTFont(os.path.normpath(os.path.join(cfg_dir, cfg['italic']))); it.flavor = 'woff2'; it.save(os.path.join(out, 'font-italic.woff2'))
        data['italic'] = True
    # download: one zip per font with the font files, the licence and the readme (the OFL asks that the licence travel with the fonts)
    if cfg.get('catalogue', True):
        import zipfile
        fdir = os.path.dirname(font_path); pkg = os.path.dirname(fdir)
        files = [font_path, font_path.replace('.ttf', '.woff2')]
        if cfg.get('italic'):
            ip = os.path.normpath(os.path.join(cfg_dir, cfg['italic'])); files += [ip, ip.replace('.ttf', '.woff2')]
        files += [os.path.join(pkg, n) for n in ('OFL.txt', 'README.md')]
        zname = data['family'].replace(' ', '') + '.zip'; folder = data['family'].replace(' ', '')
        with zipfile.ZipFile(os.path.join(out, zname), 'w', zipfile.ZIP_DEFLATED) as z:
            for f in files:
                if os.path.exists(f):
                    z.write(f, f'{folder}/' + ('fonts/' if f.startswith(fdir) else '') + os.path.basename(f))
        data['download'] = dict(file=zname, size=os.path.getsize(os.path.join(out, zname)))
        json.dump(data, open(os.path.join(out, 'data.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
        open(os.path.join(out, 'data.js'), 'w').write('window.SPEC_DATA=' + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + ';\n')
    # partner fonts (other catalogue fonts shown alongside this one)
    for i, pf in enumerate(cfg.get('overprint', {}).get('partners', [])):
        pt = TTFont(os.path.normpath(os.path.join(cfg_dir, pf['font']))); pt.flavor = 'woff2'
        pt.save(os.path.join(out, f'partner-{i}.woff2'))
    json.dump(data, open(os.path.join(out, 'data.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    # same data as a script, so the page also works opened straight from the folder (file://), where fetch is blocked
    open(os.path.join(out, 'data.js'), 'w').write('window.SPEC_DATA=' + json.dumps(data, separators=(',', ':'), ensure_ascii=False) + ';\n')
    # fill the static parts of the page so it reads correctly before scripts run
    html = open(os.path.join(out, 'index.html')).read()
    if cfg.get('back'):   # explorations live deeper; point the back button at their own index
        html = re.sub(r'(<a class="[^"]*\bback\b[^"]*"[^>]*?)href="[^"]*">[^<]*</a>', lambda m: f'{m.group(1)}href="{cfg["back"]["href"]}">← {cfg["back"]["label"]}</a>', html, count=1)
    html = html.replace('{{NAME}}', name).replace('{{TAGLINE}}', cfg.get('tagline', 'A variable typeface'))
    # shared assets (page font, photo) and the shared site footer; nav lists every font already in the catalogue
    base = os.path.relpath(ROOT, out).replace(os.sep, '/') + '/'
    html = html.replace('{{ASSETS}}', base + 'assets')
    cat = json.load(open(os.path.join(ROOT, 'catalog.json'))) if os.path.exists(os.path.join(ROOT, 'catalog.json')) else []
    tmk = lambda b: dict(tm=b['trademark']) if (b or {}).get('trademark') else {}
    nav = [dict(slug=c['slug'], name=c['name'], **tmk(c.get('base'))) for c in cat if c['slug'] != slug] + [dict(slug=slug, name=name, **tmk(cfg.get('base')))]
    nav.sort(key=lambda c: c['name'].lower())
    html = html.replace('<!--FOOTER-->', footer_html(nav, base))
    open(os.path.join(out, 'index.html'), 'w').write(html)
    if cfg.get('catalogue', True):
        update_catalogue(data)
    print(f'Built {name}: {os.path.relpath(out, ROOT)}/  ({len(glyphs)} characters, {len(axes)} axes, '
          f'{len(data["features"])} features, {sum(len(g["m"][next(iter(g["m"]))]) // 2 for g in drawn["glyphs"])} points in "{drawn["word"]}")')

def update_catalogue(data):
    cat_path = os.path.join(ROOT, 'catalog.json')
    cat = json.load(open(cat_path)) if os.path.exists(cat_path) else []
    cat = [c for c in cat if c['slug'] != data['slug']]
    cat.append(dict(slug=data['slug'], name=data['family'], tagline=data['config'].get('tagline', ''),
                    version=data['version'], axes=[dict(tag=a['tag'], name=a['name'], min=a['min'], max=a['max'],
                    default=a['default']) for a in data['axes']], glyphs=len(data['glyphs']),
                    display=data['config'].get('display'), italic=bool(data.get('italic')),
                    base={k: v for k, v in (data['config'].get('base') or {}).items() if k != 'path'},
                    remix=data['config'].get('remix')))
    cat.sort(key=lambda c: c['name'].lower())
    json.dump(cat, open(cat_path, 'w'), indent=1, ensure_ascii=False)
    tpl = open(os.path.join(TEMPLATE, '..', 'tools', 'catalogue.html')).read()
    site_path = os.path.join(ROOT, 'site.json')   # home page wording, credits and footer
    site = json.load(open(site_path)) if os.path.exists(site_path) else {}
    home = tpl.replace('/*CATALOG*/[]', json.dumps(cat, ensure_ascii=False)).replace('/*SITE*/{}', json.dumps(site, ensure_ascii=False))
    home = home.replace('<!--FOOTER-->', open(os.path.join(TEMPLATE, '..', 'tools', 'footer.html')).read())
    open(os.path.join(ROOT, 'index.html'), 'w').write(home)

def footer_html(nav, base):
    """The shared footer (tools/footer.html) plus the data it reads: site.json, the font list, the path back to the root."""
    site_path = os.path.join(ROOT, 'site.json')
    site = json.load(open(site_path)) if os.path.exists(site_path) else {}
    jf = json.dumps(dict(site=site, cat=nav, base=base, paper='sections'), ensure_ascii=False).replace('</', '<\\/')
    return f'<script>window.JF={jf};</script>\n' + open(os.path.join(TEMPLATE, '..', 'tools', 'footer.html')).read()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        build(p)
