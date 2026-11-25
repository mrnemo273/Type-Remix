from PIL import Image, ImageDraw, ImageFont
import sys
VF=sys.argv[1] if len(sys.argv)>1 else 'fonts/NewsreaderLetterpress[PRES,opsz,wght].ttf'
lab=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def vf(size,w,o,p):
    f=ImageFont.truetype(VF,size); names=[a['name'] for a in f.get_variation_axes()]
    vals={'Weight':w,'Optical size':o,'Press':p}
    f.set_variation_by_axes([vals.get(n.decode() if isinstance(n,bytes) else n) for n in names]); return f
rows=[]
for cut,p in (('Display',0),('H1',50),('H2',100)):
    for w in (500,700):
        rows.append((f'yours: {cut} {w}',ImageFont.truetype(f'NewsreaderLetterpress-{cut}-{w}.ttf',300)))
        rows.append((f'new: Press {p}, wght {w}, opsz 16',vf(300,w,16,p)))
img=Image.new('L',(2200,len(rows)*340+20),255);d=ImageDraw.Draw(img)
for i,(t,f) in enumerate(rows):
    y=10+i*340; d.text((20,y),t,font=lab,fill=110); d.text((20,y+10),'Ragfeh',font=f,fill=0)
img.save('proof-compare.png')
img.crop((0,0,2200,1380)).save('proof-compare-top.png')
