import sys
from PIL import Image, ImageDraw, ImageFont
R='fonts/WorkedSans[WORK,wght].ttf'; I='fonts/WorkedSans-Italic[WORK,wght].ttf'
def F(path,px,w,k):
    f=ImageFont.truetype(path,px); vals=[]
    for a in f.get_variation_axes():
        n=a['name'] if isinstance(a['name'],str) else a['name'].decode(); vals.append(w if n.lower().startswith('weight') else k)
    f.set_variation_by_axes(vals); return f
import os
W=2400; img=Image.new('RGB',(W,3000),'#f4f2ee'); d=ImageDraw.Draw(img); y=30
lab=lambda t:d.text((40,y),t,font=F(R,24,500,0),fill='#c2410c')
for k in (0,50,100):
    lab(f'WORK {k}'); y+=36; x=40
    for w in (100,400,900):
        d.text((x,y),'Hamk',font=F(R,230,w,k),fill='#141414'); x+=780
    y+=290
# overlay close-up: WORK 0 in red under WORK 100 in black
lab('Overlay at 900 · red = Work Sans, black = Worked Sans'); y+=40
d.text((40,y),'EVAK4',font=F(R,420,900,0),fill='#ff3b30'); 
ov=Image.new('L',(W,520),0); ImageDraw.Draw(ov).text((40,0),'EVAK4',font=F(R,420,900,100),fill=255)
img.paste(Image.new('RGB',(W,520),'#141414'),(0,y),ov); y+=540
d=ImageDraw.Draw(img)
if os.path.exists(I):
    lab('Italic · WORK 100'); y+=36
    d.text((40,y),'Worked in, imperfect.',font=F(I,120,500,100),fill='#141414'); y+=170
lab('Text · WORK 0 / WORK 100'); y+=36
for k in (0,100):
    d.text((40,y),'The quick brown fox jumps over the lazy dog — 0123456789 & ?!',font=F(R,40,400,k),fill='#141414'); y+=60
img.crop((0,0,W,y+20)).save(sys.argv[1])
