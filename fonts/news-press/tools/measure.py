from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import numpy as np, sys
def flat(rec, steps=16):
    polys=[];cur=[];
    for op,args in rec.value:
        if op=='moveTo': cur=[args[0]]
        elif op=='lineTo': cur.append(args[0])
        elif op=='qCurveTo':
            pts=list(args); p0=cur[-1]
            # implied on-curves
            offs=pts[:-1]; end=pts[-1]
            ons=[]
            for k in range(len(offs)-1): ons.append(((offs[k][0]+offs[k+1][0])/2,(offs[k][1]+offs[k+1][1])/2))
            seq=[p0]
            segs=[]; a=p0
            for k,o in enumerate(offs):
                b=ons[k] if k<len(ons) else end
                for t in np.linspace(0,1,steps)[1:]:
                    cur.append(((1-t)**2*a[0]+2*(1-t)*t*o[0]+t*t*b[0],(1-t)**2*a[1]+2*(1-t)*t*o[1]+t*t*b[1]))
                a=b
        elif op in('closePath','endPath'):
            if len(cur)>2: polys.append(cur)
            cur=[]
    return polys
def shape(polys):
    # even-odd via symmetric difference
    g=None
    for p in polys:
        P=Polygon(p).buffer(0)
        g=P if g is None else g.symmetric_difference(P)
    return g
src=instantiateVariableFont(TTFont('src/Newsreader[opsz,wght].ttf'),{'wght':int(sys.argv[2]),'opsz':16})
u=TTFont(sys.argv[1]); ug=u.getGlyphSet(); sg=src.getGlyphSet(); cm=u.getBestCmap(); scm=src.getBestCmap()
segs=[];disp=[];holes=0;hole_sizes=[];area=0;holepts=[]
for c in 'HOnoaegRskmd':
    r=RecordingPen(); sg[scm[ord(c)]].draw(r); S=shape(flat(r.value and r))
    gl=u['glyf'][cm[ord(c)]]; co,ends,fl=gl.getCoordinates(u['glyf']); co=np.array(co); s=0
    nsrc=len(flat(r))
    conts=[]
    for e in ends: conts.append(co[s:e+1]); s=e+1
    conts.sort(key=lambda a:-len(a))
    main=conts[:nsrc]; extra=conts[nsrc:]
    for m in main:
        d=np.linalg.norm(np.diff(np.vstack([m,m[:1]]),axis=0),axis=1); segs+=list(d)
        bd=S.boundary
        for p in m[::3]:
            P=Point(p); dd=bd.distance(P); disp.append(dd if S.contains(P) else -dd)  # + = inside (bite), - = outside (bump)
    for x in extra:
        pg=Polygon(x); hole_sizes.append(np.sqrt(abs(pg.area))); holepts.append(len(x))
    area+=S.area
segs=np.array(segs);disp=np.array(disp)
print(sys.argv[1].split('-',1)[1], 'seg median %.1f p10 %.1f p90 %.1f'%(np.median(segs),np.percentile(segs,10),np.percentile(segs,90)),
 '| disp sd %.1f mean %.1f p5 %.1f p95 %.1f'%(disp.std(),disp.mean(),np.percentile(disp,5),np.percentile(disp,95)),
 '| holes %d per 1e6 area %.1f, size med %.1f p90 %.1f, pts %s'%(len(hole_sizes),len(hole_sizes)/area*1e6,np.median(hole_sizes),np.percentile(hole_sizes,90),np.bincount(holepts).nonzero()[0].tolist()))
# autocorrelation of signed displacement along the H main contour
r=RecordingPen(); sg[scm[ord('H')]].draw(r); S=shape(flat(r)); bd=S.boundary
gl=u['glyf'][cm[ord('H')]]; co,ends,fl=gl.getCoordinates(u['glyf']); co=np.array(co); m=co[:ends[0]+1]
if len(m)<100:
    s=0;cs=[]
    for e in ends: cs.append(co[s:e+1]); s=e+1
    m=max(cs,key=len)
dd=np.array([(bd.distance(Point(p)))*(1 if S.contains(Point(p)) else -1) for p in m])
dd-=dd.mean()
print('  autocorr', [round(float(np.corrcoef(dd[:-k],dd[k:])[0,1]),2) for k in (1,2,3,5,8)])
