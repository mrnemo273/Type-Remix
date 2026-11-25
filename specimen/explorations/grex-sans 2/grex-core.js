/* Grex Sans — shared specimen components (Brief 02). */
(function(){
const GX={};
GX.fvs=(el,w,g)=>{el.style.fontWeight=Math.round(w);el.style.fontVariationSettings=`'GRAN' ${Math.round(g)}`};
GX.clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
GX.reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
GX.grainForSize=px=>Math.round(GX.clamp((px-14)/(110-14),0,1)*100);
let DATA=null;GX.load=()=>DATA?Promise.resolve(DATA):fetch('data.json').then(r=>r.json()).then(d=>DATA=d);

/* exact outline interpolation (same maths as the font) */
function avarMap(D,n){const s=Object.entries(D.avar).map(([a,b])=>[+a,+b]).sort((a,b)=>a[0]-b[0]);
  for(let i=1;i<s.length;i++){if(n<=s[i][0]){const[a0,b0]=s[i-1],[a1,b1]=s[i];return b0+(n-a0)/(a1-a0)*(b1-b0)}}return n}
GX.coords=(D,g,w,gr)=>{const n=avarMap(D,(w-400)/300),t=gr/100,L=(a,b,u)=>a.map((v,i)=>v+(b[i]-v)*u);
  const at=k=>n<0?L(g.m['400-'+k],g.m['100-'+k],-n):L(g.m['400-'+k],g.m['700-'+k],n);
  return{c:L(at(0),at(100),t),adv:n<0?g.adv_400+(g.adv_100-g.adv_400)*-n:g.adv_400+(g.adv_700-g.adv_400)*n}};
GX.pointCounts=D=>({plex:D.drawn.glyphs.reduce((a,g)=>a+g.plexPts,0),grex:D.drawn.glyphs.reduce((a,g)=>a+g.m['400-0'].length/2,0)});

/* draw the word as raw outlines + points on a canvas. opts: ink, fill, dot, line, scale, clip(x,y,r) */
GX.drawWord=(cv,D,w,g,o={})=>{const r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1;
  if(cv.width!==Math.round(r.width*dpr)||cv.height!==Math.round(r.height*dpr)){cv.width=Math.round(r.width*dpr);cv.height=Math.round(r.height*dpr)}
  const x=cv.getContext('2d');x.setTransform(dpr,0,0,dpr,0,0);if(!o.keep)x.clearRect(0,0,r.width,r.height);
  const gl=D.drawn.glyphs.map(q=>GX.coords(D,q,w,g)),total=gl.reduce((a,q)=>a+q.adv,0);
  const s=o.scale||Math.min(r.width*.9/total,r.height*.66/D.metrics.cap);const ox=o.ox??(r.width-total*s)/2,base=o.base??(r.height/2+D.metrics.cap*s/2);
  if(o.clip){x.save();x.beginPath();x.arc(o.clip[0],o.clip[1],o.clip[2],0,7);x.clip();if(o.bg){x.fillStyle=o.bg;x.fill()}}
  if(o.line){x.strokeStyle=o.line;x.lineWidth=1;x.setLineDash([3,4]);[0,D.metrics.xheight,D.metrics.cap].forEach(v=>{x.beginPath();x.moveTo(0,base-v*s+.5);x.lineTo(r.width,base-v*s+.5);x.stroke()});x.setLineDash([])}
  let pen=ox;gl.forEach((q,gi)=>{const ends=D.drawn.glyphs[gi].ends,c=q.c;x.beginPath();let st=0;
    ends.forEach(e=>{for(let i=st;i<=e;i++){const px=pen+c[2*i]*s,py=base-c[2*i+1]*s;i==st?x.moveTo(px,py):x.lineTo(px,py)}x.closePath();st=e+1});
    x.fillStyle=o.fill||'rgba(0,0,0,.06)';x.fill('nonzero');x.strokeStyle=o.ink||'#111';x.lineWidth=o.lw||.9;x.stroke();
    if(o.dot!==false){x.fillStyle=o.dot||'#ff48b0';const d=o.dotSize||2;for(let i=0;i<c.length/2;i++)x.fillRect(pen+c[2*i]*s-d/2,base-c[2*i+1]*s-d/2,d,d)}
    pen+=q.adv*s});
  if(o.clip)x.restore();return{s,ox,base,total}};

/* 2-D pad: x = weight 100–700, y = grain 0–100 */
GX.pad=(el,state,onChange)=>{const dot=el.querySelector('.dot');
  const show=()=>{const px=(state.w-100)/6,py=state.g;if(dot){dot.style.left=px+'%';dot.style.top=py+'%'}el.style.setProperty('--px',px+'%');el.style.setProperty('--py',py+'%');
    el.setAttribute('aria-valuetext',`weight ${Math.round(state.w)}, grain ${Math.round(state.g)}`);onChange(state)};
  const mv=e=>{const r=el.getBoundingClientRect();state.w=100+600*GX.clamp((e.clientX-r.left)/r.width,0,1);state.g=100*GX.clamp((e.clientY-r.top)/r.height,0,1);show()};
  el.addEventListener('pointerdown',e=>{el.setPointerCapture(e.pointerId);mv(e)});el.addEventListener('pointermove',e=>{if(e.buttons)mv(e)});
  el.addEventListener('keydown',e=>{const k={ArrowLeft:[-20,0],ArrowRight:[20,0],ArrowUp:[0,-5],ArrowDown:[0,5]}[e.key];if(k){e.preventDefault();state.w=GX.clamp(state.w+k[0],100,700);state.g=GX.clamp(state.g+k[1],0,100);show()}});
  show();return show};

/* touch-to-wear headline */
GX.wearLine=(el,text,{seed=true,onWear}={})=>{let chars=[],rects=[],last=null;
  const render=()=>{let t=0;chars.forEach(c=>{c.wear=GX.clamp(c.wear,0,100);GX.fvs(c.el,700-c.wear*1.6,c.wear);t+=c.wear});onWear&&onWear(Math.round(t/Math.max(1,chars.length)))};
  const measure=()=>{rects=chars.map(c=>c.el.getBoundingClientRect())};
  const build=(txt,sd)=>{el.innerHTML='';chars=[];let wd=null;[...txt].forEach((ch,i)=>{const s=document.createElement('span');
    if(ch===' '){el.appendChild(document.createTextNode(' '));wd=null;return}
    s.textContent=ch;if(!wd){wd=document.createElement('span');wd.className='wd';el.appendChild(wd)}wd.appendChild(s);
    chars.push({el:s,wear:sd?Math.max(0,Math.sin(i*1.7)*60+Math.cos(i*.6)*30):0})});render();measure()};
  el.addEventListener('pointermove',e=>{const p={x:e.clientX,y:e.clientY};if(!last){last=p;return}const v=Math.hypot(p.x-last.x,p.y-last.y);last=p;
    chars.forEach((c,i)=>{const r=rects[i];if(!r)return;const d=Math.hypot(r.left+r.width/2-p.x,(r.top+r.height/2-p.y)*.6),R=r.height*.55;if(d<R)c.wear+=v*.09*(1-d/R)});render()});
  el.addEventListener('pointerleave',()=>last=null);addEventListener('resize',measure);addEventListener('scroll',measure,{passive:true});
  build(text,seed);return{build:t=>build(t||' ',false),set:v=>{chars.forEach(c=>c.wear=v);render()}}};

/* overprint poster */
GX.WORDS=['GREX','GRAIN','INK','WEAR','PRESS','TOOTH','PULL','PROOF','RUN','STOCK','SPECK','BITE','GRIT','PAPER'];
GX.pull=(P,inks,n)=>{P.querySelectorAll('.ov').forEach(s=>s.remove());const W=P.clientWidth,H=P.clientHeight,rnd=(a,b)=>a+Math.random()*(b-a),pick=a=>a[Math.floor(Math.random()*a.length)];
  inks.forEach((ink,li)=>{for(let k=0;k<(li==inks.length-1?2:3);k++){const s=document.createElement('span');s.className='ov';s.textContent=pick(GX.WORDS);
    s.style.cssText=`position:absolute;white-space:nowrap;mix-blend-mode:multiply;line-height:.8;transform-origin:left top;color:${ink};font-size:${rnd(.16,.42)*W}px;left:${rnd(-.15,.55)*W}px;top:${rnd(-.05,.82)*H}px;transform:rotate(${pick([0,0,-90,90,rnd(-8,8)])}deg)`;
    GX.fvs(s,pick([300,500,700,700]),pick([40,70,100,100]));P.appendChild(s)}})};

/* feature demo strings with the changed glyphs wrapped */
GX.HL={ss01:/[aáàâäãåāăą]/g,ss02:/[gğĝģġ]/g,ss03:/0/g,ss04:/0/g,ss05:/ß/g,onum:/\d/g,frac:/3\/4/g,sups:/2/g,subs:/2/g,ordn:/\d[ao]/g,liga:/fi/g};
GX.featHTML=(f,cls='hl')=>f.sample.replace(GX.HL[f.tag],m=>`<span class="${cls}">${m}</span>`);
window.GX=GX;
})();
