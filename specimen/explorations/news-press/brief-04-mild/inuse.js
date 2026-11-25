/* Specimen in-use library. Each example is a self-scaling mockup: sizes are in cqw
   (percent of the card's width), so every one scales cleanly from phone to wall. */
(function(){
const XT=()=>{const c=(S.cfg.inuse||{}).axis;if(c&&S.byTag[c])return c;const o=S.axes.find(a=>a.tag!=='wght');return o&&o.tag};
const XV=g=>{const xt=XT(),c=S.cfg.inuse||{},a=S.byTag[xt];const lo=c.min??a.min,hi=c.max??a.max;return lo+(hi-lo)*g/100};
const vals=(w,g)=>{const v={};if(S.byTag.wght)v.wght=S.clamp(w,S.byTag.wght.min,S.byTag.wght.max);const xt=XT();if(xt)v[xt]=XV(g);return v};
const T=(txt,o={})=>{const w=o.w??400,g=o.g??100,s=o.s??5;const st=[`font-weight:${w}`,`font-variation-settings:${S.fv(vals(w,g))}`,`font-size:${s}cqw`];
  if(o.c)st.push(`color:${o.c}`);if(o.lh)st.push(`line-height:${o.lh}`);if(o.ls)st.push(`letter-spacing:${o.ls}em`);if(o.up)st.push('text-transform:uppercase');
  if(o.ff)st.push(`font-feature-settings:${o.ff}`);if(o.x)st.push(o.x);return `<div style="${st.join(';')}">${txt}</div>`};
const box=(bg,c,inner,x='')=>`<div class="u" style="position:absolute;inset:0;background:${bg};color:${c};padding:7cqw;display:flex;flex-direction:column;${x}">${inner}</div>`;

const EX=[
{id:'coffee',name:'Coffee bag',head:[700,100],ratio:'3/4',html:()=>box('#c7d3bd','#1d2a1f',`
  ${T('Low Tide',{w:700,g:100,s:19,lh:.9,ls:-.02})}${T('Roasters · Est. 2019',{w:500,g:20,s:3.6,up:1,ls:.12,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;border-top:.5cqw solid currentColor;padding-top:4cqw">
  ${T('Washed<br>Guji, Ethiopia',{w:600,g:60,s:9,lh:1})}${T('Peach, black tea, wildflower honey',{w:400,g:25,s:4.2,x:'margin-top:3cqw'})}
  ${T('250 g &nbsp;·&nbsp; Roasted 14.11.26 &nbsp;·&nbsp; Filter',{w:500,g:0,s:3.2,up:1,ls:.06,x:'margin-top:5cqw'})}</div>`)},

{id:'gig',name:'Gig poster',head:[700,100],ratio:'3/4',html:()=>box('#ff48b0','#111',`
  ${T('Live at the Grange Hall',{w:500,g:40,s:4.4,up:1,ls:.1})}
  ${T('Thurs&shy;day<br>Static',{w:700,g:100,s:23,lh:.82,ls:-.03,x:'margin-top:4cqw'})}
  ${T('with Pale Harbour &amp; DJ Okonkwo',{w:400,g:60,s:5.2,x:'margin-top:5cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end">${T('21.11',{w:700,g:100,s:14,lh:.9})}${T('Doors 8pm<br>£12 adv',{w:600,g:30,s:4.4,x:'text-align:right'})}</div>`)},

{id:'book',name:'Book cover',head:[500,70],ratio:'2/3',html:()=>box('#0f3a2d','#efe9d8',`
  ${T('A novel',{w:400,g:20,s:4,up:1,ls:.16})}
  ${T('The Weather Inside',{w:500,g:70,s:15,lh:.95,ls:-.02,x:'margin-top:auto'})}
  <div style="height:.5cqw;background:currentColor;margin:6cqw 0 4cqw;width:30%"></div>${T('Inès Varga',{w:600,g:40,s:5.4})}`)},

{id:'record',name:'Record sleeve',head:[700,100],ratio:'1/1',html:()=>box('#ffe800','#111',`
  <div style="position:absolute;right:-30cqw;top:16cqw;width:74cqw;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#ffe800 0 9%,#111 9.5% 31%,#333 31.5% 32%,#111 32.5% 100%)"></div>
  <div style="position:relative">${T('Slow<br>Mach-<br>ines',{w:700,g:100,s:17,lh:.84,ls:-.03})}</div>
  <div style="margin-top:auto;position:relative">${T('Side A — Tidal Rooms',{w:600,g:40,s:4.6})}${T('LP · 33⅓ rpm · TR-014',{w:500,g:0,s:3.4,up:1,ls:.08,x:'margin-top:1.5cqw'})}</div>`)},

{id:'ticket',name:'Cinema ticket',head:[700,100],ratio:'5/2',html:()=>box('#f1ece1','#1a1a1a',`
  <div style="display:grid;grid-template-columns:1fr 26%;height:100%;gap:0">
   <div style="padding-right:4cqw;display:flex;flex-direction:column">${T('Ciné Lumière · Screen 2',{w:500,g:10,s:2.4,up:1,ls:.1})}
    ${T('Admit One',{w:700,g:100,s:10,lh:.9,x:'margin-top:2cqw'})}${T('Night Ferry (2026)',{w:500,g:50,s:3.6,x:'margin-top:1.5cqw'})}
    <div style="margin-top:auto;display:flex;gap:5cqw">${T('Row<br><b>F</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Seat<br><b>12</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Time<br><b>19:45</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Price<br><b>£9.50</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}</div></div>
   <div style="border-left:.5cqw dashed #1a1a1a55;padding-left:4cqw;display:flex;flex-direction:column;justify-content:space-between">${T('No.',{w:500,g:0,s:2.2,up:1})}${T('004213',{w:700,g:80,s:5,x:'writing-mode:vertical-rl;transform:rotate(180deg)'})}${T('F12',{w:700,g:60,s:4})}</div></div>`,'padding:5cqw')},

{id:'editorial',name:'Magazine spread',head:[600,80],ratio:'4/3',html:()=>box('#ffffff','#141414',`
  ${T('Field report · Issue 12',{w:600,g:0,s:2.2,up:1,ls:.12,c:'#e5007e'})}
  ${T('What the river leaves behind',{w:600,g:80,s:8.4,lh:.98,ls:-.02,x:'margin-top:2cqw;max-width:80%'})}
  <div style="columns:2;column-gap:4cqw;margin-top:4cqw">${T('Every spring the Shenandoah rises past the old mill and settles back a little higher than before. What it leaves is a line of silt along the brick, a few inches of new ground, and a record of the year that anyone who walks the towpath can read. The mill’s last owner kept a notebook of the marks, one line for every flood since 1962, in pencil that has worn as soft as the stone. Most years the line moves an inch. In 1985 it moved four feet, and the notebook has a single word beside it, underlined twice.',{w:400,g:10,s:2.55,lh:1.5,x:'text-align:left'})}</div>`)},

{id:'can',name:'Beer can label',head:[700,100],ratio:'3/4',html:()=>box('#0078bf','#fff',`
  ${T('Field<br>Notes',{w:700,g:100,s:20,lh:.85,ls:-.02})}
  ${T('Pale Ale',{w:500,g:60,s:8,x:'margin-top:3cqw'})}
  <div style="margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);border-top:.4cqw solid #fff;padding-top:3cqw;gap:2cqw">
   ${T('5.4%<br><span style="font-size:.5em">ABV</span>',{w:700,g:70,s:6,lh:1})}${T('440<br><span style="font-size:.5em">ML</span>',{w:700,g:70,s:6,lh:1})}${T('Citra<br><span style="font-size:.5em">HOPS</span>',{w:700,g:70,s:6,lh:1})}</div>
  ${T('Brewed &amp; canned at Kettle Yard, Frederick MD',{w:400,g:20,s:2.8,x:'margin-top:3cqw'})}`)},

{id:'sign',name:'Wayfinding',head:[700,60],ratio:'2/1',html:()=>box('#1c2130','#fff',`
  <div style="display:flex;align-items:center;gap:4cqw">${T('2',{w:700,g:60,s:22,lh:.8,x:'background:#ffd200;color:#1c2130;padding:1cqw 4cqw;border-radius:1.5cqw'})}${T('Platform 2 →',{w:700,g:60,s:9.5,lh:1})}</div>
  <div style="margin-top:auto;border-top:.3cqw solid #ffffff44;padding-top:3cqw;display:flex;justify-content:space-between;align-items:end;gap:3cqw">${T('Northbound<br><span style="opacity:.7">Fenwick · Ashdown · Coast Road</span>',{w:500,g:20,s:3.4,lh:1.3})}${T('↑ Exit',{w:600,g:40,s:4.4})}</div>`,'padding:5cqw')},

{id:'tee',name:'Screenprint',head:[700,100],ratio:'1/1',html:()=>box('#2b2b2b','#efe9dc',`
  <div style="margin:auto;text-align:center">${T('Made',{w:700,g:100,s:24,lh:.82,ls:-.03})}${T('to',{w:300,g:100,s:12,lh:1})}${T('Wear',{w:700,g:100,s:24,lh:.82,ls:-.03})}
  ${T(`${S.D.family} · Run of 50`,{w:500,g:30,s:3,up:1,ls:.14,x:'margin-top:5cqw'})}</div>`)},

{id:'card',name:'Business card',head:[600,50],ratio:'7/4',html:()=>box('#fbfaf6','#161616',`
  ${T('Mara Ellison',{w:600,g:50,s:8,lh:1})}${T('Letterpress &amp; bindery',{w:400,g:30,s:4,x:'margin-top:1.5cqw;color:#777'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end;gap:2cqw">${T('mara@inkandbone.studio<br>+1 202 555 0143',{w:400,g:0,s:3,lh:1.45})}${T('Ink<br>&amp;Bone',{w:700,g:100,s:7,lh:.85,x:'text-align:right'})}</div>`)},

{id:'menu',name:'Bakery menu board',head:[700,100],ratio:'3/4',html:()=>box('#1e1e1c','#f4efe4',`
  ${T('Today’s bread',{w:700,g:100,s:13,lh:.9,ls:-.02})}${T('Baked from 4am · out by noon',{w:400,g:30,s:3.6,x:'margin-top:2cqw;opacity:.7'})}
  <div style="margin-top:auto;display:grid;gap:2.6cqw">${[['Country loaf','7.50'],['Rye, caraway','8.00'],['Seeded bâtard','7.00'],['Focaccia, rosemary','6.50'],['Morning bun','4.25']].map(([a,b])=>`<div style="display:flex;justify-content:space-between;border-bottom:.3cqw dotted #f4efe455;padding-bottom:1.6cqw">${T(a,{w:500,g:40,s:5})}${T(b,{w:600,g:40,s:5,x:'font-variant-numeric:tabular-nums'})}</div>`).join('')}</div>`)},

{id:'stamp',name:'Shipping stamp',head:[700,100],ratio:'1/1',html:()=>box('#c49a6c','#2a1d10',`
  ${T('Ship to',{w:600,g:0,s:3,up:1,ls:.12})}${T('Ana Reyes<br>48 Calloway St, Apt 3<br>Baltimore, MD 21218',{w:400,g:20,s:4.4,lh:1.35,x:'margin-top:1.5cqw'})}
  <div style="margin:auto;transform:rotate(-9deg);border:1.6cqw solid #c8102e;color:#c8102e;padding:2cqw 4cqw;mix-blend-mode:multiply;text-align:center">${T('Fragile',{w:700,g:100,s:15,lh:.95,up:1})}${T('Handle with care · This side up ↑',{w:700,g:100,s:3.6,up:1,ls:.06})}</div>`)},

{id:'post',name:'Social post',head:[500,90],ratio:'1/1',html:()=>box('#ffe800','#111',`
  ${T('“',{w:700,g:100,s:30,lh:.6})}${T('Good type gets a little worn in.',{w:500,g:90,s:12,lh:1,ls:-.02,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between">${T('@'+S.D.slug.replace(/-/g,''),{w:600,g:20,s:4})}${T('01/12',{w:600,g:20,s:4})}</div>`)},

{id:'app',name:'Weather app',head:[700,100],ratio:'3/5',html:()=>box('linear-gradient(#e8eef2,#d4dee6)','#13202b',`
  ${T('Bethesda',{w:600,g:0,s:5.4})}${T('Wednesday 18 Nov',{w:400,g:0,s:3.8,x:'opacity:.6'})}
  ${T('Rain by 4pm.',{w:700,g:100,s:17,lh:.9,ls:-.02,x:'margin-top:10cqw'})}${T('Bring the good umbrella.',{w:400,g:40,s:5.4,x:'margin-top:3cqw'})}
  <div style="margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2cqw;background:#ffffff99;border-radius:4cqw;padding:4cqw">${[['Now','9°'],['1pm','10°'],['4pm','8°'],['7pm','6°']].map(([a,b])=>`<div style="text-align:center">${T(a,{w:500,g:0,s:3.6,x:'opacity:.6'})}${T(b,{w:600,g:0,s:6.4,x:'font-variant-numeric:tabular-nums'})}</div>`).join('')}</div>`)},

/* ---------- newspaper set ---------- */
{id:'front',name:'Front page',head:[800,100],ratio:'3/4',html:()=>box('#ece7da','#1b1b19',`
  ${T('The Evening Press',{w:700,g:60,s:9.5,lh:1,x:'text-align:center'})}
  <div style="border-top:.4cqw solid currentColor;border-bottom:.15cqw solid currentColor;margin:2cqw 0 4cqw;padding:1cqw 0;display:flex;justify-content:space-between">${T('Friday, November 20, 2026',{w:500,g:20,s:2.2,up:1,ls:.06})}${T('Late edition · $2.00',{w:500,g:20,s:2.2,up:1,ls:.06})}</div>
  ${T('Council votes to keep the old bridge',{w:800,g:100,s:9.6,lh:.98,ls:-.01})}
  ${T('Late-night session ends a decade of argument over the river crossing',{w:400,g:40,s:3.8,lh:1.2,x:'margin-top:3cqw'})}
  <div style="margin-top:4cqw;display:grid;grid-template-columns:repeat(3,1fr);gap:3cqw;border-top:.15cqw solid currentColor;padding-top:3cqw">${['After nine hours and three recesses, the council voted six to three on Thursday night to repair the Water Street bridge rather than replace it.','The decision keeps the 1911 iron span open to walkers and bikes, with traffic moved to the new crossing downstream by 2028.','Residents who packed the chamber stayed past midnight. Several had brought folding chairs; one brought soup for the clerks.'].map(t=>T(t,{w:400,g:30,s:2.25,lh:1.38})).join('')}</div>`)},

{id:'bill',name:'Newsstand bill',head:[800,100],ratio:'2/3',html:()=>box('#f6f3ea','#111',`
  <div style="background:#111;color:#f6f3ea;margin:-7cqw -7cqw 6cqw;padding:3cqw 7cqw">${T('Evening Press',{w:700,g:50,s:5,up:1,ls:.08})}</div>
  ${T('Bridge saved in late night vote',{w:800,g:100,s:15.5,lh:.9,up:1,ls:-.01})}
  ${T('Full story · page 3',{w:600,g:30,s:4,up:1,ls:.1,x:'margin-top:auto'})}`)},

{id:'crossword',name:'Crossword',head:[700,80],ratio:'1/1',html:()=>{const G=['...#...','.#.#.#.','.......','##.#.##','.......','.#.#.#.','...#...'];let n=0,cells='';
  G.forEach((row,y)=>[...row].forEach((c,x)=>{const blk=c==='#',isA=!blk&&(x===0||G[y][x-1]==='#')&&x<6&&G[y][x+1]!=='#',isD=!blk&&(y===0||G[y-1][x]==='#')&&y<6&&G[y+1][x]!=='#';const num=(isA||isD)?++n:'';
    cells+=`<div style="background:${blk?'#1b1b19':'#fff'};position:relative">${num?`<span style="position:absolute;left:.6cqw;top:.2cqw">${T(num,{w:500,g:0,s:1.9})}</span>`:''}</div>`}));
  return box('#ece7da','#1b1b19',`${T('The Daily Crossword · No. 4,812',{w:700,g:80,s:4.4})}
  <div style="display:grid;grid-template-columns:48% 1fr;gap:4cqw;margin-top:4cqw;align-items:start">
   <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:.3cqw;background:#1b1b19;padding:.3cqw;aspect-ratio:1">${cells}</div>
   <div>${T('Across',{w:700,g:60,s:2.8,up:1,ls:.08})}${['1 Morning paper (5)','4 Hot off the ___ (5)','7 Ink holder (4)','9 Big story (5)'].map(t=>T(t,{w:400,g:20,s:2.6,lh:1.5})).join('')}
   ${T('Down',{w:700,g:60,s:2.8,up:1,ls:.08,x:'margin-top:2cqw'})}${['1 Front-page line (8)','2 Run again (7)','3 Column item (4)'].map(t=>T(t,{w:400,g:20,s:2.6,lh:1.5})).join('')}</div></div>
  ${T('Solution in tomorrow’s paper',{w:400,g:20,s:2.4,x:'margin-top:auto;opacity:.7'})}`)}},

{id:'scores',name:'Sports results',head:[800,100],ratio:'3/4',html:()=>box('#ece7da','#1b1b19',`
  ${T('Sport',{w:700,g:40,s:3.2,up:1,ls:.12})}${T('Harbor City take the derby',{w:800,g:100,s:10.5,lh:.95,x:'margin-top:2cqw'})}
  <div style="margin-top:auto">${T('Saturday’s results',{w:700,g:50,s:3,up:1,ls:.08,x:'border-bottom:.3cqw solid currentColor;padding-bottom:1.5cqw'})}
  ${[['Harbor City','3','1','Millbrook'],['Fenwick Athletic','0','0','Coast Road'],['Ashdown','2','4','St Ives Town'],['Kettle Yard','1','2','Old Quay']].map(([a,x,y,b])=>`<div style="display:grid;grid-template-columns:1fr 6cqw 3cqw 6cqw 1fr;align-items:baseline;border-bottom:.12cqw solid #1b1b1955;padding:1.6cqw 0">${T(a,{w:500,g:20,s:3.4})}${T(x,{w:700,g:60,s:4.4,x:'text-align:right;font-variant-numeric:tabular-nums'})}${T('–',{w:400,g:0,s:3.4,x:'text-align:center'})}${T(y,{w:700,g:60,s:4.4,x:'font-variant-numeric:tabular-nums'})}${T(b,{w:500,g:20,s:3.4,x:'text-align:right'})}</div>`).join('')}</div>`)},

{id:'markets',name:'Market report',head:[700,70],ratio:'4/3',html:()=>box('#f1ead6','#1b1b19',`
  <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:.4cqw solid currentColor;padding-bottom:1.5cqw">${T('Markets',{w:700,g:70,s:8})}${T('Close, Thursday',{w:500,g:20,s:2.6,up:1,ls:.08})}</div>
  ${[['Harbor 100','8,214.6','+0.6%'],['Coast Tech','1,902.3','−1.2%'],['Gold, oz','2,412.0','+0.3%'],['Crude, bbl','71.84','−0.9%'],['Dollar / euro','1.084','+0.1%']].map(([a,b,c])=>`<div style="display:grid;grid-template-columns:1fr auto 14cqw;gap:3cqw;align-items:baseline;border-bottom:.12cqw solid #1b1b1955;padding:1.4cqw 0">${T(a,{w:500,g:20,s:3.2})}${T(b,{w:600,g:30,s:3.4,x:'font-variant-numeric:tabular-nums;text-align:right'})}${T(c,{w:700,g:40,s:3.2,x:'font-variant-numeric:tabular-nums;text-align:right;color:'+(c[0]==='+'?'#1b1b19':'#b0172a')})}</div>`).join('')}`)},

{id:'listings',name:'TV & radio listings',head:[800,90],ratio:'3/4',html:()=>box('#ece7da','#1b1b19',`
  ${T('Tonight',{w:800,g:90,s:13,lh:.9})}${T('Channel 4 · Harbor FM',{w:500,g:20,s:2.8,up:1,ls:.08,x:'margin-top:2cqw'})}
  <div style="margin-top:4cqw;border-top:.3cqw solid currentColor">${[['6.00','Local News'],['6.30','The Garden Hour','Repotting before the frost'],['7.00','Quiz Night'],['8.00','Film: Night Ferry','A crossing in fog, a stranger with a ticket'],['10.00','Late Edition'],['11.30','Shipping Forecast']].map(([a,b,c])=>`<div style="display:grid;grid-template-columns:11cqw 1fr;gap:2cqw;padding:1.5cqw 0;border-bottom:.12cqw solid #1b1b1955">${T(a,{w:700,g:50,s:3.2,x:'font-variant-numeric:tabular-nums'})}<div>${T(b,{w:600,g:40,s:3.4})}${c?T(c,{w:400,g:10,s:2.6,x:'opacity:.75;margin-top:.5cqw'}):''}</div></div>`).join('')}</div>`)},

{id:'review',name:'Theatre review',head:[700,80],ratio:'1/1',html:()=>box('#f6f3ea','#1b1b19',`
  ${T('Theatre',{w:700,g:40,s:3.2,up:1,ls:.14,c:'#b0172a'})}
  ${T('A play that earns its silences',{w:700,g:80,s:9.5,lh:1,x:'margin-top:3cqw'})}
  ${T('★★★★☆',{w:400,g:0,s:6,ls:.1,x:'margin-top:3cqw'})}
  ${T('“The Lamplighter” at the Grange · until 12 December',{w:500,g:20,s:3,x:'margin-top:2cqw;opacity:.75'})}
  ${T('For long stretches nobody speaks, and the room leans in. It is the most confident ninety minutes on a local stage this year.',{w:400,g:30,s:3.4,lh:1.4,x:'margin-top:auto'})}`)},

{id:'classifieds',name:'Classifieds',head:[800,100],ratio:'3/4',html:()=>box('#ece7da','#1b1b19',`
  ${T('Classifieds',{w:800,g:100,s:10,lh:1,x:'border-bottom:.4cqw solid currentColor;padding-bottom:2cqw'})}
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:2.5cqw;margin-top:3cqw">${[['For sale','Upright piano, needs tuning. Free to a good home if you can carry it. 555-0148.'],['Lost','Grey cat, answers to Pepper, last seen near the bakery on Elm. Reward.'],['Wanted','Old letterpress type, wood or metal, any condition. Fair prices. Ask for Mara.'],['To let','Room above the hardware store, bright, quiet, bike storage. $640 a month.'],['Services','Clocks and watches repaired. Thirty years at the same bench.'],['Notice','The Thursday chess club has moved to the library, room 2.']].map(([a,b])=>`<div style="border:.15cqw solid #1b1b19;padding:2cqw">${T(a,{w:800,g:80,s:2.8,up:1,ls:.06})}${T(b,{w:400,g:30,s:2.5,lh:1.35,x:'margin-top:1cqw'})}</div>`).join('')}</div>`)},

{id:'letters',name:'Letters page',head:[800,100],ratio:'3/4',html:()=>box('#f6f3ea','#1b1b19',`
  ${T('Letters',{w:800,g:100,s:15,lh:.9})}${T('Write to letters@eveningpress.example',{w:500,g:10,s:2.6,x:'margin-top:2cqw;opacity:.7'})}
  ${T('Keep the bridge, and the benches',{w:700,g:70,s:5.6,lh:1.05,x:'margin-top:6cqw'})}
  ${T('Sir — I am glad the council has saved the old bridge. May I ask that they also keep the two benches at the east end? My father proposed to my mother on the left one in 1958, and I would like to sit there a while longer.',{w:400,g:30,s:3.3,lh:1.45,x:'margin-top:3cqw'})}
  ${T('R. Okafor, Silver Spring',{w:600,g:40,s:3.2,x:'margin-top:auto;text-align:right'})}`)},

{id:'forecast',name:'Weather box',head:[800,100],ratio:'4/3',html:()=>box('#ece7da','#1b1b19',`
  <div style="display:flex;justify-content:space-between;align-items:baseline">${T('Weather',{w:800,g:100,s:9})}${T('Sunrise 6.58 · Sunset 4.51',{w:500,g:20,s:2.6,up:1,ls:.06})}</div>
  ${T('Grey and mild, rain by evening. Bring the good umbrella.',{w:400,g:30,s:3.6,lh:1.3,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;display:grid;grid-template-columns:repeat(5,1fr);border-top:.4cqw solid currentColor">${[['Fri','9°','Rain'],['Sat','7°','Cloud'],['Sun','11°','Sun'],['Mon','10°','Wind'],['Tue','6°','Frost']].map(([a,b,c])=>`<div style="padding:2cqw 1cqw;border-right:.12cqw solid #1b1b1955">${T(a,{w:700,g:50,s:3,up:1})}${T(b,{w:800,g:90,s:8,x:'font-variant-numeric:tabular-nums'})}${T(c,{w:400,g:20,s:2.6})}</div>`).join('')}</div>`)},

{id:'tote',name:'Masthead tote',head:[700,100],ratio:'1/1',html:()=>box('#e4d7bd','#1b1b19',`
  <div style="position:absolute;left:30%;right:30%;top:-2cqw;height:24cqw;border:2.4cqw solid #cdbd9d;border-bottom:0;border-radius:14cqw 14cqw 0 0"></div>
  <div style="margin:auto 0;text-align:center">${T('The Evening Press',{w:700,g:100,s:10.5,lh:1})}<div style="height:.4cqw;background:currentColor;margin:3cqw auto;width:40%"></div>${T('Est. 1911 · All the news that fits',{w:500,g:40,s:3.2,up:1,ls:.1})}</div>`)},

{id:'subscribe',name:'Subscription ad',head:[800,100],ratio:'3/2',html:()=>box('#f6f3ea','#1b1b19',`
  <div style="border:.5cqw dashed #1b1b19;position:absolute;inset:4cqw;padding:5cqw;display:flex;flex-direction:column">
  ${T('On your step<br>by 6 a.m.',{w:800,g:100,s:8,lh:.95})}
  ${T('Seven days of the Evening Press, delivered by hand.',{w:400,g:30,s:3.6,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end">${T('$4 a week',{w:800,g:90,s:8})}${T('Clip and post to<br>14 Water Street',{w:500,g:20,s:2.8,x:'text-align:right'})}</div></div>`)},

/* ---------- handmade set ---------- */
{id:'seeds',name:'Seed packet',head:[700,80],ratio:'2/3',html:()=>box('#f3e3c3','#3b2a14',`
  ${T('Kitchen Garden Seed Co.',{w:600,g:30,s:3.4,up:1,ls:.1})}
  <div style="margin:5cqw -7cqw;height:46cqw;background:radial-gradient(circle at 35% 45%,#f2a33a 0 14%,transparent 15%),radial-gradient(circle at 62% 58%,#f2a33a 0 12%,transparent 13%),radial-gradient(circle at 48% 30%,#e8902a 0 9%,transparent 10%),#7c9a4e"></div>
  ${T('Sungold Tomatoes',{w:700,g:80,s:11,lh:.95})}
  ${T('Sow indoors March to April · 60 days · 1.2 g',{w:500,g:20,s:3.4,x:'margin-top:auto'})}`)},

{id:'jam',name:'Jam jar label',head:[700,80],ratio:'1/1',html:()=>box('#7a2338','#f4e6d6',`
  <div style="margin:auto;width:78cqw;aspect-ratio:1;border-radius:50%;background:#f4e6d6;color:#5a1a2a;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-shadow:inset 0 0 0 1.2cqw #f4e6d6,inset 0 0 0 1.6cqw #5a1a2a">
  ${T('Blackberry<br>&amp; Bay',{w:700,g:80,s:10,lh:.95})}${T('Batch 14 · Summer 2026',{w:500,g:20,s:3.2,up:1,ls:.08,x:'margin-top:3cqw'})}${T('Picked on the towpath',{w:400,g:40,s:3.4,x:'margin-top:1.5cqw'})}</div>`)},

{id:'studio',name:'Studio sign',head:[700,80],ratio:'3/2',html:()=>box('#2f3a33','#f1ece1',`
  ${T('Wheel &amp; Kiln',{w:600,g:30,s:4,up:1,ls:.12})}
  ${T('Open studio<br>Saturdays 10–4',{w:700,g:80,s:9,lh:1,x:'margin-top:auto;white-space:nowrap'})}
  ${T('Throwing, glazing, firing · bring an apron',{w:400,g:30,s:3.6,x:'margin-top:3cqw'})}`)},

{id:'marker',name:'Plant marker',head:[700,80],ratio:'3/4',html:()=>box('#a7c08a','#24301b',`
  <div style="margin:auto;width:42cqw;height:84cqw;background:#f5efe0;clip-path:polygon(0 0,100% 0,100% 82%,50% 100%,0 82%);padding:6cqw 4cqw;display:flex;flex-direction:column;text-align:center">
  ${T('Thai Basil',{w:700,g:80,s:7.4,lh:.95})}<div style="height:.4cqw;background:currentColor;margin:3cqw 20%"></div>${T('Full sun<br>Water daily<br>Pinch the flowers',{w:400,g:30,s:3.4,lh:1.4})}${T('Sown 3 May',{w:600,g:40,s:3,x:'margin-top:auto;margin-bottom:12cqw'})}</div>`)},

{id:'zine',name:'Zine cover',head:[800,80],ratio:'3/4',html:()=>box('#f2f0ea','#151515',`
  ${T('No. 3 · $3',{w:600,g:40,s:4})}
  ${T('Fix It Your&shy;self',{w:800,g:80,s:20,lh:.85,ls:-.02,x:'margin-top:4cqw'})}
  <div style="margin-top:auto;border-top:.6cqw solid currentColor;padding-top:3cqw;display:flex;justify-content:space-between">${T('Bikes · chairs · radios · zips',{w:500,g:30,s:3.6})}${T('24 pp',{w:500,g:30,s:3.6})}</div>`)},

{id:'pricecard',name:'Market price card',head:[700,80],ratio:'4/3',html:()=>box('#1f1f1d','#f2efe6',`
  ${T('Heirloom carrots',{w:700,g:80,s:10,lh:.95})}${T('Purple, white &amp; orange · from Fallow Farm',{w:400,g:30,s:3.6,x:'margin-top:2cqw;opacity:.85'})}
  <div style="margin-top:auto;display:flex;align-items:baseline;gap:3cqw">${T('3 bunches',{w:600,g:40,s:5})}${T('$5',{w:800,g:80,s:20,lh:.8})}</div>`)},

{id:'repairtag',name:'Repair ticket',head:[700,80],ratio:'2/3',html:()=>box('#e9dcc0','#2b2418',`
  <div style="width:8cqw;aspect-ratio:1;border-radius:50%;background:#f7f4ee;box-shadow:inset 0 0 0 .8cqw #b9a77f;margin:0 auto 5cqw"></div>
  ${T('Repair ticket',{w:700,g:80,s:9,lh:.95,x:'text-align:center'})}${T('No. 0214',{w:600,g:30,s:4,x:'text-align:center;margin-top:1cqw'})}
  <div style="margin-top:6cqw">${[['Name','Jo Park'],['Bike','Blue 3-speed'],['Work','True wheel, new chain'],['Ready','Tuesday']].map(([a,b])=>`<div style="display:flex;gap:3cqw;border-bottom:.15cqw solid #2b241866;padding:1.8cqw 0">${T(a,{w:700,g:40,s:2.8,up:1,ls:.08,x:'width:14cqw'})}${T(b,{w:400,g:60,s:3.8})}</div>`).join('')}</div>`)},

{id:'workshop',name:'Workshop poster',head:[800,80],ratio:'3/4',html:()=>box('#e85d2a','#1e120c',`
  ${T('Community tool library',{w:600,g:30,s:3.6,up:1,ls:.1})}
  ${T('Learn to sharpen your knives',{w:800,g:80,s:14,lh:.88,ls:-.02,x:'margin-top:5cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end">${T('Thursdays<br>in November',{w:700,g:60,s:5.6,lh:1})}${T('6.30 pm<br>Free',{w:600,g:30,s:4,x:'text-align:right'})}</div>`)},

{id:'notebook',name:'Notebook cover',head:[700,80],ratio:'3/4',html:()=>box('#b48a5a','#2a1b0e',`
  <div style="position:absolute;left:0;top:0;bottom:0;width:6cqw;background:#2a1b0e22"></div>
  ${T('Field<br>Notebook',{w:700,g:80,s:13,lh:.92,x:'margin-top:8cqw'})}
  <div style="margin-top:auto;border:.3cqw solid currentColor;padding:3cqw">${T('Name',{w:600,g:30,s:2.8,up:1,ls:.1})}<div style="border-bottom:.2cqw solid currentColor;height:6cqw"></div>${T('48 pages · dot grid',{w:400,g:30,s:3.2,x:'margin-top:2cqw'})}</div>`)},

{id:'carelabel',name:'Care label',head:[700,80],ratio:'2/3',html:()=>box('#d9d4c7','#26231d',`
  <div style="margin:auto;width:60cqw;background:#f7f3ea;padding:7cqw 5cqw;text-align:center;box-shadow:0 1cqw 0 #bfb8a6">
  ${T('Made by hand<br>in Asheville',{w:700,g:80,s:6.4,lh:1})}<div style="height:.3cqw;background:currentColor;margin:4cqw 25%"></div>
  ${T('100% wool<br>Cold wash<br>Dry flat<br>Darn, don’t bin',{w:400,g:40,s:3.6,lh:1.5})}</div>`)},

{id:'cider',name:'Cider label',head:[800,80],ratio:'3/4',html:()=>box('#1d3b2a','#efe3c6',`
  <div style="margin:auto 0;border:.5cqw solid currentColor;padding:7cqw 5cqw;text-align:center">
  ${T('Long Meadow',{w:600,g:30,s:4,up:1,ls:.14})}${T('Orchard<br>Dry',{w:800,g:80,s:16,lh:.88,x:'margin-top:3cqw'})}
  ${T('Pressed from windfalls · 6.2% · 500 ml',{w:500,g:30,s:3,x:'margin-top:4cqw'})}</div>`)},

{id:'window',name:'Shop window',head:[700,80],ratio:'3/2',html:()=>box('linear-gradient(160deg,#28343a,#141b1f)','#e9c46a',`
  ${T('Hardware &amp; Supply',{w:700,g:80,s:11,lh:.95,x:'text-align:center;margin-top:6cqw'})}
  <div style="height:.4cqw;background:currentColor;margin:4cqw 30%"></div>
  ${T('Keys cut while you wait · Paint mixed · Est. 1962',{w:500,g:40,s:3.8,x:'text-align:center'})}
  ${T('Open',{w:700,g:60,s:4.4,up:1,ls:.2,x:'margin-top:auto;align-self:center;border:.4cqw solid currentColor;padding:1cqw 4cqw'})}`)},
];
const WN={100:'Thin',200:'ExtraLight',300:'Light',400:'Regular',500:'Medium',600:'SemiBold',700:'Bold',800:'ExtraBold',900:'Black'};
const settings=ex=>{const[w,g]=ex.head;const parts=[];if(S.byTag.wght)parts.push(WN[Math.round(S.clamp(w,S.byTag.wght.min,S.byTag.wght.max)/100)*100]||w);
  const xt=XT();if(xt)parts.push(`${S.label(xt).toLowerCase()} ${Math.round(XV(g))}`);return parts.length?'Headline at '+parts.join(', '):''};
const DEFAULT=['coffee','gig','book','record','ticket','editorial','can','sign','tee','card','menu','stamp','post','app'];
window.specInuseList=()=>(((S.cfg||{}).inuse||{}).cards||DEFAULT).map(id=>EX.find(e=>e.id===id)).filter(Boolean);
window.specUse=ex=>{const d=document.createElement('figure');d.dataset.id=ex.id;
  d.innerHTML=`<div class="frame" style="container-type:inline-size;position:relative;aspect-ratio:${ex.ratio};overflow:hidden">${ex.html()}</div><figcaption><b>${ex.name}</b><span>${settings(ex)}</span></figcaption>`;return d};
})();
