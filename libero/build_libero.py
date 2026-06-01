#!/usr/bin/env python3
"""Builds libero_tasks.csv + libero_dashboard.html (blueprint style)."""
import json, csv, re
from collections import OrderedDict, Counter
HERE=__file__.rsplit('/',1)[0]
recs=json.load(open('/tmp/libero_tasks.json'))

with open(f'{HERE}/libero_tasks.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['suite','task_class','instruction'])
    for r in recs: w.writerow([r['suite'],r['task_class'],r['instruction']])
print('wrote libero_tasks.csv',len(recs))

# 4-suite leaderboard — OpenVLA-OFT paper (arXiv 2502.19645v2) Table I (filtered-demo protocol)
SUITES=['Spatial','Object','Goal','Long']
LB=[
 {'m':'Diffusion Policy','s':[78.3,92.5,68.3,50.5],'avg':72.4},
 {'m':'Octo','s':[78.9,85.7,84.6,51.1],'avg':75.1},
 {'m':'OpenVLA','s':[84.7,88.4,79.2,53.7],'avg':76.5},
 {'m':'DiT Policy','s':[84.2,96.3,85.4,63.8],'avg':82.4},
 {'m':'π0-FAST','s':[96.4,96.8,88.6,60.2],'avg':85.5},
 {'m':'π0','s':[96.8,98.8,95.8,85.2],'avg':94.2},
 {'m':'OpenVLA-OFT','s':[96.2,98.3,96.2,90.7],'avg':95.3},
 {'m':'OpenVLA-OFT (enhanced)','s':[97.6,98.4,97.9,94.5],'avg':97.1},
]
SUITE_DESC=OrderedDict([
 ('Spatial','same objects, <b>different spatial layouts</b> — tests spatial grounding'),
 ('Object','<b>different objects</b>, same layout — tests object generalization'),
 ('Goal','same scene, <b>different goals</b> — tests goal/instruction following'),
 ('Long','<b>long-horizon</b> multi-step tasks (LIBERO-10) — the real bottleneck'),
 ('LIBERO-90','90 short-horizon tasks — the broad procedural knowledge base'),
])

cnt=Counter(r['suite'] for r in recs)
SUITE_ORDER=['Spatial','Object','Goal','Long','LIBERO-90']

STOP=set('the a an to in on of and or with it that into from put pick place open close inside'.split())
wc=Counter()
for r in recs:
    for tok in re.findall(r"[a-z]+",r['instruction'].lower()):
        if tok in STOP or len(tok)<3: continue
        wc[tok]+=1
words=wc.most_common(65)

DATA={'tasks':recs,'lb':LB,'suites':SUITES,'suiteDesc':[[k,v] for k,v in SUITE_DESC.items()],
      'counts':{k:cnt[k] for k in SUITE_ORDER},'order':SUITE_ORDER,'words':words}
data_json=json.dumps(DATA,separators=(',',':'))
NTASK=len(recs)

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LIBERO · 4-Suite Lifelong Manipulation Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0b0c10; --paper2:#12141a; --card:#15171f; --ink:#e9ebf0; --dim:#838a98; --line:#222633;
    --spatial:#5b8def; --object:#e0a93b; --goal:#b079d0; --long:#e0533a; --p90:#3fb6a8; --green:#5bbf6a; --teal:#3fb6a8;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(91,141,239,.10), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(176,121,208,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--spatial)}
  .top:after{right:30px;border:1.5px solid var(--goal)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--spatial);border:1px solid var(--spatial);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--object)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--spatial),var(--goal));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.s{color:var(--spatial)} .stat .num.l{color:var(--long)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--long);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .suite-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
  .scard{border:1.5px solid var(--line);border-left-width:4px;border-radius:10px;padding:14px;background:var(--paper2)}
  .scard .sn{font-family:'Fraunces',serif;font-weight:900;font-size:19px}
  .scard .sc{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);margin:2px 0 8px}
  .scard .sd{font-size:12px;color:var(--dim);line-height:1.45}
  .scard .sd b{color:var(--ink)}
  /* heatmap */
  .heatwrap{overflow-x:auto}
  table.heat{border-collapse:collapse;font-size:11.5px;width:100%;min-width:480px}
  table.heat th{font-family:'Space Mono',monospace;font-weight:400;color:var(--dim);font-size:10.5px;padding:7px 6px;text-align:center}
  table.heat th.rowh{text-align:right;color:var(--ink);font-size:11.5px;white-space:nowrap;padding-right:12px}
  table.heat td{height:32px;text-align:center;font-family:'Space Mono',monospace;font-size:12px;border:1px solid var(--paper);color:#0b0c10;font-weight:700}
  table.heat td.avg{color:var(--ink);background:none!important;border-left:2px solid var(--line);font-size:13px}
  table.heat tr:hover td{outline:1px solid var(--ink)}
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;align-items:center}
  .controls input,.controls select{font-family:'IBM Plex Sans';font-size:13px;padding:9px 12px;border:1.5px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:8px}
  .controls input{flex:1;min-width:220px}
  .controls input:focus,.controls select:focus{outline:none;border-color:var(--teal)}
  .count-line{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:10px}
  #cloud{width:100%;height:280px;display:block}
  .tasklist{display:flex;flex-direction:column;gap:8px}
  .tcard{border:1.5px solid var(--line);border-left-width:4px;border-radius:10px;background:var(--paper2);padding:11px 15px;display:flex;align-items:center;gap:12px}
  .tcard .sp{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.05em;text-transform:uppercase;padding:3px 8px;border-radius:8px;flex:none}
  .tcard .ins{font-size:13px;color:var(--ink);line-height:1.4}
  mark{background:rgba(224,169,59,.32);color:inherit;padding:0 1px}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--spatial)} footer code{color:var(--teal)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">4 SUITES · SATURATED</div>
    <div class="kick">LIBERO · Lifelong Robot Manipulation Benchmark</div>
    <h1>LIBERO<br><em>Suite Atlas</em></h1>
    <p class="lede">LIBERO is the most-reported VLA capability benchmark: <b>4 evaluation suites</b> of 10 tasks each, plus a <b>90-task</b> procedural library, all on a Franka arm with templated language. Its design isolates <i>distribution shifts</i> one at a time &mdash; <b style="color:var(--spatial)">Spatial</b>, <b style="color:var(--object)">Object</b>, <b style="color:var(--goal)">Goal</b>, and long-horizon <b style="color:var(--long)">Long</b>. This atlas catalogs all ''' + str(NTASK) + r''' task instructions and renders the leaderboard &mdash; whose real message is that standard LIBERO is now <b>saturated</b> (97%+), with the <b style="color:var(--long)">Long</b> suite the last holdout.</p>
    <div class="statbar">
      <div class="stat"><div class="num">4+1</div><div class="lab">task suites</div></div>
      <div class="stat"><div class="num s">''' + str(NTASK) + r'''</div><div class="lab">task instructions</div></div>
      <div class="stat"><div class="num">97.1<span style="font-size:16px">%</span></div><div class="lab">SOTA avg (OFT)</div></div>
      <div class="stat"><div class="num l">94.5<span style="font-size:16px">%</span></div><div class="lab">best on Long suite</div></div>
      <div class="stat"><div class="num">8</div><div class="lab">policies compared</div></div>
    </div>
  </header>

  <div class="note">
    <b>Saturated &mdash; read with care.</b> On Spatial/Object/Goal, the strongest policies (OpenVLA-OFT, π0) now exceed <b>96%</b>; the benchmark no longer separates them there. Only the <b style="color:var(--long)">Long</b> suite still has headroom. The survey's caution: a 97% LIBERO number says little about robustness &mdash; the same models can collapse to single digits under a viewpoint or position shift (see LIBERO-Plus / LIBERO-PRO). Pair this capability score with a perturbation benchmark. Leaderboard uses the filtered-demo protocol from the OpenVLA-OFT paper.
  </div>

  <!-- 01 SUITES -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>The five suites</h2><span class="desc">each isolates a different distribution shift</span></div>
    <div class="panel"><div class="suite-grid" id="suiteGrid"></div></div>
  </section>

  <!-- 02 LEADERBOARD -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>Per-suite leaderboard</h2><span class="desc">8 policies × 4 suites · success % · sorted by average</span></div>
    <div class="panel">
      <div class="lbl">SUCCESS % · darker teal = solved · note the <span style="color:var(--long)">Long</span> column stays coolest</div>
      <div class="heatwrap"><table class="heat" id="heat"></table></div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">Reading down the <b style="color:var(--long)">Long</b> column tells the story: Diffusion Policy and Octo sit near <b style="color:var(--ink)">50%</b>, π0-FAST at 60%, and only OpenVLA-OFT (enhanced) clears <b style="color:var(--ink)">94%</b>. Every other column is effectively solved.</div>
    </div>
  </section>

  <!-- 03 WORD CLOUD -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>Instruction vocabulary</h2><span class="desc">tokenized from all ''' + str(NTASK) + r''' instructions</span></div>
    <div class="panel"><canvas id="cloud"></canvas></div>
  </section>

  <!-- 04 CATALOG -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>Task catalog</h2><span class="desc">all ''' + str(NTASK) + r''' instructions · search · filter by suite</span></div>
    <div class="panel">
      <div class="controls">
        <input id="search" placeholder="Search instruction… (e.g. bowl, drawer, stove, microwave)">
        <select id="suitesel"><option value="">All suites</option></select>
      </div>
      <div class="count-line" id="countLine"></div>
      <div class="tasklist" id="tasklist"></div>
    </div>
  </section>

  <footer>
    SOURCE · Task instructions: LIBERO (Liu et al., <a href="https://arxiv.org/abs/2306.03310">arXiv 2306.03310</a>, NeurIPS 2023), exported via the Lightwheel LW-BenchHub task table — Spatial/Object/Goal/Long (10 each) + LIBERO-90. Goal shows 11 task classes in this export (canonical LIBERO-Goal is 10). Leaderboard verbatim from OpenVLA-OFT (<a href="https://arxiv.org/abs/2502.19645">arXiv 2502.19645v2</a>, Table I, filtered-demonstration protocol): Diffusion Policy, Octo, OpenVLA, DiT Policy, π0, π0-FAST, OpenVLA-OFT (base &amp; enhanced). Success % over the standard 4 suites; LIBERO-90 is excluded from this leaderboard.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const SUITECOL={Spatial:css('--spatial'),Object:css('--object'),Goal:css('--goal'),Long:css('--long'),'LIBERO-90':css('--p90')};

// suite cards
document.getElementById('suiteGrid').innerHTML=DATA.suiteDesc.map(([k,v])=>{
  const c=SUITECOL[k];return `<div class="scard" style="border-left-color:${c}">
    <div class="sn" style="color:${c}">${k}</div><div class="sc">${DATA.counts[k]} tasks</div><div class="sd">${v}</div></div>`;}).join('');

// heatmap
(function(){
  const lerp=(a,b,t)=>a+(b-a)*t;
  function cell(v){const t=Math.max(0,Math.min(1,(v-40)/60));
    const r=Math.round(lerp(224,63,t)),g=Math.round(lerp(83,182,t)),b=Math.round(lerp(58,168,t));return `rgb(${r},${g},${b})`;}
  const rows=DATA.lb.slice().sort((a,b)=>b.avg-a.avg);
  let h='<tr><th class="rowh">policy</th>'+DATA.suites.map(s=>`<th style="color:${SUITECOL[s]}">${s}</th>`).join('')+'<th>#AVG</th></tr>';
  rows.forEach(m=>{h+=`<tr><th class="rowh">${m.m}</th>`;
    m.s.forEach(v=>h+=`<td style="background:${cell(v)}">${v.toFixed(1)}</td>`);
    h+=`<td class="avg">${m.avg.toFixed(1)}</td></tr>`;});
  document.getElementById('heat').innerHTML=h;
})();

// word cloud
(function(){
  const cv=document.getElementById('cloud');const ctx=cv.getContext('2d');
  function draw(){
    const dpr=window.devicePixelRatio||1;const W=cv.clientWidth,H=280;
    cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const words=DATA.words;if(!words.length)return;const mx=words[0][1],mn=words[words.length-1][1];
    const pal=[css('--spatial'),css('--object'),css('--goal'),css('--long'),css('--p90'),css('--ink')];
    const placed=[];
    words.forEach((w,i)=>{
      const fs=12+(w[1]-mn)/Math.max(1,(mx-mn))*40;
      ctx.font=`${fs>26?900:600} ${fs}px Fraunces, serif`;
      const tw=ctx.measureText(w[0]).width, th=fs*0.92, pad=2, cx=W/2, cy=H/2;
      for(let sp=0;sp<2600;sp++){const r=sp*0.45,ang=sp*0.42;
        const x=cx+r*Math.cos(ang)-tw/2, y=cy+r*Math.sin(ang)+th/2;
        if(x<3||x+tw>W-3||y-th<3||y>H-3)continue;
        const box={x:x-pad,y:y-th-pad,w:tw+2*pad,h:th+2*pad};let ok=true;
        for(const p of placed){if(box.x<p.x+p.w&&box.x+box.w>p.x&&box.y<p.y+p.h&&box.y+box.h>p.y){ok=false;break;}}
        if(ok){placed.push(box);ctx.fillStyle=pal[i%pal.length];ctx.fillText(w[0],x,y);break;}}
      });
  }
  draw();let t;window.addEventListener('resize',()=>{clearTimeout(t);t=setTimeout(draw,200);});
})();

// catalog
(function(){
  const sel=document.getElementById('suitesel');
  DATA.order.forEach(s=>sel.innerHTML+=`<option value="${s}">${s} (${DATA.counts[s]})</option>`);
  function render(){
    const q=document.getElementById('search').value.toLowerCase().trim();
    const su=sel.value;
    let rows=DATA.tasks.filter(t=>(!q||t.instruction.toLowerCase().includes(q))&&(!su||t.suite===su));
    const ord=DATA.order;rows=rows.slice().sort((a,b)=>ord.indexOf(a.suite)-ord.indexOf(b.suite));
    const hl=s=>q?s.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>'):s;
    document.getElementById('countLine').textContent=`Showing ${rows.length} / ${DATA.tasks.length} tasks`;
    document.getElementById('tasklist').innerHTML=rows.map(t=>{const c=SUITECOL[t.suite];
      return `<div class="tcard" style="border-left-color:${c}"><span class="sp" style="background:${c}22;color:${c}">${t.suite}</span><span class="ins">${hl(t.instruction)}</span></div>`;}).join('');
  }
  document.getElementById('search').addEventListener('input',render);
  sel.addEventListener('change',render);render();
})();
</script>
'''
open(f'{HERE}/libero_dashboard.html','w').write(HTML)
print('wrote libero_dashboard.html',len(HTML),'bytes')
