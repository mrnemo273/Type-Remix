"""Subset Plex Sans Var to Latin and cut static masters at wght 100/400/700, wdth 100."""
import sys
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer
UNI = ("U+0020-007E,U+00A0-017F,U+0192,U+0218-021B,U+02C6-02DD,U+2010-2027,U+2030-203A,"
       "U+2044,U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+2248,U+2260,U+2264,U+2265,U+25CF")
f = TTFont('src/PlexSansVar-Roman.ttf')
opts = subset.Options(); opts.layout_features = ['*']; opts.glyph_names = True
opts.name_IDs = ['*']; opts.notdef_outline = True; opts.hinting = False
s = subset.Subsetter(opts); s.populate(unicodes=subset.parse_unicodes(UNI)); s.subset(f)
f.save('src/sub.ttf')
for w in (100, 400, 700):
    v = TTFont('src/sub.ttf')
    inst = instancer.instantiateVariableFont(v, {'wght': w, 'wdth': 100})
    inst.save(f'src/master-w{w}.ttf')
    print(w, len(inst.getGlyphOrder()))
