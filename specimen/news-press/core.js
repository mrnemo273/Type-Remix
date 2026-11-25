/* Specimen core — generic helpers driven by data.json (axes, metrics, outlines). */
(function(){
const S={};
S.clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
S.reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
S.load=()=>(window.SPEC_DATA?Promise.resolve(window.SPEC_DATA):fetch('data.json').then(r=>r.json())).then(D=>{S.D=D;S.axes=D.axes;S.byTag=Object.fromEntries(D.axes.map(a=>[a.tag,a]));S.cfg=D.config||{};return D});

/* axis values: objects like {wght:700,GRAN:100}; missing axes use their default */
S.fv=(vals,noW)=>S.axes.filter(a=>!(noW&&a.tag==='wght')).map(a=>`'${a.tag}' ${Math.round((vals&&vals[a.tag]!=null)?vals[a.tag]:a.default)}`).join(', ')||'normal';
S.set=(el,vals)=>{el.style.fontVariationSettings=S.fv(vals);if(vals&&vals.wght!=null)el.style.fontWeight=Math.round(vals.wght)};
/* u in 0..1 along an axis */
S.at=(tag,u)=>{const a=S.byTag[tag];return a?a.min+(a.max-a.min)*S.clamp(u,0,1):null};
S.allAt=u=>Object.fromEntries(S.axes.map(a=>[a.tag,a.min+(a.max-a.min)*u]));
S.label=tag=>{const c=(S.cfg.axes||{})[tag]||{};const a=S.byTag[tag];return c.label||(a&&a.name)||tag};

/* exact outline interpolation over the -1/0/+1 grid exported by the build script */
function avar(a,n){if(!a.avar)return n;const s=a.avar;for(let i=1;i<s.length;i++){if(n<=s[i][0]){const[x0,y0]=s[i-1],[x1,y1]=s[i];return y0+(n-x0)/(x1-x0)*(y1-y0)}}return n}
function norm(a,v){const n=v<a.default?(v-a.default)/(a.default-a.min||1):(v-a.default)/(a.max-a.default||1);return avar(a,S.clamp(n,-1,1))}
S.coords=(g,vals)=>{const dr=S.D.drawn,tags=dr.axes;let corners=[{key:[],w:1}];
  tags.forEach(t=>{const a=S.byTag[t],st=dr.stops[t],n=norm(a,vals[t]??a.default);let lo=st[0],hi=st[st.length-1];
    for(let i=0;i<st.length-1;i++)if(n>=st[i]&&n<=st[i+1]){lo=st[i];hi=st[i+1];break}
    const u=hi===lo?0:(n-lo)/(hi-lo),next=[];corners.forEach(c=>{next.push({key:[...c.key,lo],w:c.w*(1-u)});if(hi!==lo)next.push({key:[...c.key,hi],w:c.w*u})});corners=next});
  const n=g.m[Object.keys(g.m)[0]].length,c=new Float64Array(n);let adv=0;
  corners.forEach(k=>{if(!k.w)return;const key=k.key.join(','),m=g.m[key];for(let i=0;i<n;i++)c[i]+=m[i]*k.w;adv+=g.adv[key]*k.w});return{c,adv}};
S.points=()=>S.D.drawn.glyphs.reduce((a,g)=>a+g.flags.length,0);

/* draw the outline word: quadratic TrueType contours + on/off-curve points */
S.drawWord=(cv,vals,o={})=>{const D=S.D,r=cv.getBoundingClientRect(),dpr=devicePixelRatio||1;
  if(cv.width!==Math.round(r.width*dpr)||cv.height!==Math.round(r.height*dpr)){cv.width=Math.round(r.width*dpr);cv.height=Math.round(r.height*dpr)}
  const x=cv.getContext('2d');x.setTransform(dpr,0,0,dpr,0,0);x.clearRect(0,0,r.width,r.height);
  const gl=D.drawn.glyphs.map(g=>S.coords(g,vals)),total=gl.reduce((a,g)=>a+g.adv,0)||1,cap=D.metrics.cap;
  const s=Math.min(r.width*(o.left?.92:.9)/total,r.height*.62/cap),ox=o.left?r.width*.04:(r.width-total*s)/2,base=r.height/2+cap*s/2;
  if(o.line){x.strokeStyle=o.line;x.lineWidth=1;x.setLineDash([3,4]);[0,D.metrics.xheight,cap].forEach(v=>{x.beginPath();x.moveTo(0,base-v*s+.5);x.lineTo(r.width,base-v*s+.5);x.stroke()});x.setLineDash([])}
  let pen=ox;
  gl.forEach((q,gi)=>{const G=D.drawn.glyphs[gi],c=q.c,P=i=>[pen+c[2*i]*s,base-c[2*i+1]*s];x.beginPath();let st=0;
    G.ends.forEach(e=>{const idx=[];for(let i=st;i<=e;i++)idx.push(i);st=e+1;if(idx.length<2)return;
      const on=i=>G.flags[i]===1,mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
      let k0=idx.findIndex(on),start;const rot=k0<0?idx:idx.slice(k0).concat(idx.slice(0,k0));
      start=k0<0?mid(P(idx[idx.length-1]),P(idx[0])):P(rot[0]);x.moveTo(...start);
      const seq=k0<0?rot:rot.slice(1);let ctrl=null;
      seq.forEach(i=>{const p=P(i);if(on(i)){ctrl?x.quadraticCurveTo(...ctrl,...p):x.lineTo(...p);ctrl=null}else{if(ctrl){const m=mid(ctrl,p);x.quadraticCurveTo(...ctrl,...m)}ctrl=p}});
      ctrl?x.quadraticCurveTo(...ctrl,...start):x.lineTo(...start);x.closePath()});
    x.fillStyle=o.fill||'rgba(0,0,0,.06)';x.fill('nonzero');x.strokeStyle=o.ink||'#111';x.lineWidth=.9;x.stroke();
    if(o.dot!==false){const d=o.dotSize||2.2;for(let i=0;i<c.length/2;i++){const[px,py]=P(i);if(G.flags[i]){x.fillStyle=o.dot||'#ff48b0';x.fillRect(px-d/2,py-d/2,d,d)}else{x.strokeStyle=o.off||o.dot||'#ff48b0';x.lineWidth=1;x.beginPath();x.arc(px,py,d*.9,0,7);x.stroke()}}}
    pen+=q.adv*s})};

/* 2-D pad over up to two axes (x = first, y = second) */
S.pad=(el,state,tags,onChange)=>{const dot=el.querySelector('.dot');const[ta,tb]=tags,A=S.byTag[ta],B=tb&&S.byTag[tb];
  const show=()=>{const px=(state[ta]-A.min)/(A.max-A.min)*100,py=B?(state[tb]-B.min)/(B.max-B.min)*100:50;
    dot.style.left=px+'%';dot.style.top=py+'%';el.style.setProperty('--px',px+'%');el.style.setProperty('--py',py+'%');el.classList.toggle('lo',py<22);
    el.setAttribute('aria-valuetext',tags.map(t=>`${S.label(t)} ${Math.round(state[t])}`).join(', '));onChange(state)};
  const mv=e=>{const r=el.getBoundingClientRect();state[ta]=S.at(ta,(e.clientX-r.left)/r.width);if(B)state[tb]=S.at(tb,(e.clientY-r.top)/r.height);show()};
  const used=()=>el.classList.add('used');el.addEventListener('keydown',used);
  el.addEventListener('pointerdown',e=>{used();el.setPointerCapture(e.pointerId);mv(e)});el.addEventListener('pointermove',e=>{if(e.buttons)mv(e)});
  el.addEventListener('keydown',e=>{const st=(t,d)=>{const a=S.byTag[t];state[t]=S.clamp(state[t]+d*(a.max-a.min)/20,a.min,a.max)};
    const k={ArrowLeft:()=>st(ta,-1),ArrowRight:()=>st(ta,1),ArrowUp:()=>B&&st(tb,-1),ArrowDown:()=>B&&st(tb,1)}[e.key];if(k){e.preventDefault();k();show()}});
  show();return show};

/* seeded random */
S.rng=seed=>()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
S.pick=(r,a)=>a[Math.floor(r()*a.length)];
S.esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;');
window.S=S;
})();
