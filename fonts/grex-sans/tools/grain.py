"""Grain engine — interpolation-compatible roughening for variable fonts.

Every master gets exactly the same point structure:
  * each outline segment is resampled at the same parameters in every master
  * edge displacement (wobble + bites in + bumps out) moves those points along the normal
  * knockout holes and outside specks are extra contours present in every master;
    at GRAN 0 they collapse to a single point (zero area) and the edge displacement is 0,
    so GRAN 0 is exactly the base design.

Usage: python3 grain.py   (reads src/master-w*.ttf, writes masters/*.ttf)
"""
import hashlib, math, os
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables import ttProgram

# ---------------------------------------------------------------- parameters
P = dict(
    spacing=7.0,          # resample step along outlines (font units)
    wobble=3.2,           # edge wobble amplitude at Regular (units)
    wobble_layers=((48, 1.0), (16, 0.55), (6, 0.35)),   # (wavelength, weight)
    event_gap=46.0,       # mean distance between edge bites/bumps
    bite_prob=0.6,        # share of events that bite in (rest poke out)
    bite_depth=0.16,      # max bite depth as a fraction of local stroke thickness
    bump_height=0.13,     # max bump height as a fraction of the master's stem
    event_width=(6.0, 18.0),
    hole_gap=34.0,        # spacing of knockout candidates along the outline
    hole_prob=0.55,
    hole_r=(0.07, 0.17),  # hole radius as a fraction of local thickness
    speck_gap=60.0,
    speck_prob=0.4,
    speck_r=(0.035, 0.09),  # speck radius as a fraction of stem
    speck_off=(0.4, 2.2),   # gap between edge and speck, in speck radii
)
WEIGHTS = (100, 400, 700)
HEAVY_DAMP = 0.75   # grain grows slower than the stroke above Regular (0 = no damping)
DEFAULT_W = 400

# ---------------------------------------------------------------- geometry helpers
def segments_from_recording(rec):
    """RecordingPen value -> list of contours, each a list of segments (tuples of points)."""
    contours, segs, start, cur = [], [], None, None
    for op, args in rec:
        if op == 'moveTo':
            start = cur = args[0]; segs = []
        elif op == 'lineTo':
            segs.append((cur, args[0])); cur = args[0]
        elif op == 'qCurveTo':
            pts = list(args)
            if pts[-1] is None:  # all-off-curve contour
                offs = pts[:-1]
                start = cur = ((offs[-1][0] + offs[0][0]) / 2, (offs[-1][1] + offs[0][1]) / 2)
                segs = []
                pts = offs + [start]
            offs, end = pts[:-1], pts[-1]
            for k, c in enumerate(offs):
                nxt = end if k == len(offs) - 1 else ((c[0] + offs[k + 1][0]) / 2, (c[1] + offs[k + 1][1]) / 2)
                segs.append((cur, c, nxt)); cur = nxt
        elif op == 'curveTo':
            raise ValueError('cubic outlines not supported')
        elif op in ('closePath', 'endPath'):
            segs.append((cur, start))  # always add (maybe zero-length) closing line
            contours.append(segs); segs = []
    return contours

def seg_point(seg, t):
    if len(seg) == 2:
        (x0, y0), (x1, y1) = seg
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
    (x0, y0), (cx, cy), (x1, y1) = seg
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return (a * x0 + b * cx + c * x1, a * y0 + b * cy + c * y1)

def seg_len(seg):
    pts = [seg_point(seg, k / 16) for k in range(17)]
    return sum(math.dist(pts[k], pts[k + 1]) for k in range(16))

def winding(q, polys):
    """Nonzero winding number of point q against list of closed polygons (N,2)."""
    x, y = q; wn = 0
    for poly in polys:
        a = poly; b = np.roll(poly, -1, axis=0)
        up = (a[:, 1] <= y) & (b[:, 1] > y)
        dn = (a[:, 1] > y) & (b[:, 1] <= y)
        cross = (b[:, 0] - a[:, 0]) * (y - a[:, 1]) - (x - a[:, 0]) * (b[:, 1] - a[:, 1])
        wn += int(np.sum(up & (cross > 0))) - int(np.sum(dn & (cross < 0)))
    return wn

def ray_dist(p, d, polys):
    """Distance from p along unit vector d to the nearest outline edge (skipping ~0)."""
    best = math.inf
    for poly in polys:
        a = poly; b = np.roll(poly, -1, axis=0); e = b - a
        den = d[0] * e[:, 1] - d[1] * e[:, 0]
        ok = np.abs(den) > 1e-9
        ap = a - p
        t = np.where(ok, (ap[:, 0] * e[:, 1] - ap[:, 1] * e[:, 0]) / np.where(ok, den, 1), np.inf)
        u = np.where(ok, (ap[:, 0] * d[1] - ap[:, 1] * d[0]) / np.where(ok, den, 1), -1)
        hit = ok & (t > 1.0) & (u >= 0) & (u <= 1)
        if hit.any():
            best = min(best, float(t[hit].min()))
    return best

def edge_dist(q, polys):
    best = math.inf
    for poly in polys:
        a = poly; b = np.roll(poly, -1, axis=0); e = b - a
        L2 = np.maximum((e ** 2).sum(1), 1e-9)
        t = np.clip(((q - a) * e).sum(1) / L2, 0, 1)
        proj = a + e * t[:, None]
        best = min(best, float(np.sqrt(((proj - q) ** 2).sum(1)).min()))
    return best

def value_noise(s, L, lam, rng_vals):
    m = len(rng_vals)
    x = (s / L) * m
    i = np.floor(x).astype(int); f = x - i
    f = (1 - np.cos(f * math.pi)) / 2
    return rng_vals[i % m] * (1 - f) + rng_vals[(i + 1) % m] * f

def blob(center, r, n, jitter, rng, ccw):
    """Irregular polygon around center; returns (n,2). r may be 0 (collapsed)."""
    ang = np.linspace(0, 2 * math.pi, n, endpoint=False) + rng.uniform(0, 2 * math.pi)
    rad = r * (1 + jitter * rng.uniform(-1, 1, n))
    pts = np.stack([center[0] + rad * np.cos(ang), center[1] + rad * np.sin(ang)], 1)
    return pts if ccw else pts[::-1]

# ---------------------------------------------------------------- per glyph
def measure_stem(font):
    gs = font.getGlyphSet(); pen = DecomposingRecordingPen(gs); gs['H'].draw(pen)
    polys = [np.array([seg_point(s, 0) for s in c]) for c in segments_from_recording(pen.value)]
    xs = []
    y = 560.0
    for poly in polys:
        a = poly; b = np.roll(poly, -1, axis=0)
        m = (a[:, 1] - y) * (b[:, 1] - y) < 0
        xs += list(a[m, 0] + (y - a[m, 1]) * (b[m, 0] - a[m, 0]) / (b[m, 1] - a[m, 1]))
    xs.sort()
    return xs[1] - xs[0]

def process_glyph(name, recs, stems):
    """recs: {w: recording}. Returns {(w, g): list of contours (np arrays)}."""
    W = list(recs)
    eff = {w: max(stems[w], 0.5 * stems[DEFAULT_W]) for w in W}  # grain floor for light weights
    damp = {w: (stems[w] / stems[DEFAULT_W]) ** -HEAVY_DAMP if stems[w] > stems[DEFAULT_W] else 1.0 for w in W}
    segsets = {w: segments_from_recording(recs[w]) for w in W}
    nC = len(segsets[DEFAULT_W])
    if nC == 0:
        return {(w, g): [] for w in W for g in (0, 1)}
    for w in W:
        assert len(segsets[w]) == nC and all(len(a) == len(b) for a, b in zip(segsets[w], segsets[DEFAULT_W])), name
    seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)

    # resample identically in every master
    samp = {w: [] for w in W}
    for ci in range(nC):
        pts = {w: [] for w in W}
        for si in range(len(segsets[DEFAULT_W][ci])):
            L = max(seg_len(segsets[w][ci][si]) for w in W)
            if L < 0.5:
                continue
            n = max(1, math.ceil(L / P['spacing']))
            for k in range(n):
                for w in W:
                    pts[w].append(seg_point(segsets[w][ci][si], k / n))
        for w in W:
            samp[w].append(np.array(pts[w], float))
    keep = [i for i in range(nC) if len(samp[DEFAULT_W][i]) >= 3]
    for w in W:
        samp[w] = [samp[w][i] for i in keep]
    nC = len(keep)

    # outward normals (sign decided once, on the default master)
    def normals(poly):
        t = np.roll(poly, -1, 0) - np.roll(poly, 1, 0)
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
        return np.stack([-t[:, 1], t[:, 0]], 1)  # left of travel
    polysD = samp[DEFAULT_W]
    sign, ink = [], []
    for ci, poly in enumerate(polysD):
        nl = normals(poly); votes = 0; inkv = []
        for i in np.linspace(0, len(poly) - 1, 7).astype(int):
            outside_left = winding(poly[i] + nl[i] * 1.5, polysD) == 0
            votes += 1 if outside_left else -1
            inkv.append(winding(poly[i] - (nl[i] if outside_left else -nl[i]) * 1.5, polysD))
        sign.append(1.0 if votes >= 0 else -1.0)
        nz = [v for v in inkv if v != 0]
        ink.append(int(np.sign(np.median(nz))) if nz else 1)
    s_ink = int(np.sign(np.median(ink))) or 1
    N = {w: [normals(samp[w][ci]) * sign[ci] for ci in range(nC)] for w in W}

    # arc length on the default master
    arcs = []
    for poly in polysD:
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
        L = d[-1] + np.linalg.norm(poly[0] - poly[-1])
        arcs.append((d, max(L, 1.0)))

    out = {}
    disp = {w: [] for w in W}
    extras = []  # list of dicts describing hole/speck contours
    for ci in range(nC):
        s, L = arcs[ci]
        wob = np.zeros(len(s))
        for lam, wgt in P['wobble_layers']:
            m = max(3, round(L / lam))
            wob += wgt * value_noise(s, L, lam, rng.uniform(-1, 1, m))
        wob /= sum(wgt for _, wgt in P['wobble_layers'])
        # edge events
        events = []
        pos = rng.exponential(P['event_gap'])
        while pos < L:
            events.append(dict(s=pos, w=rng.uniform(*P['event_width']), h=rng.uniform(0.3, 1.0) ** 0.7,
                               bite=rng.random() < P['bite_prob'], rough=rng.uniform(-1, 1, 5)))
            pos += rng.exponential(P['event_gap'])
        for w in W:
            k = stems[w] / stems[DEFAULT_W]
            d = P['wobble'] * min(max(k, 0.55), 1.0) * wob
            poly = samp[w][ci]; nrm = N[w][ci]; polysW = samp[w]
            for ev in events:
                i0 = int(np.argmin(np.abs(s - ev['s'])))
                dx = np.abs(((s - ev['s'] + L / 2) % L) - L / 2)
                if ev['bite']:
                    t_loc = ray_dist(poly[i0], -nrm[i0], polysW)
                    t_loc = min(t_loc, 1.6 * stems[w]) if np.isfinite(t_loc) else stems[w]
                    amp = -ev['h'] * P['bite_depth'] * t_loc * damp[w]
                else:
                    amp = ev['h'] * P['bump_height'] * eff[w] * damp[w]
                # rounded, blobby profile: never narrower than ~1.4x its height
                width = max(ev['w'] * math.sqrt(k), 1.4 * abs(amp))
                prof = np.where(dx < width, np.sqrt((np.cos(np.pi * dx / width) + 1) / 2), 0.0)
                d += prof * amp
            disp[w].append(d)

        # knockout holes (inside the ink) and specks (outside)
        for kind in ('hole', 'speck'):
            gap = P['hole_gap'] if kind == 'hole' else P['speck_gap']
            prob = P['hole_prob'] if kind == 'hole' else P['speck_prob']
            pos = rng.uniform(0, gap)
            while pos < L:
                if rng.random() < prob:
                    i0 = int(np.argmin(np.abs(s - pos)))
                    extras.append(dict(kind=kind, ci=ci, i=i0, frac=rng.uniform(0.44, 0.56),
                                       rf=rng.uniform(*(P['hole_r'] if kind == 'hole' else P['speck_r'])),
                                       off=rng.uniform(*P['speck_off']), n=int(rng.integers(6, 10)),
                                       jit=rng.uniform(0.15, 0.35), seed=int(rng.integers(1 << 30))))
                pos += gap * rng.uniform(0.6, 1.4)

    # resolve extras per master, validate across all masters, drop failures
    placed = []
    for ex in extras:
        geo = {}
        ok = True
        for w in W:
            poly = samp[w][ex['ci']]; nrm = N[w][ex['ci']][ex['i']]; p = poly[ex['i']]
            if ex['kind'] == 'hole':
                t = ray_dist(p, -nrm, samp[w])
                if not np.isfinite(t) or t > 2.2 * stems[w] or t < 0.45 * stems[w]:
                    ok = False; break
                c = p - nrm * t * ex['frac']; r = ex['rf'] * t * damp[w]
                if winding(c, samp[w]) != s_ink:
                    ok = False; break
                k = stems[w] / stems[DEFAULT_W]
                need = r * (1 + ex['jit']) + P['bite_depth'] * t + P['wobble'] * max(k, 0.55) + 1.0
                if edge_dist(c, samp[w]) < need:
                    ok = False; break
            else:
                r = ex['rf'] * eff[w] * damp[w]
                c = p + nrm * (r * (1 + ex['jit']) + r * ex['off'] + P['wobble'])
            geo[w] = (c, r)
        if not ok:
            continue
        clash = False
        for q in placed:
            if q['kind'] != ex['kind']:
                continue
            for w in W:
                (c1, r1), (c2, r2) = geo[w], q['geo'][w]
                if np.linalg.norm(c1 - c2) < (r1 + r2) * 1.4 + 2:
                    clash = True; break
            if clash:
                break
        if clash:
            continue
        ex['geo'] = geo; placed.append(ex)

    for w in W:
        for g in (0, 1):
            contours = []
            for ci in range(nC):
                contours.append(samp[w][ci] + (disp[w][ci] * g)[:, None] * N[w][ci])
            for ex in placed:
                c, r = ex['geo'][w]
                ccw = (s_ink > 0) if ex['kind'] == 'speck' else (s_ink < 0)
                contours.append(blob(c, r * g, ex['n'], ex['jit'], np.random.default_rng(ex['seed']), ccw))
            out[(w, g)] = contours
    return out

# ---------------------------------------------------------------- main
def main():
    os.makedirs('masters', exist_ok=True)
    fonts = {w: TTFont(f'src/master-w{w}.ttf') for w in WEIGHTS}
    stems = {w: measure_stem(fonts[w]) for w in WEIGHTS}
    print('stems', stems)
    gsets = {w: fonts[w].getGlyphSet() for w in WEIGHTS}
    order = fonts[DEFAULT_W].getGlyphOrder()
    result = {}
    for gi, name in enumerate(order):
        recs = {}
        for w in WEIGHTS:
            pen = DecomposingRecordingPen(gsets[w]); gsets[w][name].draw(pen); recs[w] = pen.value
        result[name] = process_glyph(name, recs, stems)
    for w in WEIGHTS:
        for g in (0, 1):
            f = TTFont(f'src/master-w{w}.ttf')
            glyf = f['glyf']; hmtx = f['hmtx']
            for name in order:
                gl = Glyph(); coords = []; ends = []
                for poly in result[name][(w, g)]:
                    coords += [(round(float(x)), round(float(y))) for x, y in poly]
                    ends.append(len(coords) - 1)
                gl.numberOfContours = len(ends)
                if ends:
                    gl.coordinates = GlyphCoordinates(coords); gl.endPtsOfContours = ends
                    gl.flags = bytearray([1] * len(coords))
                    gl.program = ttProgram.Program(); gl.program.fromBytecode(b'')
                    gl.recalcBounds(glyf)
                glyf[name] = gl
                adv, _ = hmtx[name]
                hmtx[name] = (adv, getattr(gl, 'xMin', 0) if gl.numberOfContours else 0)
            for t in ('fpgm', 'prep', 'cvt ', 'gasp', 'hdmx', 'LTSH', 'VDMX'):
                if t in f:
                    del f[t]
            f.save(f'masters/w{w}-g{g * 100}.ttf')
            print('wrote', w, g)

if __name__ == '__main__':
    main()
