import sys
from PIL import Image, ImageDraw, ImageFont
FONT = sys.argv[1]; OUT = sys.argv[2]
def F(px, w, g):
    f = ImageFont.truetype(FONT, px)
    axes = {a['name'] if isinstance(a['name'], str) else a['name'].decode(): a for a in f.get_variation_axes()}
    f.set_variation_by_axes([w, g] if list(axes)[0].startswith(b'W'.decode()) else [g, w]) if False else None
    vals = []
    for a in f.get_variation_axes():
        nm = a['name'] if isinstance(a['name'], str) else a['name'].decode()
        vals.append(w if nm.lower().startswith('weight') else g)
    f.set_variation_by_axes(vals); return f
W = 2400
img = Image.new('RGB', (W, 2300), '#f2eee6'); d = ImageDraw.Draw(img)
lab = ImageFont.truetype(FONT, 22)
y = 30
for g in (0, 50, 100):
    d.text((40, y), f'GRAN {g}', font=F(22, 500, 0), fill='#c2410c'); y += 34
    x = 40
    for w in (100, 400, 700):
        d.text((x, y), 'Rag', font=F(260, w, g), fill='#141414'); x += 760
    y += 330
for g in (0, 100):
    d.text((40, y), f'GRAN {g} — 64px / 28px / 16px', font=F(22, 500, 0), fill='#c2410c'); y += 34
    d.text((40, y), 'Grain in the type. Authentic, imperfect.', font=F(64, 400, g), fill='#141414'); y += 90
    d.text((40, y), 'The quick brown fox jumps over the lazy dog — 0123456789 &?!', font=F(28, 400, g), fill='#141414'); y += 44
    d.text((40, y), 'Edges with grain poking out and knockouts poking in, across every weight from Thin to Bold.', font=F(16, 400, g), fill='#141414'); y += 50
img.crop((0, 0, W, y + 20)).save(OUT)
