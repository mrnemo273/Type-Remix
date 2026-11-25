/* Grex Sans — Brief 03 heroes: the page opens on the name alone. Three versions, switchable via #hero-1/2/3. */
(function(){
const NAME='Grex Sans';
const css=`
.gx-hero{position:relative;min-height:min(100svh,1100px);display:flex;flex-direction:column;justify-content:space-between;padding:clamp(14px,2vw,28px) var(--gut,24px) 72px;overflow:hidden;background:var(--hero-bg,#fff);color:var(--hero-fg,#111)}
.gx-hero .meta{display:flex;justify-content:space-between;gap:12px 28px;flex-wrap:wrap;font-size:12px;letter-spacing:.07em;text-transform:uppercase;font-weight:600;position:relative;z-index:2;font-variation-settings:'GRAN' 0}
.gx-hero .meta a{color:inherit}
.gx-hero .name{width:max-content;white-space:nowrap;line-height:.78;letter-spacing:-.035em;font-weight:700;position:relative;z-index:1;margin:auto 0}
.gx-hero .name span{display:inline-block}
.gx-hero .facts{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;border-top:2px solid currentColor;padding-top:12px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:600;position:relative;z-index:2;font-variation-settings:'GRAN' 0}
.gx-hero .facts b{display:block;font-size:clamp(18px,1.8vw,30px);letter-spacing:0;text-transform:none}
.gx-hero .layer{position:absolute;width:max-content;left:0;top:0;mix-blend-mode:multiply;white-space:nowrap;line-height:.78;letter-spacing:-.035em;transition:transform .5s ease}
.gx-hero.h3 .stack{position:relative;margin:auto 0}
.gx-switch{position:fixed;right:16px;bottom:16px;z-index:60;display:flex;gap:4px;align-items:center;background:#111;color:#fff;border-radius:999px;padding:5px 6px 5px 14px;font:600 12px/1 'Grex Sans',system-ui,sans-serif;font-variation-settings:'GRAN' 0;box-shadow:0 4px 14px rgba(0,0,0,.25)}
.gx-switch button{font:inherit;border:0;border-radius:999px;background:transparent;color:#fff;width:30px;height:30px;cursor:pointer}
.gx-switch button[aria-pressed="true"]{background:#fff;color:#111}
@media (max-width:700px){.gx-hero .facts{grid-template-columns:repeat(2,minmax(0,1fr))}.gx-hero{min-height:auto;gap:28px}}
@media (prefers-reduced-motion:reduce){.gx-hero .layer{transition:none}}`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

const fvs=(el,w,g)=>{el.style.fontWeight=Math.round(w);el.style.fontVariationSettings=`'GRAN' ${Math.round(g)}`};
// size a single-line element so it spans its container exactly
function fit(el,box){el.style.fontSize='100px';const w=el.scrollWidth||1;el.style.fontSize=(100*box.clientWidth/w)+'px'}
const facts=`<div class="facts"><div>Weight<b>100–700</b></div><div>Grain<b>0–100</b></div><div>Characters<b>366</b></div><div>Licence<b>OFL</b></div></div>`;
const meta=(left)=>`<div class="meta"><span>${left}</span><span>Built on IBM Plex Sans</span><a href="#get">Get the font ↓</a></div>`;

const HEROES={
 1:{label:'Masthead',build(h){h.className='gx-hero h1';h.innerHTML=meta('Version 2.0 · Variable')+`<div class="name">${NAME}</div>`+facts;
    const n=h.querySelector('.name');fvs(n,700,100);return()=>fit(n,h.querySelector('.facts'))}},
 2:{label:'Clean to worn',build(h){h.className='gx-hero h2';h.innerHTML=meta('Thin & clean → Bold & worn')+`<div class="name">${[...NAME].map(c=>`<span>${c===' '?'&nbsp;':c}</span>`).join('')}</div>`+facts;
    const n=h.querySelector('.name'),sp=[...n.children],N=sp.length-1;let t0=performance.now(),raf;
    const paint=ph=>sp.forEach((s,i)=>{const u=Math.min(1,Math.max(0,i/N+ph));fvs(s,100+600*u,100*u)});
    const loop=now=>{const ph=Math.sin((now-t0)/2600)*.12;paint(ph);fit(n,h.querySelector('.facts'));raf=requestAnimationFrame(loop)};
    if(matchMedia('(prefers-reduced-motion: reduce)').matches)paint(0);else raf=requestAnimationFrame(loop);
    h._stop=()=>cancelAnimationFrame(raf);paint(0);return()=>fit(n,h.querySelector('.facts'))}},
 3:{label:'Misregistered',build(h){h.className='gx-hero h3';h.style.setProperty('--hero-bg','#fffdf8');
    const inks=[['#ff48b0',700,55],['#0078bf',700,100]];
    h.innerHTML=meta('Two passes, one name')+`<div class="stack"><div class="name" style="visibility:hidden">${NAME}</div>${inks.map(([c])=>`<div class="layer" style="color:${c}">${NAME}</div>`).join('')}</div>`+facts;
    const n=h.querySelector('.name'),L=[...h.querySelectorAll('.layer')];L.forEach((l,i)=>fvs(l,inks[i][1],inks[i][2]));fvs(n,700,100);
    const off=[[-.02,.016],[.012,-.01]];const place=(k=1)=>L.forEach((l,i)=>l.style.transform=`translate(${off[i][0]*k}em,${off[i][1]*k}em)`);place();
    h.addEventListener('pointermove',e=>{const r=h.getBoundingClientRect();const k=((e.clientX-r.left)/r.width-.5)*4;place(k)});h.addEventListener('pointerleave',()=>place());
    return()=>{fit(n,h.querySelector('.facts'));L.forEach(l=>l.style.fontSize=n.style.fontSize)}}},
};
window.GXHero=function(mount){
  const sw=document.createElement('div');sw.className='gx-switch';sw.setAttribute('role','group');sw.setAttribute('aria-label','Choose a hero');
  sw.innerHTML='<span>Hero</span>'+[1,2,3].map(i=>`<button data-h="${i}" aria-label="Hero ${i}: ${HEROES[i].label}" title="${HEROES[i].label}">${i}</button>`).join('');document.body.appendChild(sw);
  let refit=null;
  const show=k=>{if(mount._stop)mount._stop();mount._stop=null;mount.removeAttribute('style');refit=HEROES[k].build(mount);
    sw.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.h==k));document.fonts.ready.then(()=>refit&&refit())};
  const fromHash=()=>{const m=location.hash.match(/^#hero-([123])$/);return m?+m[1]:1};
  sw.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;location.hash='hero-'+b.dataset.h});
  addEventListener('hashchange',()=>{if(/^#hero-/.test(location.hash))show(fromHash())});
  addEventListener('resize',()=>refit&&refit());show(fromHash());
};
})();
