"""Worked Sans — build script (v8: Work Sans Rough, made variable).

Takes Work Sans (variable, roman or italic), cuts a static instance at every weight master,
and rebuilds each one twice: at WORK 0 (untouched geometry, extra points sitting exactly on
the original outline) and at WORK 100 (corners filleted by an uneven radius, long straight
lines bowed in or out by a hair). Same points in every master, so it interpolates.

    python3 worked.py roman|italic
"""
import hashlib, math, os, sys, copy
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables import ttProgram
from fontTools.varLib import instancer
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor
from fontTools import varLib
from fontTools.otlLib.builder import buildStatTable

# ---------------------------------------------------------------- the look (all knobs here)
P = dict(
    # modelled on Work Sans Rough (measured from WorkSansRough-Medium/Bold): absolute units, same at every weight
    corner_angle=22,       # degrees of turn that counts as a corner
    radius=30,             # corner rounding: on-curve points this far either side of the corner (units)
    radius_spread=(0.85, 1.15),
    max_share=0.48,        # never use more than this share of an adjacent segment
    facet=47,              # straight edges are cut into facets about this long
    facet_slide=0.12,      # facet points slide along the edge by up to this share of a facet
    edge_sd=2.0,           # facet points pushed off the edge: gaussian spread (units)
    edge_clip=4.6,         # ...never more than this
    curve_sd=2.0,          # curve points nudged in x and y by this spread (units)
    curve_clip=5.0,
    corner_sd=1.5,         # the rounded corner's handle is nudged too
    light_stem=80,         # below this stem width, the two sides of a stroke move more together
    light_min=0.3,         #   (independent share at the thinnest weight; the rest follows a shared fine field)
    fine_field=45,         # size of that shared field (units)
)
SRC = {'roman': 'src/WorkSans[wght].ttf', 'italic': 'src/WorkSans-Italic[wght].ttf'}
FAMILY = 'Worked Sans'

def inv_avar(seg, n):
    pts = sorted(seg.items())
    for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
        if b0 <= n <= b1:
            return a0 + (n - b0) / (b1 - b0) * (a1 - a0) if b1 != b0 else a0
    return n

def master_weights(f):
    """User-space weights at every gvar peak (so each master is reproduced exactly)."""
    peaks = {0.0, -1.0, 1.0}
    for vs in f['gvar'].variations.values():
        for v in vs:
            peaks.add(round(v.axes['wght'][1], 4))
    seg = f['avar'].segments['wght']; a = f['fvar'].axes[0]
    out = []
    for n in sorted(peaks):
        u = inv_avar(seg, n)
        w = a.defaultValue + u * ((a.defaultValue - a.minValue) if u < 0 else (a.maxValue - a.defaultValue))
        d = a.defaultValue + n * ((a.defaultValue - a.minValue) if n < 0 else (a.maxValue - a.defaultValue))  # design coordinate
        out.append((round(w, 3), round(d, 3), n))
    return out

def stem(font):
    """Vertical stem thickness of H at 80% cap height."""
    glyf = font['glyf']; cm = font.getBestCmap(); g = glyf[cm[ord('H')]]
    c, ends, _ = g.getCoordinates(glyf); y = font['OS/2'].sCapHeight * .8; xs = []; st = 0
    for e in ends:
        pts = list(c[st:e + 1]); st = e + 1
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            if (y0 - y) * (y1 - y) < 0:
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return xs[1] - xs[0]

def rnd(seed):
    h = hashlib.md5(seed.encode()).digest()
    return int.from_bytes(h[:8], 'big') / 2 ** 64

def field(gname, x, y, ch):
    """Smooth 2-D noise in -1..1. Nearby points (like the two sides of one stroke) get nearly the same value."""
    G = P['field']; fx, fy = x / G, y / G; ix, iy = math.floor(fx), math.floor(fy); tx, ty = fx - ix, fy - iy
    sm = lambda t: t * t * (3 - 2 * t)
    v = lambda i, j: rnd(f'{gname}/f{ch}/{i}/{j}') * 2 - 1
    a = v(ix, iy) + (v(ix + 1, iy) - v(ix, iy)) * sm(tx)
    b = v(ix, iy + 1) + (v(ix + 1, iy + 1) - v(ix, iy + 1)) * sm(tx)
    return a + (b - a) * sm(ty)

def hand(gname, x, y, k=0):
    """The shared hand-movement vector at (x, y)."""
    return field(gname, x, y, 2 * k), field(gname, x, y, 2 * k + 1)

def gauss(seed, clip):
    u1 = max(rnd(seed + 'a'), 1e-12); u2 = rnd(seed + 'b')
    return max(-clip, min(clip, math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)))

def fine(gname, x, y, ch):
    G = P['fine_field']; fx, fy = x / G, y / G; ix, iy = math.floor(fx), math.floor(fy); tx, ty = fx - ix, fy - iy
    sm = lambda t: t * t * (3 - 2 * t)
    v = lambda i, j: gauss(f'{gname}/F{ch}/{i}/{j}', 2.5)
    a = v(ix, iy) + (v(ix + 1, iy) - v(ix, iy)) * sm(tx)
    b = v(ix, iy + 1) + (v(ix + 1, iy + 1) - v(ix, iy + 1)) * sm(tx)
    return a + (b - a) * sm(ty)

def unit(dx, dy):
    L = math.hypot(dx, dy)
    return (dx / L, dy / L) if L > 1e-9 else (0.0, 0.0)

def rework(gname, masters, stems, amount):
    """Work Sans Rough, made variable. masters: {key: (coords, ends, flags)}; amount 0..1."""
    keys = [k for k in masters]; ref = masters[keys[len(keys) // 2]]
    coords0, ends, flags0 = ref
    out = {k: ([], [], []) for k in keys}
    start = 0
    for ci, end in enumerate(ends):
        idx = list(range(start, end + 1)); n = len(idx); start = end + 1
        on = [flags0[i] & 1 for i in idx]
        # --- decisions on the reference master (identical structure in every master)
        corner = {}
        for j in range(n):
            if not on[j]:
                continue
            p = coords0[idx[j]]; a = coords0[idx[j - 1]]; b = coords0[idx[(j + 1) % n]]
            u1 = unit(p[0] - a[0], p[1] - a[1]); u2 = unit(b[0] - p[0], b[1] - p[1])
            if u1 == (0, 0) or u2 == (0, 0):
                continue
            turn = math.degrees(math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1]))))
            if turn >= P['corner_angle']:
                lo, hi = P['radius_spread']
                corner[j] = (lo + (hi - lo) * rnd(f'{gname}/{ci}/{j}/r'),
                             (gauss(f'{gname}/{ci}/{j}/cx', 2) * P['corner_sd'], gauss(f'{gname}/{ci}/{j}/cy', 2) * P['corner_sd']),
                             (fine(gname, *p, 0), fine(gname, *p, 1)))
        facets = {}
        for j in range(n):
            k = (j + 1) % n
            if on[j] and on[k]:
                L = math.dist(coords0[idx[j]], coords0[idx[k]])
                m = max(1, round(L / P['facet']))
                pts_ = []
                for i in range(1, m):
                    f = (i + (rnd(f'{gname}/{ci}/{j}/s{i}') * 2 - 1) * P['facet_slide']) / m
                    q = (coords0[idx[j]][0] + (coords0[idx[k]][0] - coords0[idx[j]][0]) * f,
                         coords0[idx[j]][1] + (coords0[idx[k]][1] - coords0[idx[j]][1]) * f)
                    pts_.append((f, gauss(f'{gname}/{ci}/{j}/o{i}', P['edge_clip'] / P['edge_sd']) * P['edge_sd'],
                                 (fine(gname, *q, 0), fine(gname, *q, 1))))
                facets[j] = pts_
        jit = {}
        for j in range(n):
            if j in corner:
                continue
            p = coords0[idx[j]]
            jit[j] = ((gauss(f'{gname}/{ci}/{j}/jx', P['curve_clip'] / P['curve_sd']) * P['curve_sd'],
                       gauss(f'{gname}/{ci}/{j}/jy', P['curve_clip'] / P['curve_sd']) * P['curve_sd']),
                      (fine(gname, *p, 0) * P['curve_sd'], fine(gname, *p, 1) * P['curve_sd']))
        # --- per master
        for key in keys:
            coords, _, flags = masters[key]; st = stems[key]
            ind = max(P['light_min'], min(1.0, st / P['light_stem']))     # how independently the two sides move
            mix = lambda indep, shared: (indep[0] * ind + shared[0] * (1 - ind), indep[1] * ind + shared[1] * (1 - ind))
            pts = [coords[i] for i in idx]
            fil = {}
            for j, (share, cjit, cshared) in corner.items():
                p = pts[j]; a = pts[j - 1]; b = pts[(j + 1) % n]
                r = min(P['radius'] * share, P['max_share'] * math.dist(p, a), P['max_share'] * math.dist(p, b)) * amount
                u1 = unit(a[0] - p[0], a[1] - p[1]); u2 = unit(b[0] - p[0], b[1] - p[1])
                dj = mix(cjit, (cshared[0] * P['corner_sd'], cshared[1] * P['corner_sd']))
                C = (p[0] + dj[0] * amount, p[1] + dj[1] * amount)
                fil[j] = ((p[0] + u1[0] * r, p[1] + u1[1] * r), C, (p[0] + u2[0] * r, p[1] + u2[1] * r))
            head = lambda j: fil[j][2] if j in fil else pts[j]
            tail = lambda j: fil[j][0] if j in fil else pts[j]
            new = []
            for j in range(n):
                if j in fil:
                    A, C, B = fil[j]; new += [(A[0], A[1], 1), (C[0], C[1], 0), (B[0], B[1], 1)]
                else:
                    (ix, iy), (sx, sy) = jit[j]; d = mix((ix, iy), (sx, sy))
                    new.append((pts[j][0] + d[0] * amount, pts[j][1] + d[1] * amount, on[j]))
                if j in facets:
                    k = (j + 1) % n; s0, s1 = head(j), tail(k)
                    nx, ny = unit(-(s1[1] - s0[1]), s1[0] - s0[0])
                    for f, o_ind, (fx, fy) in facets[j]:
                        o_sh = (fx * nx + fy * ny) * P['edge_sd']          # shared field, projected on the edge normal
                        o = (o_ind * ind + o_sh * (1 - ind)) * amount
                        new.append((s0[0] + (s1[0] - s0[0]) * f + nx * o, s0[1] + (s1[1] - s0[1]) * f + ny * o, 1))
            oc, oe, of = out[key]
            oc += [(x, y) for x, y, _ in new]; of += [o for _, _, o in new]; oe.append(len(oc) - 1)
    return out

def build(style):
    src = TTFont(SRC[style])
    src['GSUB'].table.FeatureVariations = None   # re-added as designspace rules below
    tmp = f'src/.nofv-{style}.ttf'; src.save(tmp)
    orig = TTFont(SRC[style])
    mw = master_weights(orig)
    print(style, 'masters (user, design, norm):', mw)
    insts = {}
    for w, d, n in mw:
        insts[w] = instancer.instantiateVariableFont(TTFont(tmp), {'wght': w})
    keys = [(w, t) for w, _, _ in mw for t in (0, 1)]
    stems = {(w, t): stem(insts[w]) for w, t in keys}
    ref_w = min(mw, key=lambda m: abs(m[2]))[0]
    stems['__ref'] = stems[(ref_w, 0)]
    print('stems', {k[0]: round(v) for k, v in stems.items() if k != '__ref' and k[1] == 0})
    outs = {k: instancer.instantiateVariableFont(TTFont(tmp), {'wght': k[0]}) for k in keys}
    order = insts[ref_w].getGlyphOrder()
    for gname in order:
        g0 = insts[ref_w]['glyf'][gname]
        if g0.isComposite() or g0.numberOfContours <= 0:
            continue
        base = {}
        for w, _, _ in mw:
            gl = insts[w]['glyf']; c, e, fl = gl[gname].getCoordinates(gl)
            base[w] = (list(c), list(e), list(fl))
        overlap = base[ref_w][2][0] & 0x40
        for t in (0, 1):
            res = rework(gname, {w: base[w] for w, _, _ in mw}, {w: stems[(w, 0)] for w, _, _ in mw} | {'__ref': stems['__ref']}, t)
            for w, _, _ in mw:
                c, e, fl = res[w]
                ng = Glyph(); ng.numberOfContours = len(e)
                ng.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in c]); ng.endPtsOfContours = e
                ng.flags = bytearray(fl); ng.flags[0] |= overlap
                ng.program = ttProgram.Program(); ng.program.fromBytecode(b'')
                glyf = outs[(w, t)]['glyf']; glyf[gname] = ng; ng.recalcBounds(glyf)
    os.makedirs('masters', exist_ok=True)
    for (w, t), f in outs.items():
        for tag in ('fpgm', 'prep', 'cvt ', 'gasp', 'hdmx', 'LTSH', 'VDMX'):
            if tag in f:
                del f[tag]
        for gname in f.getGlyphOrder():   # empty composite programs too
            g = f['glyf'][gname]
            if g.isComposite() and hasattr(g, 'program'):
                g.program = ttProgram.Program(); g.program.fromBytecode(b'')
        for gname in f.getGlyphOrder():
            g = f['glyf'][gname]; g.recalcBounds(f['glyf'])
            adv, _ = f['hmtx'][gname]; f['hmtx'][gname] = (adv, getattr(g, 'xMin', 0) if g.numberOfContours else 0)
        f.save(f'masters/{style}-w{w}-k{t * 100}.ttf')
    # designspace
    seg = orig['avar'].segments['wght']; a = orig['fvar'].axes[0]
    tod = lambda n: a.defaultValue + n * ((a.defaultValue - a.minValue) if n < 0 else (a.maxValue - a.defaultValue))
    tou = lambda u: a.defaultValue + u * ((a.defaultValue - a.minValue) if u < 0 else (a.maxValue - a.defaultValue))
    ds = DesignSpaceDocument()
    ax = AxisDescriptor(); ax.tag = 'wght'; ax.name = 'Weight'; ax.minimum, ax.default, ax.maximum = a.minValue, a.defaultValue, a.maxValue
    ax.map = [(round(tou(u), 3), round(tod(n), 3)) for u, n in sorted(seg.items())]; ds.addAxis(ax)
    ak = AxisDescriptor(); ak.tag = 'WORK'; ak.name = 'Worked'; ak.minimum, ak.default, ak.maximum = 0, 100, 100; ds.addAxis(ak)
    for w, d, n in mw:
        for t in (0, 1):
            s = SourceDescriptor(); s.path = os.path.abspath(f'masters/{style}-w{w}-k{t * 100}.ttf'); s.name = f'w{w}k{t}'
            s.location = {'Weight': d, 'Worked': t * 100}; ds.addSource(s)
    fv = orig['GSUB'].table.FeatureVariations; gs = orig['GSUB'].table
    for i, rec in enumerate(fv.FeatureVariationRecord if fv else []):
        subs = {}
        for sr in rec.FeatureTableSubstitution.SubstitutionRecord:
            for li in sr.Feature.LookupListIndex:
                for st in gs.LookupList.Lookup[li].SubTable:
                    subs.update(getattr(st, 'mapping', {}))
        c = rec.ConditionSet.ConditionTable[0]
        r = RuleDescriptor(); r.name = f'bracket{i}'
        r.conditionSets.append([dict(name='Weight', minimum=tod(c.FilterRangeMinValue), maximum=tod(c.FilterRangeMaxValue))])
        r.subs = sorted(subs.items()); ds.addRule(r)
    ds.rulesProcessingLast = False
    names = {100: 'Thin', 200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold', 900: 'Black'}
    ital = style == 'italic'
    for w, nme in names.items():
        i = InstanceDescriptor(); i.familyName = FAMILY
        i.styleName = (nme + ' Italic').replace('Regular Italic', 'Italic') if ital else nme
        i.location = {'Weight': tod(next(n for u, n in sorted(seg.items()) if abs(tou(u) - w) < .5)), 'Worked': 100}; ds.addInstance(i)
    dsp = f'WorkedSans-{style}.designspace'; ds.write(dsp)
    vf, _, _ = varLib.build(ds, exclude=['STAT'])
    nm = vf['name']; ps = 'WorkedSans' + ('-Italic' if ital else '')
    for rec in list(nm.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            nm.removeNames(nameID=rec.nameID)
    nm.setName(FAMILY, 1, 3, 1, 0x409); nm.setName('Italic' if ital else 'Regular', 2, 3, 1, 0x409)
    nm.setName(f'{ps};1.000', 3, 3, 1, 0x409); nm.setName(FAMILY + (' Italic' if ital else ''), 4, 3, 1, 0x409)
    nm.setName('Version 1.000; derived from Work Sans 2.012', 5, 3, 1, 0x409)
    nm.setName(ps if ital else 'WorkedSans-Regular', 6, 3, 1, 0x409); nm.setName('WorkedSans', 25, 3, 1, 0x409)
    nm.setName('Copyright 2019 The Work Sans Project Authors. Worked Sans modifications by JC Morales.', 0, 3, 1, 0x409)
    nm.setName('JC Morales (worked treatment); Work Sans by Wei Huang', 9, 3, 1, 0x409)
    nm.setName('This Font Software is licensed under the SIL Open Font License, Version 1.1.', 13, 3, 1, 0x409)
    nm.setName('https://openfontlicense.org', 14, 3, 1, 0x409)
    for axd in vf['fvar'].axes:
        axd.axisNameID = nm.addMultilingualName({'en': 'Weight' if axd.axisTag == 'wght' else 'Worked'}, mac=False)
    for inst, (w, nme) in zip(vf['fvar'].instances, names.items()):
        sn = (nme + ' Italic').replace('Regular Italic', 'Italic') if ital else nme
        inst.subfamilyNameID = nm.addMultilingualName({'en': sn}, mac=False)
        inst.postscriptNameID = nm.addMultilingualName({'en': f'WorkedSans-{sn.replace(" ", "")}'}, mac=False)
    vf['OS/2'].fsSelection = (vf['OS/2'].fsSelection & ~0b1100001) | (0b1 if ital else 0b1000000)
    vf['head'].macStyle = 0b10 if ital else 0
    buildStatTable(vf, [
        dict(tag='wght', name='Weight', values=[dict(value=w, name=n, **({'flags': 2, 'linkedValue': 700} if w == 400 else {})) for w, n in names.items()]),
        dict(tag='WORK', name='Worked', values=[dict(value=0, name='Fresh'), dict(value=100, name='Worked', flags=2)]),
        dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic')] if ital else [dict(value=0, name='Roman', flags=2, linkedValue=1)]),
    ], elidedFallbackName=2)
    os.makedirs('fonts', exist_ok=True)
    out = f'fonts/WorkedSans{"-Italic" if ital else ""}[WORK,wght].ttf'
    vf.save(out); vf.flavor = 'woff2'; vf.save(out.replace('.ttf', '.woff2'))
    os.remove(tmp)
    print('saved', out, os.path.getsize(out) // 1024, 'KB')

if __name__ == '__main__':
    for s in (sys.argv[1:] or ['roman', 'italic']):
        build(s)
