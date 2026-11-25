/* Grex Sans — in-use library. Each example is a self-scaling mockup: sizes are in cqw
   (percent of the card's width), so every one scales cleanly from phone to wall. */
(function(){
const T=(txt,o={})=>{const w=o.w??400,g=o.g??100,s=o.s??5;const st=[`font-weight:${w}`,`font-variation-settings:'GRAN' ${g}`,`font-size:${s}cqw`];
  if(o.c)st.push(`color:${o.c}`);if(o.lh)st.push(`line-height:${o.lh}`);if(o.ls)st.push(`letter-spacing:${o.ls}em`);if(o.up)st.push('text-transform:uppercase');
  if(o.ff)st.push(`font-feature-settings:${o.ff}`);if(o.x)st.push(o.x);return `<div style="${st.join(';')}">${txt}</div>`};
const box=(bg,c,inner,x='')=>`<div class="u" style="position:absolute;inset:0;background:${bg};color:${c};padding:7cqw;display:flex;flex-direction:column;${x}">${inner}</div>`;

const EX=[
{id:'coffee',name:'Coffee bag',note:'Headline at Bold, grain 100; origin notes at grain 30',ratio:'3/4',html:()=>box('#c7d3bd','#1d2a1f',`
  ${T('Low Tide',{w:700,g:100,s:19,lh:.9,ls:-.02})}${T('Roasters · Est. 2019',{w:500,g:20,s:3.6,up:1,ls:.12,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;border-top:.5cqw solid currentColor;padding-top:4cqw">
  ${T('Washed<br>Guji, Ethiopia',{w:600,g:60,s:9,lh:1})}${T('Peach, black tea, wildflower honey',{w:400,g:25,s:4.2,x:'margin-top:3cqw'})}
  ${T('250 g &nbsp;·&nbsp; Roasted 14.11.26 &nbsp;·&nbsp; Filter',{w:500,g:0,s:3.2,up:1,ls:.06,x:'margin-top:5cqw'})}</div>`)},

{id:'gig',name:'Gig poster',note:'Black on fluoro pink, grain 100 at three weights',ratio:'3/4',html:()=>box('#ff48b0','#111',`
  ${T('Live at the Grange Hall',{w:500,g:40,s:4.4,up:1,ls:.1})}
  ${T('Thurs&shy;day<br>Static',{w:700,g:100,s:23,lh:.82,ls:-.03,x:'margin-top:4cqw'})}
  ${T('with Pale Harbour &amp; DJ Okonkwo',{w:400,g:60,s:5.2,x:'margin-top:5cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end">${T('21.11',{w:700,g:100,s:14,lh:.9})}${T('Doors 8pm<br>£12 adv',{w:600,g:30,s:4.4,x:'text-align:right'})}</div>`)},

{id:'book',name:'Book cover',note:'Medium at grain 70 on deep green',ratio:'2/3',html:()=>box('#0f3a2d','#efe9d8',`
  ${T('A novel',{w:400,g:20,s:4,up:1,ls:.16})}
  ${T('The Weather Inside',{w:500,g:70,s:15,lh:.95,ls:-.02,x:'margin-top:auto'})}
  <div style="height:.5cqw;background:currentColor;margin:6cqw 0 4cqw;width:30%"></div>${T('Inès Varga',{w:600,g:40,s:5.4})}`)},

{id:'record',name:'Record sleeve',note:'Bold, grain 100, set tight over a yellow sleeve',ratio:'1/1',html:()=>box('#ffe800','#111',`
  <div style="position:absolute;right:-30cqw;top:16cqw;width:74cqw;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#ffe800 0 9%,#111 9.5% 31%,#333 31.5% 32%,#111 32.5% 100%)"></div>
  <div style="position:relative">${T('Slow<br>Mach-<br>ines',{w:700,g:100,s:17,lh:.84,ls:-.03})}</div>
  <div style="margin-top:auto;position:relative">${T('Side A — Tidal Rooms',{w:600,g:40,s:4.6})}${T('LP · 33⅓ rpm · TR-014',{w:500,g:0,s:3.4,up:1,ls:.08,x:'margin-top:1.5cqw'})}</div>`)},

{id:'ticket',name:'Cinema ticket',note:'Tabular figures at grain 20; the title at 100',ratio:'5/2',html:()=>box('#f1ece1','#1a1a1a',`
  <div style="display:grid;grid-template-columns:1fr 26%;height:100%;gap:0">
   <div style="padding-right:4cqw;display:flex;flex-direction:column">${T('Ciné Lumière · Screen 2',{w:500,g:10,s:2.4,up:1,ls:.1})}
    ${T('Admit One',{w:700,g:100,s:10,lh:.9,x:'margin-top:2cqw'})}${T('Night Ferry (2026)',{w:500,g:50,s:3.6,x:'margin-top:1.5cqw'})}
    <div style="margin-top:auto;display:flex;gap:5cqw">${T('Row<br><b>F</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Seat<br><b>12</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Time<br><b>19:45</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}${T('Price<br><b>£9.50</b>',{w:500,g:20,s:2.6,up:1,lh:1.1})}</div></div>
   <div style="border-left:.5cqw dashed #1a1a1a55;padding-left:4cqw;display:flex;flex-direction:column;justify-content:space-between">${T('No.',{w:500,g:0,s:2.2,up:1})}${T('004213',{w:700,g:80,s:5,x:'writing-mode:vertical-rl;transform:rotate(180deg)'})}${T('F12',{w:700,g:60,s:4})}</div></div>`,'padding:5cqw')},

{id:'editorial',name:'Magazine spread',note:'Headline at grain 80, body at grain 10: the texture holds at text size',ratio:'4/3',html:()=>box('#ffffff','#141414',`
  ${T('Field report · Issue 12',{w:600,g:0,s:2.2,up:1,ls:.12,c:'#e5007e'})}
  ${T('What the river leaves behind',{w:600,g:80,s:8.4,lh:.98,ls:-.02,x:'margin-top:2cqw;max-width:80%'})}
  <div style="columns:2;column-gap:4cqw;margin-top:4cqw">${T('Every spring the Shenandoah rises past the old mill and settles back a little higher than before. What it leaves is a line of silt along the brick, a few inches of new ground, and a record of the year that anyone who walks the towpath can read. The mill’s last owner kept a notebook of the marks, one line for every flood since 1962, in pencil that has worn as soft as the stone. Most years the line moves an inch. In 1985 it moved four feet, and the notebook has a single word beside it, underlined twice.',{w:400,g:10,s:2.55,lh:1.5,x:'text-align:left'})}</div>`)},

{id:'can',name:'Beer can label',note:'Reversed out of riso blue, Bold at grain 100',ratio:'3/4',html:()=>box('#0078bf','#fff',`
  ${T('Field<br>Notes',{w:700,g:100,s:20,lh:.85,ls:-.02})}
  ${T('Pale Ale',{w:500,g:60,s:8,x:'margin-top:3cqw'})}
  <div style="margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);border-top:.4cqw solid #fff;padding-top:3cqw;gap:2cqw">
   ${T('5.4%<br><span style="font-size:.5em">ABV</span>',{w:700,g:70,s:6,lh:1})}${T('440<br><span style="font-size:.5em">ML</span>',{w:700,g:70,s:6,lh:1})}${T('Citra<br><span style="font-size:.5em">HOPS</span>',{w:700,g:70,s:6,lh:1})}</div>
  ${T('Brewed &amp; canned at Kettle Yard, Frederick MD',{w:400,g:20,s:2.8,x:'margin-top:3cqw'})}`)},

{id:'sign',name:'Wayfinding',note:'Platform sign; arrows are the font’s own glyphs',ratio:'2/1',html:()=>box('#1c2130','#fff',`
  <div style="display:flex;align-items:center;gap:4cqw">${T('2',{w:700,g:60,s:22,lh:.8,x:'background:#ffd200;color:#1c2130;padding:1cqw 4cqw;border-radius:1.5cqw'})}${T('Platform 2 →',{w:700,g:60,s:9.5,lh:1})}</div>
  <div style="margin-top:auto;border-top:.3cqw solid #ffffff44;padding-top:3cqw;display:flex;justify-content:space-between;align-items:end;gap:3cqw">${T('Northbound<br><span style="opacity:.7">Fenwick · Ashdown · Coast Road</span>',{w:500,g:20,s:3.4,lh:1.3})}${T('↑ Exit',{w:600,g:40,s:4.4})}</div>`,'padding:5cqw')},

{id:'tee',name:'Screenprint',note:'Off-white on charcoal; the grain reads as ink on cotton',ratio:'1/1',html:()=>box('#2b2b2b','#efe9dc',`
  <div style="margin:auto;text-align:center">${T('Made',{w:700,g:100,s:24,lh:.82,ls:-.03})}${T('to',{w:300,g:100,s:12,lh:1})}${T('Wear',{w:700,g:100,s:24,lh:.82,ls:-.03})}
  ${T('Grex Sans · Run of 50',{w:500,g:30,s:3,up:1,ls:.14,x:'margin-top:5cqw'})}</div>`)},

{id:'card',name:'Business card',note:'Name at grain 50, details clean',ratio:'7/4',html:()=>box('#fbfaf6','#161616',`
  ${T('Mara Ellison',{w:600,g:50,s:8,lh:1})}${T('Letterpress &amp; bindery',{w:400,g:30,s:4,x:'margin-top:1.5cqw;color:#777'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:end;gap:2cqw">${T('mara@inkandbone.studio<br>+1 202 555 0143',{w:400,g:0,s:3,lh:1.45})}${T('Ink<br>&amp;Bone',{w:700,g:100,s:7,lh:.85,x:'text-align:right'})}</div>`)},

{id:'menu',name:'Bakery menu board',note:'Prices in tabular figures; headline at grain 100',ratio:'3/4',html:()=>box('#1e1e1c','#f4efe4',`
  ${T('Today’s bread',{w:700,g:100,s:13,lh:.9,ls:-.02})}${T('Baked from 4am · out by noon',{w:400,g:30,s:3.6,x:'margin-top:2cqw;opacity:.7'})}
  <div style="margin-top:auto;display:grid;gap:2.6cqw">${[['Country loaf','7.50'],['Rye, caraway','8.00'],['Seeded bâtard','7.00'],['Focaccia, rosemary','6.50'],['Morning bun','4.25']].map(([a,b])=>`<div style="display:flex;justify-content:space-between;border-bottom:.3cqw dotted #f4efe455;padding-bottom:1.6cqw">${T(a,{w:500,g:40,s:5})}${T(b,{w:600,g:40,s:5,x:'font-variant-numeric:tabular-nums'})}</div>`).join('')}</div>`)},

{id:'stamp',name:'Shipping stamp',note:'Rubber-stamp red on kraft: grain at its most physical',ratio:'1/1',html:()=>box('#c49a6c','#2a1d10',`
  ${T('Ship to',{w:600,g:0,s:3,up:1,ls:.12})}${T('Ana Reyes<br>48 Calloway St, Apt 3<br>Baltimore, MD 21218',{w:400,g:20,s:4.4,lh:1.35,x:'margin-top:1.5cqw'})}
  <div style="margin:auto;transform:rotate(-9deg);border:1.6cqw solid #c8102e;color:#c8102e;padding:2cqw 4cqw;mix-blend-mode:multiply;text-align:center">${T('Fragile',{w:700,g:100,s:15,lh:.95,up:1})}${T('Handle with care · This side up ↑',{w:700,g:100,s:3.6,up:1,ls:.06})}</div>`)},

{id:'post',name:'Social post',note:'Square quote card, Medium at grain 90',ratio:'1/1',html:()=>box('#ffe800','#111',`
  ${T('“',{w:700,g:100,s:30,lh:.6})}${T('Good type gets a little worn in.',{w:500,g:90,s:12,lh:1,ls:-.02,x:'margin-top:2cqw'})}
  <div style="margin-top:auto;display:flex;justify-content:space-between">${T('@grexsans',{w:600,g:20,s:4})}${T('01/12',{w:600,g:20,s:4})}</div>`)},

{id:'app',name:'Weather app',note:'Grain on the headline only; the interface stays at grain 0',ratio:'3/5',html:()=>box('linear-gradient(#e8eef2,#d4dee6)','#13202b',`
  ${T('Bethesda',{w:600,g:0,s:5.4})}${T('Wednesday 18 Nov',{w:400,g:0,s:3.8,x:'opacity:.6'})}
  ${T('Rain by 4pm.',{w:700,g:100,s:17,lh:.9,ls:-.02,x:'margin-top:10cqw'})}${T('Bring the good umbrella.',{w:400,g:40,s:5.4,x:'margin-top:3cqw'})}
  <div style="margin-top:auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2cqw;background:#ffffff99;border-radius:4cqw;padding:4cqw">${[['Now','9°'],['1pm','10°'],['4pm','8°'],['7pm','6°']].map(([a,b])=>`<div style="text-align:center">${T(a,{w:500,g:0,s:3.6,x:'opacity:.6'})}${T(b,{w:600,g:0,s:6.4,x:'font-variant-numeric:tabular-nums'})}</div>`).join('')}</div>`)},
];
window.GREX_INUSE=EX;
window.grexUse=(ex,cls='use')=>{const d=document.createElement('figure');d.className=cls;d.dataset.id=ex.id;
  d.innerHTML=`<div class="frame" style="container-type:inline-size;position:relative;aspect-ratio:${ex.ratio};overflow:hidden">${ex.html()}</div><figcaption><b>${ex.name}</b><span>${ex.note}</span></figcaption>`;return d};
})();
