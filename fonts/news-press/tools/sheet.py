from PIL import Image, ImageDraw, ImageFont
VF='fonts/NewsreaderLetterpress[PRES,opsz,wght].ttf'
lab=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
def vf(size,w,o,p):
    f=ImageFont.truetype(VF,size); names=[a['name'] for a in f.get_variation_axes()]
    vals={'Weight':w,'Optical size':o,'Press':p}
    f.set_variation_by_axes([vals[n.decode() if isinstance(n,bytes) else n] for n in names]); return f
W=(200,400,600,800); P=(0,50,100)
img=Image.new('L',(2600,150+len(W)*230+60+3*230),255); d=ImageDraw.Draw(img)
d.text((20,20),'Newsreader Letterpress (variable) — weight down, press across, optical size 18',font=lab,fill=90)
for j,p in enumerate(P): d.text((200+j*800,70),f'Press {p}',font=lab,fill=90)
for i,w in enumerate(W):
    y=110+i*230; d.text((20,y+90),f'wght {w}',font=lab,fill=90)
    for j,p in enumerate(P): d.text((200+j*800,y),'Hamburg',font=vf(170,w,18,p),fill=0)
y0=110+len(W)*230+40; d.text((20,y0),'Optical size at wght 400, Press 50:',font=lab,fill=90)
for i,o in enumerate((6,18,72)):
    y=y0+40+i*230; d.text((20,y+90),f'opsz {o}',font=lab,fill=90); d.text((200,y),'Letterpress Rag',font=vf(170,400,o,50),fill=0)
img.save('sheet.png')
