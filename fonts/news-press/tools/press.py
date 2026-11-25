"""News Press (formerly Newsreader Letterpress), variable: build script.

Copies the method of the static Newsreader Letterpress cuts (Display, H1, H2), measured from
those files, and puts it on a Press axis:

  * every outline is resampled into short straight facets (all on-curve points)
  * each facet point is pushed in or out along the edge normal by smoothed gaussian noise
  * small knockout specks sit inside the ink

The three static cuts become three stops on the axis (units at 2000 UPM, as measured):

    Press   0  = Display cut   facets ~11, wobble sd ~8,  many small specks   (~60 per 1e6 units², ~12 across)
    Press  50  = H1 cut        facets ~16, wobble sd ~12, half as many, ~22 across
    Press 100  = H2 cut        facets ~20, wobble sd ~14, a quarter as many, ~34 across

Every master has the same points: one resampling for all of them, and every speck exists in every
master (collapsed to a point where it isn't used), so weight and press interpolate. Optical size is fixed
at 16, where the static cuts were made (dropped to keep the web font around 2 MB).

    python3 press.py roman|italic
"""
import hashlib, math, os, sys
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables import ttProgram
from fontTools.pens.recordingPen import RecordingPen
from fontTools.varLib import instancer
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor, RuleDescriptor
from fontTools import varLib
from fontTools.otlLib.builder import buildStatTable

# ---------------------------------------------------------------- the look (all knobs here)
SPACING = 10.0                       # resample step (units); finer than the finest facet
STOPS = {                            # Press value -> measured look of each static cut
    0:   dict(knot=11.0, sd=8.0,  dens=60e-6, size=12.0),
    50:  dict(knot=16.0, sd=12.0, dens=30e-6, size=22.0),
    100: dict(knot=24.0, sd=12.5, dens=14e-6, size=34.0, smooth=(0.6, 1.0, 0.6)),   # v2: softer than the H2 cut (longer, rounder waves)
}
PRESS_DEFAULT = 50
SMOOTH = (0.3, 1.0, 0.3)             # knot smoothing -> neighbour correlation ~0.6, as measured
CLIP = 2.4                           # gaussian clip, in sd
THIN = 7.0                           # strokes thinner than THIN*sd move more as one (both sides together)
THIN_MIN = 0.25
MAX_SHARE = 0.32                     # an edge never moves more than this share of the local stroke
HOLE_PTS = (5, 9)                    # speck polygons: 5-8 sides (the static cuts use 3-7; no sharp triangles here)
HOLE_JIT = 0.28
HOLE_ASPECT = (0.42, 0.35)           # elongation: lognormal (mu, sigma) -> median ~1.5, p90 ~2.4, as measured
DEBUG = False
OPSZ = 16.0                          # optical size is fixed here: the static cuts were all made at 16
FAMILY = 'News Press'
PS = 'NewsPress'
SRC = {'roman': 'src/Newsreader[opsz,wght].ttf', 'italic': 'src/Newsreader-Italic[opsz,wght].ttf'}

# ---------------------------------------------------------------- geometry
def contours_from(rec):
    out, segs, start, cur = [], [], None, None
    for op, args in rec:
        if op == 'moveTo':
            start = cur = args[0]; segs = []
        elif op == 'lineTo':
            segs.append((cur, args[0])); cur = args[0]
        elif op == 'qCurveTo':
            pts = list(args)
            if pts[-1] is None:
                offs = pts[:-1]
                start = cur = ((offs[-1][0] + offs[0][0]) / 2, (offs[-1][1] + offs[0][1]) / 2)
                segs = []; pts = offs + [start]
            offs, end = pts[:-1], pts[-1]
            for k, c in enumerate(offs):
                nxt = end if k == len(offs) - 1 else ((c[0] + offs[k + 1][0]) / 2, (c[1] + offs[k + 1][1]) / 2)
                segs.append((cur, c, nxt)); cur = nxt
        elif op in ('closePath', 'endPath'):
            segs.append((cur, start)); out.append(segs); segs = []
    return out

def seg_pt(seg, t):
    if len(seg) == 2:
        (x0, y0), (x1, y1) = seg
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    (x0, y0), (cx, cy), (x1, y1) = seg
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return (a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1)

def seg_len(seg):
    p = [seg_pt(seg, k / 16) for k in range(17)]
    return sum(math.dist(p[k], p[k + 1]) for k in range(16))

def winding(q, polys):
    x, y = q; wn = 0
    for a in polys:
        b = np.roll(a, -1, 0)
        up = (a[:, 1] <= y) & (b[:, 1] > y); dn = (a[:, 1] > y) & (b[:, 1] <= y)
        cr = (b[:, 0] - a[:, 0]) * (y - a[:, 1]) - (x - a[:, 0]) * (b[:, 1] - a[:, 1])
        wn += int(np.sum(up & (cr > 0))) - int(np.sum(dn & (cr < 0)))
    return wn

def ray(p, d, polys):
    best = math.inf
    for a in polys:
        e = np.roll(a, -1, 0) - a
        den = d[0] * e[:, 1] - d[1] * e[:, 0]; ok = np.abs(den) > 1e-9; ap = a - p
        dd = np.where(ok, den, 1)
        t = np.where(ok, (ap[:, 0] * e[:, 1] - ap[:, 1] * e[:, 0]) / dd, np.inf)
        u = np.where(ok, (ap[:, 0] * d[1] - ap[:, 1] * d[0]) / dd, -1)
        hit = ok & (t > 1.0) & (u >= 0) & (u <= 1)
        if hit.any():
            best = min(best, float(t[hit].min()))
    return best

def edge_dist(q, polys):
    best = math.inf
    for a in polys:
        e = np.roll(a, -1, 0) - a; L2 = np.maximum((e ** 2).sum(1), 1e-9)
        t = np.clip(((q - a) * e).sum(1) / L2, 0, 1)
        best = min(best, float(np.sqrt(((a + e * t[:, None] - q) ** 2).sum(1)).min()))
    return best

def normals(poly):
    t = np.roll(poly, -1, 0) - np.roll(poly, 1, 0)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
    return np.stack([-t[:, 1], t[:, 0]], 1)

def vfield(rng_seed, pts, grid):
    """Smooth 2-D vector noise (unit-ish sd) at pts, grid-sized cells."""
    out = np.zeros_like(pts)
    for ch in range(2):
        f = pts / grid; i = np.floor(f).astype(np.int64); t = f - i; t = t * t * (3 - 2 * t)
        def v(ix, iy):
            h = (ix * 73856093) ^ (iy * 19349663) ^ (rng_seed * 83492791 + ch * 2654435761)
            h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
            return (h / 2 ** 32) * 3.4 - 1.7
        a = v(i[:, 0], i[:, 1]) + (v(i[:, 0] + 1, i[:, 1]) - v(i[:, 0], i[:, 1])) * t[:, 0]
        b = v(i[:, 0], i[:, 1] + 1) + (v(i[:, 0] + 1, i[:, 1] + 1) - v(i[:, 0], i[:, 1] + 1)) * t[:, 0]
        out[:, ch] = a + (b - a) * t[:, 1]
    return out

# ---------------------------------------------------------------- one glyph
def press_glyph(name, recs, ref):
    """recs: {master: recording}. Returns {(master, stop): [polygons]}."""
    M = list(recs)
    cs = {m: contours_from(recs[m]) for m in M}
    nC = len(cs[ref])
    for m in M:
        assert len(cs[m]) == nC and all(len(a) == len(b) for a, b in zip(cs[m], cs[ref])), name
    seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    # resample identically in every master
    samp = {m: [] for m in M}
    for ci in range(nC):
        pts = {m: [] for m in M}
        for si in range(len(cs[ref][ci])):
            L = max(seg_len(cs[m][ci][si]) for m in M)
            if L < 0.5:
                continue
            n = max(1, math.ceil(L / SPACING))
            for k in range(n):
                for m in M:
                    pts[m].append(seg_pt(cs[m][ci][si], k / n))
        for m in M:
            samp[m].append(np.array(pts[m], float))
    keep = [i for i in range(nC) if len(samp[ref][i]) >= 3]
    for m in M:
        samp[m] = [samp[m][i] for i in keep]
    nC = len(keep)
    if nC == 0:
        return {(m, k): [] for m in M for k in STOPS}
    # outward normals, sign decided once on the reference master
    R = samp[ref]; sign = []; inks = []
    for poly in R:
        nl = normals(poly); votes = 0; iv = []
        for i in np.linspace(0, len(poly) - 1, 7).astype(int):
            outl = winding(poly[i] + nl[i] * 1.5, R) == 0
            votes += 1 if outl else -1
            iv.append(winding(poly[i] - (nl[i] if outl else -nl[i]) * 1.5, R))
        sign.append(1.0 if votes >= 0 else -1.0)
        nz = [v for v in iv if v]; inks.append(int(np.sign(np.median(nz))) if nz else 1)
    s_ink = int(np.sign(np.median(inks))) or 1
    N = {m: [normals(samp[m][ci]) * sign[ci] for ci in range(nC)] for m in M}
    # local stroke thickness (every 3rd point, interpolated)
    thick = {}
    for m in M:
        thick[m] = []
        for ci in range(nC):
            poly = samp[m][ci]; nrm = N[m][ci]; n = len(poly)
            idx = np.arange(0, n, 3); tv = []
            for i in idx:
                t = ray(poly[i], -nrm[i], samp[m]); tv.append(t if np.isfinite(t) else 400.0)
            thick[m].append(np.interp(np.arange(n), np.r_[idx, n], np.r_[tv, tv[0]]))
    # arc length on the reference master
    arcs = []
    for poly in R:
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
        arcs.append((d, max(d[-1] + np.linalg.norm(poly[0] - poly[-1]), 1.0)))
    # edge displacement per stop: knots along the arc, smoothed, linear between knots (facets)
    disp = {}
    for k, S in STOPS.items():
        fseed = int(rng.integers(1 << 30))
        for ci in range(nC):
            s, L = arcs[ci]
            nk = max(3, round(L / S['knot']))
            kpos = (np.arange(nk) + rng.uniform(-0.18, 0.18, nk)) * L / nk
            kpos[0] = 0.0
            g = np.clip(rng.standard_normal(nk), -CLIP, CLIP)
            sm = S.get('smooth', SMOOTH)
            g = sm[0] * np.roll(g, 1) + sm[1] * g + sm[2] * np.roll(g, -1)
            g /= math.sqrt(sum(w * w for w in sm))
            ind_d = np.interp(s, np.r_[kpos, L], np.r_[g, g[0]]) * S['sd']
            for m in M:
                poly = samp[m][ci]; nrm = N[m][ci]; t = thick[m][ci]
                sh = (vfield(fseed, poly, S['knot'] * 2.2) * nrm).sum(1) * S['sd']
                w_ind = np.clip(t / (THIN * S['sd']), THIN_MIN, 1.0)
                d = ind_d * w_ind + sh * (1 - w_ind)
                cap = MAX_SHARE * t
                disp[(m, k, ci)] = np.clip(d, -cap, cap)
    # specks: per stop, scattered over the ink of the reference master, anchored to the nearest edge
    holes = []
    xs = np.concatenate(R); x0, y0 = xs.min(0); x1, y1 = xs.max(0)
    def ink_area(polys):
        t = 0.0
        for a in polys:
            b = np.roll(a, -1, 0); t += 0.5 * (a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1]).sum()
        return abs(t)
    area = max(ink_area(samp[m]) for m in M if m[1] == ref[1])   # heaviest weight at this size: holes collapse where lighter strokes have no room
    for k, S in STOPS.items():
        r0 = S['size'] / 1.72
        want = rng.poisson(S['dens'] * area)
        got = []; tries = 0
        while len(got) < want and tries < want * 40 + 40:
            tries += 1
            c = np.array([rng.uniform(x0, x1), rng.uniform(y0, y1)])
            if winding(c, R) != s_ink:
                continue
            if edge_dist(c, R) < r0 * 0.6 + S['sd'] * 0.5:
                continue
            if any(np.linalg.norm(c - h['c']) < (r0 + h['r0']) * 1.3 for h in got):
                continue
            # anchor: nearest sample, distance along its inward ray as a share of the stroke there
            best = None
            for ci, poly in enumerate(R):
                dd = np.linalg.norm(poly - c, axis=1); i = int(dd.argmin())
                if best is None or dd[i] < best[0]:
                    best = (dd[i], ci, i)
            _, ci, i = best
            t = ray(R[ci][i], -N[ref][ci][i], R)
            if not np.isfinite(t) or t <= 0:
                continue
            frac = float(np.dot(R[ci][i] - c, N[ref][ci][i])) / t
            if not 0.15 < frac < 0.85:
                continue
            got.append(dict(c=c, r0=r0, ci=ci, i=i, frac=frac, k=k, sd=S['sd'],
                            n=int(rng.integers(*HOLE_PTS)), seed=int(rng.integers(1 << 30)),
                            asp=float(np.clip(rng.lognormal(*HOLE_ASPECT), 1.0, 3.2)), rot=float(rng.uniform(0, math.pi))))
        if DEBUG: print(name, k, 'want', want, 'got', len(got), 'tries', tries)
        holes += got
    # resolve each speck in each master (shrinks to fit, or collapses if it no longer fits)
    for h in holes:
        h['geo'] = {}
        for m in M:
            p = samp[m][h['ci']][h['i']]; nrm = N[m][h['ci']][h['i']]
            t = ray(p, -nrm, samp[m])
            c = p - nrm * (t if np.isfinite(t) else 0) * h['frac']; r = 0.0
            if np.isfinite(t) and winding(c, samp[m]) == s_ink:
                room = (edge_dist(c, samp[m]) - h['sd'] * 1.0) / ((1 + HOLE_JIT) * math.sqrt(h['asp']))
                r = max(0.0, min(h['r0'], room))
                if r < 2.5:
                    r = 0.0
            h['geo'][m] = (c, r)
    out = {}
    for m in M:
        for k in STOPS:
            polys = [samp[m][ci] + disp[(m, k, ci)][:, None] * N[m][ci] for ci in range(nC)]
            for h in holes:
                c, r = h['geo'][m]; r = r if h['k'] == k else 0.0
                hr = np.random.default_rng(h['seed']); n = h['n']
                ang = np.linspace(0, 2 * math.pi, n, endpoint=False) + hr.uniform(0, 2 * math.pi) + hr.uniform(-.25, .25, n) * 2 * math.pi / n
                rad = r * (1 + HOLE_JIT * hr.uniform(-1, 1, n))
                ex, ey = rad * np.cos(ang) * math.sqrt(h['asp']), rad * np.sin(ang) / math.sqrt(h['asp'])   # same area, stretched
                cr, sr = math.cos(h['rot']), math.sin(h['rot'])
                pts = np.stack([c[0] + ex * cr - ey * sr, c[1] + ex * sr + ey * cr], 1)
                polys.append(pts[::-1] if s_ink > 0 else pts)   # knockouts wind against the ink
            out[(m, k)] = polys
    return out

# ---------------------------------------------------------------- build
def build(style):
    orig = TTFont(SRC[style])
    a = {ax.axisTag: ax for ax in orig['fvar'].axes}
    W = (a['wght'].minValue, a['wght'].defaultValue, a['wght'].maxValue)
    O = (OPSZ,)
    src = TTFont(SRC[style]); fv = src['GSUB'].table.FeatureVariations
    src['GSUB'].table.FeatureVariations = None
    tmp = f'src/.nofv-{style}.ttf'; src.save(tmp)
    M = [(w, o) for w in W for o in O]; ref = (W[1], O[0])
    inst = {m: instancer.instantiateVariableFont(TTFont(tmp), {'wght': m[0], 'opsz': m[1]}) for m in M}
    order = inst[ref].getGlyphOrder()
    outs = {(m, k): instancer.instantiateVariableFont(TTFont(tmp), {'wght': m[0], 'opsz': m[1]}) for m in M for k in STOPS}
    done = 0
    for gname in order:
        g0 = inst[ref]['glyf'][gname]
        if g0.isComposite() or g0.numberOfContours <= 0:
            continue
        recs = {}
        for m in M:
            pen = RecordingPen(); inst[m].getGlyphSet()[gname].draw(pen); recs[m] = pen.value
        res = press_glyph(gname, recs, ref)
        for (m, k), polys in res.items():
            coords, ends = [], []
            for poly in polys:
                coords += [(int(round(float(x))), int(round(float(y)))) for x, y in poly]; ends.append(len(coords) - 1)
            gl = Glyph(); gl.numberOfContours = len(ends)
            if ends:
                gl.coordinates = GlyphCoordinates(coords); gl.endPtsOfContours = ends
                gl.flags = bytearray([1] * len(coords))
                gl.program = ttProgram.Program(); gl.program.fromBytecode(b'')
            glyf = outs[(m, k)]['glyf']; glyf[gname] = gl
            if ends:
                gl.recalcBounds(glyf)
        done += 1
        if done % 40 == 0:
            print(style, done, 'glyphs', flush=True)
    os.makedirs('masters', exist_ok=True)
    for (m, k), f in outs.items():
        for tag in ('fpgm', 'prep', 'cvt ', 'gasp', 'hdmx', 'LTSH', 'VDMX'):
            if tag in f:
                del f[tag]
        for gname in f.getGlyphOrder():
            g = f['glyf'][gname]
            if g.isComposite() and hasattr(g, 'program'):
                g.program = ttProgram.Program(); g.program.fromBytecode(b'')
            g.recalcBounds(f['glyf'])
            adv, _ = f['hmtx'][gname]; f['hmtx'][gname] = (adv, getattr(g, 'xMin', 0) if g.numberOfContours else 0)
        f.save(f'masters/{style}-w{int(m[0])}-p{k}.ttf')
    # designspace: design coords = normalized (after avar) stretched back over the user range
    seg = orig['avar'].segments
    def tod(tag, n):
        A = a[tag]; return A.defaultValue + n * ((A.defaultValue - A.minValue) if n < 0 else (A.maxValue - A.defaultValue))
    def tou(tag, u):
        return tod(tag, u)
    ds = DesignSpaceDocument()
    for tag, nm in (('wght', 'Weight'),):
        ax = AxisDescriptor(); ax.tag = tag; ax.name = nm
        ax.minimum, ax.default, ax.maximum = a[tag].minValue, a[tag].defaultValue, a[tag].maxValue
        ax.map = [(round(tou(tag, u), 3), round(tod(tag, n), 3)) for u, n in sorted(seg[tag].items())]; ds.addAxis(ax)
    ap = AxisDescriptor(); ap.tag = 'PRES'; ap.name = 'Press'; ap.minimum, ap.default, ap.maximum = min(STOPS), PRESS_DEFAULT, max(STOPS); ds.addAxis(ap)
    for m in M:
        for k in STOPS:
            s = SourceDescriptor(); s.path = os.path.abspath(f'masters/{style}-w{int(m[0])}-p{k}.ttf')
            s.name = f'w{m[0]}o{m[1]}p{k}'
            s.location = {'Weight': tod('wght', -1 if m[0] == W[0] else (1 if m[0] == W[2] else 0)), 'Press': k}
            ds.addSource(s)
    gs = orig['GSUB'].table; names_ax = {0: 'Weight', 1: 'Optical size'}; tags_ax = {0: 'wght', 1: 'opsz'}
    for i, rec in enumerate(fv.FeatureVariationRecord if fv else []):
        subs = {}
        for sr in rec.FeatureTableSubstitution.SubstitutionRecord:
            for li in sr.Feature.LookupListIndex:
                for st in gs.LookupList.Lookup[li].SubTable:
                    subs.update(getattr(st, 'mapping', {}))
        conds, live = [], True
        for c in rec.ConditionSet.ConditionTable:
            lo, hi = tod(tags_ax[c.AxisIndex], c.FilterRangeMinValue), tod(tags_ax[c.AxisIndex], c.FilterRangeMaxValue)
            if tags_ax[c.AxisIndex] == 'opsz':
                live = live and lo <= OPSZ <= hi          # optical size is pinned: keep the rule only if it applies there
            else:
                conds.append(dict(name=names_ax[c.AxisIndex], minimum=lo, maximum=hi))
        if not live or not conds:
            continue
        r = RuleDescriptor(); r.name = f'rule{i}'
        r.conditionSets.append(conds)
        r.subs = sorted(subs.items()); ds.addRule(r)
    ds.rulesProcessingLast = False
    ital = style == 'italic'
    wn = {200: 'ExtraLight', 300: 'Light', 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold', 800: 'ExtraBold'}
    def wloc(w):
        u = (w - a['wght'].defaultValue) / ((a['wght'].defaultValue - a['wght'].minValue) if w < a['wght'].defaultValue else (a['wght'].maxValue - a['wght'].defaultValue))
        pts = sorted(seg['wght'].items())
        for (u0, n0), (u1, n1) in zip(pts, pts[1:]):
            if u0 <= u <= u1:
                return tod('wght', n0 + (u - u0) / (u1 - u0) * (n1 - n0))
        return tod('wght', u)
    for w, nme in wn.items():
        i = InstanceDescriptor(); i.familyName = FAMILY
        i.styleName = (nme + ' Italic').replace('Regular Italic', 'Italic') if ital else nme
        i.location = {'Weight': wloc(w), 'Press': PRESS_DEFAULT}; ds.addInstance(i)
    dsp = f'{PS}-{style}.designspace'; ds.write(dsp)
    vf, _, _ = varLib.build(ds, exclude=['STAT'])
    nm = vf['name']; ps = PS + ('-Italic' if ital else '')
    for rec in list(nm.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25):
            nm.removeNames(nameID=rec.nameID)
    nm.setName(FAMILY, 1, 3, 1, 0x409); nm.setName('Italic' if ital else 'Regular', 2, 3, 1, 0x409)
    nm.setName(f'{ps};1.000', 3, 3, 1, 0x409); nm.setName(FAMILY + (' Italic' if ital else ''), 4, 3, 1, 0x409)
    nm.setName('Version 1.000; derived from Newsreader 1.003', 5, 3, 1, 0x409)
    nm.setName(ps if ital else PS + '-Regular', 6, 3, 1, 0x409); nm.setName(PS, 25, 3, 1, 0x409)
    nm.setName('Copyright 2020 The Newsreader Project Authors. Letterpress modifications by JC Morales.', 0, 3, 1, 0x409)
    nm.setName('JC Morales (letterpress treatment); Newsreader by Production Type', 9, 3, 1, 0x409)
    nm.setName('This Font Software is licensed under the SIL Open Font License, Version 1.1.', 13, 3, 1, 0x409)
    nm.setName('https://openfontlicense.org', 14, 3, 1, 0x409)
    axn = {'wght': 'Weight', 'PRES': 'Press'}
    for axd in vf['fvar'].axes:
        axd.axisNameID = nm.addMultilingualName({'en': axn[axd.axisTag]}, mac=False)
    for inst_, (w, nme) in zip(vf['fvar'].instances, wn.items()):
        sn = (nme + ' Italic').replace('Regular Italic', 'Italic') if ital else nme
        inst_.subfamilyNameID = nm.addMultilingualName({'en': sn}, mac=False)
        inst_.postscriptNameID = nm.addMultilingualName({'en': f'{PS}-{sn.replace(" ", "")}'}, mac=False)
    vf['OS/2'].fsSelection = (vf['OS/2'].fsSelection & ~0b1100001) | (0b1 if ital else 0b1000000)
    vf['head'].macStyle = 0b10 if ital else 0
    buildStatTable(vf, [
        dict(tag='wght', name='Weight', values=[dict(value=w, name=n, **({'flags': 2, 'linkedValue': 700} if w == 400 else {})) for w, n in wn.items()]),
        dict(tag='PRES', name='Press', values=[dict(value=0, name='Kiss'), dict(value=50, name='Press', flags=2), dict(value=100, name='Heavy')]),
        dict(tag='ital', name='Italic', values=[dict(value=1, name='Italic')] if ital else [dict(value=0, name='Roman', flags=2, linkedValue=1)]),
    ], elidedFallbackName=2)
    os.makedirs('fonts', exist_ok=True)
    out = f'fonts/{PS}{"-Italic" if ital else ""}[PRES,wght].ttf'
    vf.save(out); vf.flavor = 'woff2'; vf.save(out.replace('.ttf', '.woff2'))
    os.remove(tmp)
    print('saved', out, os.path.getsize(out) // 1024, 'KB', os.path.getsize(out.replace('.ttf', '.woff2')) // 1024, 'KB woff2')

if __name__ == '__main__':
    for s in (sys.argv[1:] or ['roman', 'italic']):
        build(s)
