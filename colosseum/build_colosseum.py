#!/usr/bin/env python3
"""Builds colosseum.csv + colosseum_dashboard.html (blueprint style)."""
import json, csv
HERE=__file__.rsplit('/',1)[0]
A=json.load(open('/tmp/colosseum_agg.json'))
agg=A['agg']; NOV=A['nov']; ALLV=A['allv']

GROUP={
 'MO_Color':'Manipulated object','MO_Texture':'Manipulated object','MO_Size':'Manipulated object',
 'RO_Color':'Receiver object','RO_Texture':'Receiver object','RO_Size':'Receiver object',
 'Light_Color':'Scene','Table_Color':'Scene','Table_Texture':'Scene','Background_Texture':'Scene',
 'Distractor':'Distractors','Camera_Pose':'Camera','Object_Friction':'Physics','Object_Mass':'Physics',
}
LABEL={'MO_Color':'Object color','MO_Texture':'Object texture','MO_Size':'Object size',
 'RO_Color':'Receiver color','RO_Texture':'Receiver texture','RO_Size':'Receiver size',
 'Light_Color':'Light color','Table_Color':'Table color','Table_Texture':'Table texture',
 'Background_Texture':'Background texture','Distractor':'Distractor objects','Camera_Pose':'Camera pose',
 'Object_Friction':'Object friction','Object_Mass':'Object mass'}
TASKS=['open drawer','slide block to target','basketball in hoop','meat on grill','close box',
 'close laptop lid','empty dishwasher','reach and drag','get ice from fridge','hockey',
 'put money in safe','place wine at rack location','move hanger','wipe desk','straighten rope',
 'insert onto square peg','stack cups','turn oven on','setup chess','scoop with spatula']
MODELS=['R3M-MLP','MVP-MLP','PerAct','RVT','VoxPoser']

factors=[{'key':k,'label':LABEL[k],'group':GROUP[k],'deg':agg[k]['deg'],
          'success':agg[k]['mean_success'],'baseline':agg[k]['baseline']} for k in agg]
factors.sort(key=lambda x:-x['deg'])

with open(f'{HERE}/colosseum.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['perturbation_factor','group','mean_success_pct','baseline_pct','degradation_pct'])
    for x in factors: w.writerow([x['key'],x['group'],x['success'],x['baseline'],x['deg']])
print('wrote colosseum.csv')

DATA={'factors':factors,'tasks':TASKS,'models':MODELS,'nov':NOV,'allv':ALLV,
      'combined':round((NOV-ALLV)/NOV*100,1)}
data_json=json.dumps(DATA,separators=(',',':'))

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>THE COLOSSEUM · Generalization Perturbation Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0e0c08; --paper2:#15120c; --card:#19150d; --ink:#efe8d8; --dim:#a2967c; --line:#322a1c;
    --bronze:#c89b4a; --sand:#d8b878; --rust:#d0673a; --teal:#4fb0a0; --red:#d8503a; --green:#8bb05a; --blue:#6f9fd0;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(200,155,74,.12), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(208,103,58,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--bronze)}
  .top:after{right:30px;border:1.5px solid var(--rust)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--bronze);border:1px solid var(--bronze);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--rust)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,64px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--bronze),var(--rust));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.b{color:var(--bronze)} .stat .num.r{color:var(--red)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--bronze);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--bronze);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--rust)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .bar-wrap{display:flex;flex-direction:column;gap:8px}
  .bar-row{display:grid;grid-template-columns:148px 1fr 46px;align-items:center;gap:12px}
  .bar-row .name{font-size:12.5px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bar-row .grp{font-family:'Space Mono',monospace;font-size:8px}
  .track{height:18px;background:var(--paper);border:1px solid var(--line);border-radius:3px;overflow:hidden;position:relative;background-image:repeating-linear-gradient(90deg,transparent,transparent calc(25% - 1px),var(--line) calc(25% - 1px),var(--line) 25%)}
  .fill{height:100%;position:relative;z-index:1;transition:width .5s cubic-bezier(.2,.8,.2,1)}
  .bar-row .v{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;text-align:right}
  .legend{display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:14px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim)}
  .legend span{display:flex;align-items:center;gap:6px} .legend i{width:11px;height:11px;border-radius:2px}
  .grpwrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
  .grpcard{border:1.5px solid var(--line);border-top:4px solid var(--line);border-radius:10px;padding:13px;background:var(--paper2)}
  .grpcard .gn{font-family:'Fraunces',serif;font-weight:900;font-size:16px}
  .grpcard .gf{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);margin-top:6px;line-height:1.6}
  .tasklist{display:grid;grid-template-columns:1fr;gap:7px}
  @media(min-width:680px){.tasklist{grid-template-columns:1fr 1fr}}
  .tcard{border:1.5px solid var(--line);border-radius:9px;background:var(--paper2);padding:10px 13px;font-family:'Space Mono',monospace;font-size:12px;color:var(--ink);display:flex;gap:9px;align-items:center}
  .tcard .n{color:var(--bronze);font-size:10px}
  .combobar{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
  #combo{flex:1;min-width:280px;height:60px}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--blue)} footer code{color:var(--bronze)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">14 AXES · 20 TASKS</div>
    <div class="kick">THE COLOSSEUM · Systematic Generalization Benchmark</div>
    <h1>THE COLOSSEUM<br><em>Perturbation Atlas</em></h1>
    <div class="byline" style="font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2"><b style="color:var(--ink);font-weight:600">Jie Wang</b> · <a href="https://everloom-129.github.io/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">everloom-129.github.io</a> · GRASP Lab, UPenn &nbsp;·&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">Claude Code</a> &nbsp;·&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
    <p class="lede">THE COLOSSEUM stress-tests manipulation policies by perturbing <b>14 environmental factors</b> &mdash; the color, texture and size of the manipulated &amp; receiver objects, table and background appearance, lighting, distractors, camera pose, and physical properties &mdash; across <b>20 RLBench tasks</b> and <b>5 models</b>. Unlike the LIBERO probes, its perturbations are <b>physically grounded</b> and shown to correlate with real-robot results. The finding: each single factor costs <b>~30&ndash;50%</b> success for strong baselines, and <b>combining them erases ≥75%</b>.</p>
    <div class="statbar">
      <div class="stat"><div class="num b">14</div><div class="lab">perturbation factors</div></div>
      <div class="stat"><div class="num">20</div><div class="lab">RLBench tasks</div></div>
      <div class="stat"><div class="num">5</div><div class="lab">models evaluated</div></div>
      <div class="stat"><div class="num r">&minus;''' + str(DATA['combined']) + r'''<span style="font-size:15px">%</span></div><div class="lab">all-perturbations drop</div></div>
      <div class="stat"><div class="num b">0.61</div><div class="lab">sim↔real R²</div></div>
    </div>
  </header>

  <div class="note">
    <b>What breaks generalization.</b> Aggregated across all 5 models and 20 tasks, the most damaging single perturbations are <b style="color:var(--red)">object color</b> and <b style="color:var(--red)">distractor objects</b>, followed by table/light color &mdash; appearance and clutter, not geometry. <b style="color:var(--ink)">Camera pose</b>, <b style="color:var(--ink)">background texture</b> and <b style="color:var(--ink)">receiver texture</b> are comparatively benign on average. Bars below show <b>% success lost vs. the unperturbed baseline</b>, computed over every model×task cell with both values reported.
  </div>

  <!-- 01 FACTOR IMPACT -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>What hurts most</h2><span class="desc">14 factors ranked by mean success lost · across 5 models × 20 tasks</span></div>
    <div class="panel">
      <div class="lbl">PERFORMANCE DEGRADATION % · longer / redder = more damaging</div>
      <div class="bar-wrap" id="bars"></div>
      <div class="legend" id="legend"></div>
    </div>
  </section>

  <!-- 02 COMBINED -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>Single vs. combined</h2><span class="desc">unperturbed → all-perturbations-at-once</span></div>
    <div class="panel">
      <div class="combobar">
        <svg id="combo" viewBox="0 0 760 60"></svg>
      </div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">Mean success collapses from <b style="color:var(--teal)">''' + str(round(NOV,1)) + r'''%</b> (no variations) to <b style="color:var(--red)">''' + str(round(ALLV,1)) + r'''%</b> when all 14 factors are perturbed together &mdash; a <b style="color:var(--ink)">''' + str(DATA['combined']) + r'''% relative drop</b>. Robustness is not additive: stacking perturbations compounds failure far beyond any single factor. And because COLOSSEUM perturbations are physically realistic, this degradation <b>transfers to real robots</b> (R²≈0.61).</div>
    </div>
  </section>

  <!-- 03 FACTOR GROUPS -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>The 14 factors</h2><span class="desc">grouped by what they perturb</span></div>
    <div class="panel"><div class="grpwrap" id="grpGrid"></div></div>
  </section>

  <!-- 04 TASKS -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>The 20 tasks</h2><span class="desc">a curated RLBench subset · each evaluated under all 14 perturbations</span></div>
    <div class="panel"><div class="tasklist" id="taskList"></div></div>
  </section>

  <footer>
    SOURCE · THE COLOSSEUM (Pumacay et al., <a href="https://arxiv.org/abs/2402.08191">arXiv 2402.08191v2</a>, RSS 2024); repo <a href="https://github.com/robot-colosseum/robot-colosseum">robot-colosseum</a>. 14 perturbation factors · 20 RLBench tasks · 5 models (R3M-MLP, MVP-MLP, PerAct, RVT, VoxPoser). Per-factor degradation computed here from the paper's per-task success tables (Tables&nbsp;3–7), aggregated over all model×task cells where both the perturbed and unperturbed values are reported; "All-perturbations" and "No-variations" means likewise. MO = manipulated object, RO = receiver object. Sim↔real correlation R̄²≈0.614 reported in the paper.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const GROUPCOL={'Manipulated object':css('--rust'),'Receiver object':css('--sand'),'Scene':css('--bronze'),
  'Distractors':css('--red'),'Camera':css('--blue'),'Physics':css('--teal')};

// factor impact bars
(function(){
  const mx=Math.max(...DATA.factors.map(f=>f.deg));
  document.getElementById('bars').innerHTML=DATA.factors.map(f=>{
    const c=GROUPCOL[f.group];
    return `<div class="bar-row"><div class="name" title="${f.group}">${f.label}</div>
      <div class="track"><div class="fill" style="width:${f.deg/mx*100}%;background:${c}"></div></div>
      <div class="v" style="color:${c}">&minus;${f.deg}</div></div>`;}).join('');
  document.getElementById('legend').innerHTML=Object.keys(GROUPCOL).map(g=>
    `<span><i style="background:${GROUPCOL[g]}"></i>${g}</span>`).join('');
})();

// combined dumbbell (single horizontal)
(function(){
  const W=760,H=60,padL=10,padR=10,y=30;
  const x=v=>padL+v/100*(W-padL-padR);
  let s='';
  for(let g=0;g<=100;g+=20){const xx=x(g);s+=`<line x1="${xx}" y1="14" x2="${xx}" y2="46" stroke="${css('--line')}"/>`;s+=`<text x="${xx}" y="58" text-anchor="middle" style="font-family:'Space Mono';font-size:9px;fill:${css('--dim')}">${g}%</text>`;}
  s+=`<line x1="${x(DATA.allv)}" y1="${y}" x2="${x(DATA.nov)}" y2="${y}" stroke="${css('--red')}" stroke-width="3" opacity="0.5"/>`;
  s+=`<circle cx="${x(DATA.nov)}" cy="${y}" r="8" fill="${css('--teal')}"/>`;
  s+=`<circle cx="${x(DATA.allv)}" cy="${y}" r="8" fill="${css('--red')}"/>`;
  s+=`<text x="${x(DATA.nov)+12}" y="${y+4}" style="font-family:Fraunces;font-weight:900;font-size:15px;fill:${css('--teal')}">${DATA.nov}%</text>`;
  s+=`<text x="${x(DATA.allv)-12}" y="${y-12}" text-anchor="middle" style="font-family:Fraunces;font-weight:900;font-size:15px;fill:${css('--red')}">${DATA.allv}%</text>`;
  s+=`<text x="${x(DATA.nov)+12}" y="${y+18}" style="font-family:'Space Mono';font-size:9px;fill:${css('--dim')}">no variations</text>`;
  s+=`<text x="${x(DATA.allv)-12}" y="${y+2}" text-anchor="end" style="font-family:'Space Mono';font-size:9px;fill:${css('--dim')}">all 14 perturbed</text>`;
  document.getElementById('combo').innerHTML=s;
})();

// factor groups
(function(){
  const groups={};DATA.factors.forEach(f=>{(groups[f.group]=groups[f.group]||[]).push(f.label);});
  document.getElementById('grpGrid').innerHTML=Object.keys(GROUPCOL).filter(g=>groups[g]).map(g=>
    `<div class="grpcard" style="border-top-color:${GROUPCOL[g]}"><div class="gn" style="color:${GROUPCOL[g]}">${g}</div>
      <div class="gf">${groups[g].map(x=>'· '+x).join('<br>')}</div></div>`).join('');
})();

// tasks
document.getElementById('taskList').innerHTML=DATA.tasks.map((t,i)=>
  `<div class="tcard"><span class="n">${String(i+1).padStart(2,'0')}</span>${t}</div>`).join('');
</script>
'''
open(f'{HERE}/colosseum_dashboard.html','w').write(HTML)
print('wrote colosseum_dashboard.html',len(HTML),'bytes')
