from PIL import Image, ImageDraw, ImageFont
import sys
sys.argv=[0]; exec(open('proof.py').read().split('rows=[]')[0])
img=Image.new('L',(2400,1900),255);d=ImageDraw.Draw(img)
for i,(cut,p) in enumerate((('Display',0),('H1',50),('H2',100))):
    y=i*620
    d.text((20,y+5),f'{cut} 700 (yours)  |  Press {p} (new)',font=lab,fill=110)
    d.text((20,y-60),'ag',font=ImageFont.truetype(f'NewsreaderLetterpress-{cut}-700.ttf',560),fill=0)
    d.text((1220,y-60),'ag',font=vf(560,700,16,p),fill=0)
img.save('close-compare.png')
