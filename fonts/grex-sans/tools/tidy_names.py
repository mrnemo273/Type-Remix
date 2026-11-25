"""Credit the modifications inside each font file. Original copyright lines and designer credits stay as they are."""
import glob, os, sys
from fontTools.ttLib import TTFont
root = sys.argv[1]
for ttf in sorted(glob.glob(os.path.join(root, '*/fonts/*.ttf'))):
    f = TTFont(ttf); nm = f['name']
    cp = nm.getDebugName(0) or ''
    if 'Modifications copyright' not in cp:
        nm.setName(cp.rstrip('. ') + '. Modifications copyright 2026 Juan-Carlos Morales.', 0, 3, 1, 0x409)
    nm.setName('Juan-Carlos Morales', 8, 3, 1, 0x409)
    nm.setName('https://juanemo.com', 11, 3, 1, 0x409)
    for rec in [r for r in nm.names if r.nameID in (0, 8, 11) and r.platformID == 1]:
        nm.names.remove(rec)
    f.save(ttf); f.flavor = 'woff2'; f.save(ttf.replace('.ttf', '.woff2'))
    print(os.path.basename(ttf), '|', TTFont(ttf)['name'].getDebugName(0))
for ofl in sorted(glob.glob(os.path.join(root, '*/OFL.txt'))):
    s = open(ofl).read()
    if 'Juan-Carlos Morales' not in s:
        open(ofl, 'w').write('Copyright 2026 Juan-Carlos Morales (modifications)\n' + s)
    print(ofl.split('/')[-2], open(ofl).readline().strip())
