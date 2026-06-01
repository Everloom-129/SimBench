#!/usr/bin/env python3
"""Builds libero_plus.csv + libero_plus_dashboard.html (blueprint style)."""
import json, csv
HERE=__file__.rsplit('/',1)[0]

FACTORS=['Camera','Robot','Language','Light','Background','Noise','Layout']
FACTOR_DESC={
 'Camera':'shifts the 3rd-person camera distance &amp; orientation',
 'Robot':'random perturbations to the arm&rsquo;s initial joint angles',
 'Language':'task instructions rewritten by an LLM',
 'Light':'alters diffuse color &amp; light direction',
 'Background':'modifies scene themes / wall &amp; floor textures',
 'Noise':'adds sensor (camera) noise',
 'Layout':'injects confounding objects &amp; shifts the target object',
}
# Official LIBERO-Plus leaderboard (github.com/sylvestf/LIBERO-plus README) — success % under each perturbation
LB=[
 ('OpenVLA',         [0.8,3.5,23.0,8.1,34.8,15.2,28.5],15.6),
 ('OpenVLA-OFT',     [56.4,31.9,79.5,88.7,93.3,75.8,74.2],69.6),
 ('OpenVLA-OFT_w',   [10.4,38.7,70.5,76.8,93.6,49.9,69.9],55.8),
 ('NORA',            [2.2,37.0,65.1,45.7,58.6,12.8,62.1],39.0),
 ('WorldVLA',        [0.1,27.9,41.6,43.7,17.1,10.9,38.0],25.0),
 ('UniVLA',          [1.8,46.2,69.6,69.0,81.0,21.2,31.9],43.9),
 ('π0',              [13.8,6.0,58.8,85.0,81.4,79.0,68.9],53.6),
 ('π0-Fast',         [65.1,21.6,61.0,73.2,73.2,74.4,68.8],61.6),
 ('RIPT-VLA',        [55.2,31.2,77.6,88.4,91.6,73.5,74.2],68.4),
 ('OpenVLA-OFT_m',   [55.6,21.7,81.0,92.7,91.0,78.6,68.7],67.9),
 ('OpenVLA-OFT+',    [92.8,30.3,85.8,94.9,93.9,89.3,77.6],79.6),
]
# clean LIBERO 4-suite avg (OpenVLA-OFT paper) for the models we also have clean numbers for
CLEAN={'OpenVLA':76.5,'OpenVLA-OFT':95.3,'π0':94.2,'π0-Fast':85.5}
SUITE_DIST={'Spatial':2293,'Object':2576,'Goal':2569,'Long':2592}

with open(f'{HERE}/libero_plus.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['model']+FACTORS+['Total'])
    for m,s,t in LB: w.writerow([m]+s+[t])
print('wrote libero_plus.csv')

# per-factor average across models (which perturbation is hardest)
favg={f:round(sum(s[i] for _,s,_ in LB)/len(LB),1) for i,f in enumerate(FACTORS)}
# robustness gap
GAP=[{'m':m,'clean':CLEAN[m],'plus':t} for (m,s,t) in LB if m in CLEAN]

DATA={'factors':FACTORS,'factorDesc':FACTOR_DESC,'lb':[{'m':m,'s':s,'t':t} for m,s,t in LB],
      'favg':favg,'gap':GAP,'suiteDist':SUITE_DIST}
data_json=json.dumps(DATA,separators=(',',':'),ensure_ascii=False)

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LIBERO-Plus · VLA Robustness / Perturbation Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#100a0b; --paper2:#181011; --card:#1b1213; --ink:#f0e7e6; --dim:#a08988; --line:#33211f;
    --red:#e0463a; --amber:#e0993b; --teal:#3fb6a8; --blue:#5b8def; --green:#5bbf6a; --violet:#b079d0;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(224,70,58,.12), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(224,153,59,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--red)}
  .top:after{right:30px;border:1.5px solid var(--amber)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--red);border:1px solid var(--red);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--amber)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--red),var(--amber));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.r{color:var(--red)} .stat .num.a{color:var(--amber)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--red);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--amber);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--amber)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .fac-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px}
  .fac{border:1.5px solid var(--line);border-radius:10px;padding:14px;background:var(--paper2);position:relative;overflow:hidden}
  .fac .fn{font-family:'Fraunces',serif;font-weight:900;font-size:17px}
  .fac .fa{font-family:'Space Mono',monospace;font-size:22px;font-weight:700;margin:6px 0 2px}
  .fac .fl{font-family:'Space Mono',monospace;font-size:8.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
  .fac .fd{font-size:11px;color:var(--dim);line-height:1.4;margin-top:8px}
  .heatwrap{overflow-x:auto}
  table.heat{border-collapse:collapse;font-size:11.5px;width:100%;min-width:640px}
  table.heat th{font-family:'Space Mono',monospace;font-weight:400;color:var(--dim);font-size:10.5px;padding:7px 6px;text-align:center}
  table.heat th.rowh{text-align:right;color:var(--ink);font-size:11.5px;white-space:nowrap;padding-right:12px}
  table.heat td{height:30px;text-align:center;font-family:'Space Mono',monospace;font-size:11.5px;border:1px solid var(--paper);color:#100a0b;font-weight:700}
  table.heat td.tot{color:var(--ink);background:none!important;border-left:2px solid var(--line);font-size:12.5px}
  table.heat tr:hover td{outline:1px solid var(--ink)}
  table.heat tr.hl td{outline:1.5px solid var(--amber)}
  #gap{width:100%;height:230px;display:block}
  .gx{font-family:'Space Mono',monospace;font-size:10px;fill:var(--dim)}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--blue)} footer code{color:var(--amber)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">95% &rarr; &lt;30%</div>
    <div class="kick">LIBERO-Plus · In-Depth Robustness Analysis of VLAs</div>
    <h1>LIBERO-Plus<br><em>Perturbation Atlas</em></h1>
    <p class="lede">LIBERO-Plus takes the saturated LIBERO suites and asks the real question: <b>do VLAs actually generalize, or memorize?</b> It applies <b>controlled perturbations across 7 dimensions</b> &mdash; camera viewpoint, robot initial state, language, lighting, background, sensor noise, object layout &mdash; over <b>10,030 evaluation instances</b> (21 sub-components). The verdict is brutal: policies scoring <b>95%+</b> on clean LIBERO <b>collapse below 30%</b> under a modest camera shift, and they <b>ignore language almost entirely</b>.</p>
    <div class="statbar">
      <div class="stat"><div class="num r">7</div><div class="lab">perturbation factors</div></div>
      <div class="stat"><div class="num">21</div><div class="lab">sub-components</div></div>
      <div class="stat"><div class="num a">10,030</div><div class="lab">eval instances</div></div>
      <div class="stat"><div class="num">11</div><div class="lab">VLAs analyzed</div></div>
      <div class="stat"><div class="num r">&minus;60<span style="font-size:16px">pt</span></div><div class="lab">worst-case drop</div></div>
    </div>
  </header>

  <div class="note">
    <b>The two killers: viewpoint &amp; embodiment.</b> Across all 11 models, the <b style="color:var(--red)">Camera</b> and <b style="color:var(--red)">Robot initial state</b> perturbations cause the largest collapse &mdash; π0 falls to <b>6%</b> when the arm starts from a new pose. Meanwhile <b style="color:var(--ink)">Language</b>, <b style="color:var(--ink)">Light</b> and <b style="color:var(--ink)">Background</b> barely dent performance &mdash; and the paper shows the language-insensitivity is because models <i>tend to ignore the instruction entirely</i>. Cells below are success % <b>under</b> each perturbation (higher = more robust).
  </div>

  <!-- 01 FACTORS -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>The 7 perturbation factors</h2><span class="desc">mean success across all 11 models · sorted hardest-first</span></div>
    <div class="panel"><div class="fac-grid" id="facGrid"></div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">The number on each card is the <b>average success across all 11 models</b> under that perturbation. <b style="color:var(--red)">Robot</b> and <b style="color:var(--red)">Camera</b> are the bottleneck; everything else stays comparatively intact.</div>
    </div>
  </section>

  <!-- 02 HEATMAP -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>Robustness matrix</h2><span class="desc">11 VLAs × 7 perturbations · success % · sorted by total</span></div>
    <div class="panel">
      <div class="lbl">SUCCESS % UNDER PERTURBATION · darker red = collapses · darker teal = robust</div>
      <div class="heatwrap"><table class="heat" id="heat"></table></div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">Read down the <b style="color:var(--red)">Camera</b> and <b style="color:var(--red)">Robot</b> columns: a sea of red for almost every policy. Only <b style="color:var(--ink)">OpenVLA-OFT+</b> &mdash; explicitly trained on the perturbation set &mdash; recovers Camera robustness (92.8%), and even it still struggles with Robot state (30.3%).</div>
    </div>
  </section>

  <!-- 03 GAP -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>The robustness gap</h2><span class="desc">clean LIBERO → LIBERO-Plus total · the headline collapse</span></div>
    <div class="panel">
      <div class="lbl">EACH LINE = ONE POLICY · left dot = clean LIBERO avg · right dot = LIBERO-Plus total · longer = more brittle</div>
      <svg id="gap" viewBox="0 0 760 230"></svg>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)"><b style="color:var(--ink)">OpenVLA</b> falls from 76.5 → <b style="color:var(--red)">15.6</b>; <b style="color:var(--ink)">π0</b> from 94.2 → <b style="color:var(--red)">53.6</b>; <b style="color:var(--ink)">OpenVLA-OFT</b> from 95.3 → 69.6. The survey&rsquo;s thesis in one chart: a high clean-LIBERO score says little about robustness &mdash; never report it alone.</div>
    </div>
  </section>

  <footer>
    SOURCE · LIBERO-Plus (Fei et al., <a href="https://arxiv.org/abs/2510.13626">arXiv 2510.13626</a>, 2025); leaderboard verbatim from the official repo <a href="https://github.com/sylvestf/LIBERO-plus">github.com/sylvestf/LIBERO-plus</a>. 7 perturbation factors · 21 sub-components · 10,030 eval instances (Spatial 2,293 / Object 2,576 / Goal 2,569 / Long 2,592). Cells are success % <i>under</i> each perturbation; Total is the overall LIBERO-Plus score. Clean-LIBERO baselines (for the gap chart) from the OpenVLA-OFT paper (<a href="https://arxiv.org/abs/2502.19645">arXiv 2502.19645</a>). Variants: <code>_w</code> = no wrist cam, <code>_m</code> = mix-SFT, <code>+</code> = trained on LIBERO-Plus data.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const lerp=(a,b,t)=>a+(b-a)*t;
function cell(v){const t=Math.max(0,Math.min(1,v/100));
  const r=Math.round(lerp(224,63,t)),g=Math.round(lerp(70,182,t)),b=Math.round(lerp(58,168,t));return `rgb(${r},${g},${b})`;}

// factor cards (sorted hardest first by favg)
(function(){
  const facs=DATA.factors.slice().sort((a,b)=>DATA.favg[a]-DATA.favg[b]);
  document.getElementById('facGrid').innerHTML=facs.map(f=>{
    const v=DATA.favg[f];const c=cell(v);
    return `<div class="fac" style="border-left:4px solid ${c}">
      <div class="fn">${f}</div><div class="fa" style="color:${c}">${v}%</div>
      <div class="fl">avg success</div><div class="fd">${DATA.factorDesc[f]}</div></div>`;}).join('');
})();

// heatmap
(function(){
  const rows=DATA.lb.slice().sort((a,b)=>b.t-a.t);
  let h='<tr><th class="rowh">model</th>'+DATA.factors.map(f=>`<th>${f}</th>`).join('')+'<th>TOTAL</th></tr>';
  rows.forEach(m=>{const hl=m.m==='OpenVLA-OFT+'?' class="hl"':'';
    h+=`<tr${hl}><th class="rowh">${m.m}</th>`;
    m.s.forEach(v=>h+=`<td style="background:${cell(v)}">${v.toFixed(1)}</td>`);
    h+=`<td class="tot">${m.t.toFixed(1)}</td></tr>`;});
  document.getElementById('heat').innerHTML=h;
})();

// robustness gap dumbbell
(function(){
  const rows=DATA.gap.slice().sort((a,b)=>b.clean-a.clean);
  const W=760,H=230,padL=120,padR=70,padT=20,padB=34;
  const x=v=>padL+v/100*(W-padL-padR);
  const rowH=(H-padT-padB)/rows.length;
  let s='';
  for(let g=0;g<=100;g+=20){const xx=x(g);s+=`<line x1="${xx}" y1="${padT}" x2="${xx}" y2="${H-padB}" stroke="${css('--line')}"/>`;s+=`<text x="${xx}" y="${H-padB+15}" text-anchor="middle" class="gx">${g}%</text>`;}
  rows.forEach((r,i)=>{const cy=padT+rowH*(i+0.5);
    s+=`<text x="${padL-12}" y="${cy+4}" text-anchor="end" class="gx" style="fill:${css('--ink')};font-size:11px">${r.m}</text>`;
    s+=`<line x1="${x(r.plus)}" y1="${cy}" x2="${x(r.clean)}" y2="${cy}" stroke="${css('--red')}" stroke-width="2" opacity="0.5"/>`;
    s+=`<circle cx="${x(r.clean)}" cy="${cy}" r="5.5" fill="${css('--teal')}"/>`;
    s+=`<circle cx="${x(r.plus)}" cy="${cy}" r="5.5" fill="${css('--red')}"/>`;
    s+=`<text x="${x(r.clean)+9}" y="${cy+4}" class="gx" style="fill:${css('--teal')}">${r.clean.toFixed(1)}</text>`;
    s+=`<text x="${x(r.plus)-9}" y="${cy+4}" text-anchor="end" class="gx" style="fill:${css('--red')}">${r.plus.toFixed(1)}</text>`;});
  s+=`<circle cx="${padL+4}" cy="12" r="5" fill="${css('--teal')}"/><text x="${padL+14}" y="16" class="gx" style="fill:${css('--teal')}">clean LIBERO</text>`;
  s+=`<circle cx="${padL+140}" cy="12" r="5" fill="${css('--red')}"/><text x="${padL+150}" y="16" class="gx" style="fill:${css('--red')}">LIBERO-Plus</text>`;
  document.getElementById('gap').innerHTML=s;
})();
</script>
'''
open(f'{HERE}/libero_plus_dashboard.html','w').write(HTML)
print('wrote libero_plus_dashboard.html',len(HTML),'bytes')
