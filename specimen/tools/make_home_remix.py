"""Brief 05: animate the word 'Remix' in the home page title. Builds three explorations
(mild, middle, wild) from the current home page into explorations/home/brief-05-*/index.html."""
import os,re,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
home=open(os.path.join(ROOT,'index.html')).read()
FONTS=[]
for slug,fam in (('grex-sans','RX Grex'),('news-press','RX News'),('worked-sans','RX Worked')):
    d=json.load(open(os.path.join(ROOT,slug,'data.json')))
    FONTS.append(dict(fam=fam,src=f'{slug}/font.woff2',axes={a['tag']:[a['min'],a['max']] for a in d['axes']}))
CSS="""<style>
%s
.hero h1 .rx{display:inline-block;letter-spacing:0}
.hero h1 .rx.keep{letter-spacing:inherit}
.hero h1 .rx .l{display:inline-block;transform-origin:50%% 100%%;will-change:transform}
.rxbtn{position:fixed;top:clamp(10px,1.6vw,22px);z-index:60;display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%%;border:2px solid #1d1d1f;background:rgba(251,251,249,.9);color:#1d1d1f;cursor:pointer}
.rxbtn.snd{right:var(--gut)}.rxbtn .x{display:none}.rxbtn[aria-pressed=false] .x{display:inline}.rxbtn[aria-pressed=false] .w{display:none}
.rxback{position:fixed;left:var(--gut);top:clamp(10px,1.6vw,22px);z-index:60;font:600 13px/1 'IS',system-ui,sans-serif;padding:11px 16px;border-radius:999px;border:2px solid #1d1d1f;color:#1d1d1f;background:rgba(251,251,249,.9);text-decoration:none}
.rxtag{position:fixed;left:50%%;transform:translateX(-50%%);top:clamp(22px,2.6vw,36px);z-index:60;font:500 11px/1 'IS',system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#86868b}
</style>"""
FF='\n'.join(f"@font-face{{font-family:'{f['fam']}';src:url('{f['src']}') format('woff2');font-weight:1 1000;font-display:block}}" for f in FONTS)
JS=r"""<script>
(()=>{const MODE='__MODE__',FONTS=__FONTS__,EVERY=6500;
/* sound: the same soft click as the specimen heroes, one per letter */
const SND=(()=>{let ctx=null,on=true,un=false,nb=null,bs=null;try{on=localStorage.getItem('tr-sound')!=='off'}catch(e){}
  const get=()=>{if(!ctx){const AC=window.AudioContext||window.webkitAudioContext;if(!AC)return null;ctx=new AC()}if(ctx.state==='suspended')ctx.resume();return ctx};
  ['pointerdown','keydown','touchend'].forEach(ev=>addEventListener(ev,()=>{un=true;if(on)get()},{once:true,passive:true}));
  const noise=c=>{if(!nb){nb=c.createBuffer(1,c.sampleRate*.25|0,c.sampleRate);const d=nb.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1}return nb};
  const bus=c=>{if(!bs){const k=c.createDynamicsCompressor();k.threshold.value=-24;k.ratio.value=4;k.attack.value=.003;k.release.value=.2;const g=c.createGain();g.gain.value=.9;k.connect(g).connect(c.destination);bs=k}return bs};
  const ok=()=>on&&un&&ctx&&ctx.state==='running';
  const burst=(c,t,type,freq,q,gain,len)=>{const n=c.createBufferSource(),f=c.createBiquadFilter(),g=c.createGain();n.buffer=noise(c);f.type=type;f.frequency.value=freq;f.Q.value=q;
    g.gain.setValueAtTime(gain,t);g.gain.exponentialRampToValueAtTime(.0001,t+len);n.connect(f).connect(g).connect(c.destination);n.start(t);n.stop(t+len+.01)};
  return{press(i=0){if(!ok())return;const c=ctx,t=c.currentTime,o=c.createOscillator(),g=c.createGain(),j=1+((i*37)%9-4)*.025,out=bus(c);
      o.type='sine';o.frequency.setValueAtTime(170*j,t);o.frequency.exponentialRampToValueAtTime(80*j,t+.06);
      g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(.045,t+.004);g.gain.exponentialRampToValueAtTime(.0001,t+.09);o.connect(g).connect(out);o.start(t);o.stop(t+.1);
      burst(c,t,'bandpass',2000*j,1.2,.035,.03)},
    get on(){return on},set(v){on=v;try{localStorage.setItem('tr-sound',v?'on':'off')}catch(e){}if(v){un=true;get()}}}})();
{const b=document.getElementById('rxsnd'),u=()=>{const t=SND.on?'Sound on':'Sound off';b.setAttribute('aria-pressed',SND.on);b.setAttribute('aria-label',t);b.title=t};u();b.onclick=()=>{SND.set(!SND.on);u()}}

/* split the title: 'Type-' stays as it is, the letters of 'Remix' get remixed */
const h=document.getElementById('title'),word=h.textContent,cut=MODE==='whole'?0:word.lastIndexOf('-')+1;
h.innerHTML=`<span><span class="ty">${word.slice(0,cut)}</span><span class="rx${MODE==='whole'?' keep':''}">${[...word.slice(cut)].map(c=>`<span class="l">${c}</span>`).join('')}</span></span>`;
const outer=h.firstChild,L=[...h.querySelectorAll('.rx .l')];
const R=Math.random,pick=a=>a[Math.floor(R()*a.length)],lerp=(a,b,t)=>a+(b-a)*t,snap=(t,n)=>Math.round(t*(n-1))/(n-1);
/* one setting for a font: weight never too thin at this size, the remix axis anywhere along its range */
const setting=(f,floor)=>{const v={};for(const[tag,[lo,hi]]of Object.entries(f.axes))v[tag]=Math.round(lerp(lo,hi,tag==='wght'?lerp(floor,1,snap(R(),5)):snap(R(),5)));return v};
const style=(f,v,extra={})=>({fontFamily:`'${f.fam}'`,fontVariationSettings:Object.entries(v).map(([k,x])=>`'${k}' ${x}`).join(', '),fontWeight:'normal',...extra});
let prevF=-1;
const plan=()=>{
  if(MODE==='mild'){let k;do k=Math.floor(R()*FONTS.length);while(k===prevF&&FONTS.length>1);prevF=k;const f=FONTS[k],v=setting(f,.35);return L.map(()=>style(f,v))}
  if(MODE==='middle'||MODE==='whole'){let ks;do ks=L.map(()=>Math.floor(R()*FONTS.length));while(new Set(ks).size<2);return ks.map(k=>style(FONTS[k],setting(FONTS[k],.35)))}
  return L.map(()=>{const f=pick(FONTS);return style(f,setting(f,0),{rotate:`${(R()-.5)*8}deg`,translate:`0 ${(R()-.5)*.07}em`})})};
const apply=(el,s)=>{el.style.letterSpacing='-.01em';el.style.fontFamily=s.fontFamily;el.style.fontVariationSettings=s.fontVariationSettings;el.style.rotate=s.rotate||'';el.style.translate=s.translate||''};
/* measure the new word before it lands, so the whole title can resize to fill the width while the letters drop in */
const measure=st=>{const c=outer.cloneNode(true);c.style.cssText='position:absolute;visibility:hidden;left:0;top:0';[...c.querySelectorAll('.rx .l')].forEach((el,i)=>apply(el,st[i]));h.appendChild(c);const w=c.getBoundingClientRect().width;c.remove();return w};
const target=st=>{const t=parseFloat(getComputedStyle(h).fontSize)*h.clientWidth/measure(st)*.995;return cap?Math.min(t,cap*h.clientWidth):t};
let ratio=0,cap=0;const box=()=>{h.style.height=(h.clientWidth*ratio)+'px'};
if(MODE==='whole'){h.style.display='flex';h.style.alignItems='flex-end';h.parentElement.style.overflowX='clip';
  document.fonts.ready.then(()=>{const w=h.clientWidth,f=parseFloat(getComputedStyle(h).fontSize);cap=f/w*1.12;ratio=h.getBoundingClientRect().height/w*1.12;box()});
  if('ResizeObserver'in window)new ResizeObserver(()=>{if(ratio)box()}).observe(h.parentElement)}
let visible=true;if('IntersectionObserver'in window)new IntersectionObserver(e=>{visible=e[0].intersectionRatio>.3},{threshold:[0,.3,.6]}).observe(h);
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const beat=150,flam=65,groups=[1,2,1],dur=260,press=.06;
const times=()=>{let t=0,g=0,n=0;return L.map(()=>{if(n===groups[g%groups.length]){g++;n=0;t+=beat}else if(n>0)t+=flam;n++;return Math.max(0,t+(R()-.5)*14)})};
const change=()=>{const st=plan(),fs=target(st),tm=times(),span=tm[tm.length-1]+dur;
  h.style.transition=reduce?'none':`font-size ${span}ms cubic-bezier(.3,.7,.2,1)`;h.style.fontSize=fs+'px';setTimeout(()=>h.style.transition='',span+50);
  L.forEach((el,i)=>setTimeout(()=>{if(!reduce)el.animate([{transform:'translateY(0) scaleY(1)'},{transform:`translateY(${press}em) scaleY(${1-press*.6})`,offset:.35},{transform:`translateY(${-press*.25}em) scaleY(1)`,offset:.7},{transform:'translateY(0) scaleY(1)'}],{duration:dur,easing:'cubic-bezier(.3,.7,.4,1)'});
    setTimeout(()=>{apply(el,st[i]);if(visible)SND.press(i)},dur*.33)},tm[i]))};
document.fonts.ready.then(()=>Promise.all(FONTS.map(f=>document.fonts.load(`100px '${f.fam}'`,'Remix')))).then(()=>{setTimeout(()=>{change();setInterval(()=>{if(!document.hidden)change()},EVERY)},2500)});
})();
</script>"""
LABEL={'mild':'Mild','middle':'Middle','wild':'Wild','whole':'Chosen'}
for mode in ('mild','middle','wild','whole'):
    s=home
    s=s.replace('<head>','<head>\n<base href="../../../">',1)
    s=s.replace('</head>',(CSS%FF)+'\n</head>',1)
    btn=('<a class="rxback" href="explorations/index.html">&larr; Explorations</a>'
         f'<span class="rxtag">Brief 05 &middot; {LABEL[mode]}</span>'
         '<button class="rxbtn snd" id="rxsnd" type="button" aria-pressed="true"><svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true"><path d="M2 6h3l4-3v10l-4-3H2z" fill="currentColor"/><path class="w" d="M11 5.5a3.5 3.5 0 0 1 0 5M12.8 3.6a6 6 0 0 1 0 8.8" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path class="x" d="M11 6l4 4M15 6l-4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg></button>')
    i=s.index('<body');i=s.index('>',i)+1;s=s[:i]+'\n'+btn+s[i:]
    js=JS.replace('__MODE__',mode).replace('__FONTS__',json.dumps([dict(fam=f['fam'],axes=f['axes']) for f in FONTS]))
    k=s.rindex('</body>');s=s[:k]+js+'\n'+s[k:]
    s=re.sub(r'<title>[^<]*</title>',f'<title>Brief 05 · {LABEL[mode]} · Type-Remix</title>',s,count=1)
    out=os.path.join(ROOT,'explorations','home',f'brief-05-{"chosen" if mode=="whole" else mode}');os.makedirs(out,exist_ok=True)
    open(os.path.join(out,'index.html'),'w').write(s);print('wrote',out)
