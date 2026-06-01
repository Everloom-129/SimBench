#!/usr/bin/env python3
"""Builds rlbench_tasks.csv + rlbench_dashboard.html (blueprint style)."""
import json, csv, re
from collections import OrderedDict, Counter

HERE = __file__.rsplit('/', 1)[0]
names = [l.strip() for l in open('/tmp/rlbench_tasknames.txt') if l.strip()]

# ---------- categorize 100+ tasks into skill families ----------
def categorize(t):
    if t.startswith('stack_'):                       return 'Stack'
    if re.match(r'(open|close)_', t) or t in ('slide_cabinet_open','slide_cabinet_open_and_place_cups'):
        return 'Open / Close'
    if any(k in t for k in ('button','switch','channel','lamp_','tv_on','light_bulb','toilet_seat','beat_the_buzz','turn_oven_on','change_clock')):
        return 'Buttons & Switches'
    if any(k in t for k in ('insert','screw','plug_charger','unplug','peg','usb','nail','hanger','hang_frame')):
        return 'Insert & Fasten'
    if any(k in t for k in ('sweep','wipe','scoop','water_plants','straighten_rope','drag','pour','empty_','take_lid','take_off_weighing','weighing')):
        return 'Tool Use'
    if any(k in t for k in ('puzzle','checkers','chess','jenga','shape_sorter','hockey','basketball','hit_ball','set_the_table','setup_','solve_','pyramid','numbered')):
        return 'Games & Sorting'
    if any(k in t for k in ('put_','place_','take_','get_ice','remove_cups','move_hanger','phone_on_base','frame_on_hanger')):
        return 'Pick & Place'
    if any(k in t for k in ('reach','slide_block','turn_tap','press','pick_')):
        return 'Reach & Push'
    return 'Pick & Place'

SKILLVERB = {  # leading verb -> human skill
}
def humanize(t):
    return t.replace('_',' ')

# the 18-task multi-task benchmark (PerAct/RVT/RVT-2). map display -> repo task
BENCH18 = OrderedDict([
    ('Close Jar','close_jar'),('Drag Stick','reach_and_drag'),('Insert Peg','insert_onto_square_peg'),
    ('Meat off Grill','meat_off_grill'),('Open Drawer','open_drawer'),('Place Cups','place_cups'),
    ('Place Wine','stack_wine'),('Push Buttons','push_buttons'),('Put in Cupboard','put_groceries_in_cupboard'),
    ('Put in Drawer','put_item_in_drawer'),('Put in Safe','put_money_in_safe'),('Screw Bulb','light_bulb_in'),
    ('Slide Block','slide_block_to_target'),('Sort Shape','place_shape_in_shape_sorter'),('Stack Blocks','stack_blocks'),
    ('Stack Cups','stack_cups'),('Sweep to Dustpan','sweep_to_dustpan'),('Turn Tap','turn_tap'),
])
bench_repo = set(BENCH18.values())

recs = []
for t in sorted(names):
    recs.append({'task':t,'category':categorize(t),'label':humanize(t),'bench18':t in bench_repo})

with open(f'{HERE}/rlbench_tasks.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['task','category','label','in_18task_benchmark'])
    for r in recs: w.writerow([r['task'],r['category'],r['label'],r['bench18']])
print('wrote rlbench_tasks.csv', len(recs))

# ---------- 18-task multi-task leaderboard (verbatim, RVT-2 paper Table I, arXiv 2406.08545v1) ----------
T18 = list(BENCH18.keys())
LB = {
 'tasks': T18,
 'methods': [
   {'m':'Image-BC (CNN)','avg':1.3,'fps':None,'s':[0,0,0,0,4,0,0,0,0,8,4,0,0,0,0,0,0,8]},
   {'m':'Image-BC (ViT)','avg':1.3,'fps':None,'s':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16]},
   {'m':'C2F-ARM-BC','avg':20.1,'fps':None,'s':[24,24,4,20,20,0,8,72,0,4,12,8,16,8,0,0,0,68]},
   {'m':'HiveFormer','avg':45.3,'fps':None,'s':[52,76,0,100,52,0,80,84,32,68,76,8,64,8,8,0,28,80]},
   {'m':'PolarNet','avg':46.4,'fps':None,'s':[36,92,4,100,84,0,40,96,12,32,84,44,56,12,4,8,52,80]},
   {'m':'PerAct','avg':49.4,'fps':4.9,'s':[55.2,89.6,5.6,70.4,88.0,2.4,44.8,92.8,28.0,51.2,84.0,17.6,74.0,16.8,26.4,2.4,52.0,88.0]},
   {'m':'RVT','avg':62.9,'fps':11.6,'s':[52.0,99.2,11.2,88.0,71.2,4.0,91.0,100.0,49.6,88.0,91.2,48.0,81.6,36.0,28.8,26.4,72.0,93.6]},
   {'m':'Act3D','avg':65.0,'fps':None,'s':[92,92,27,94,93,3,80,99,51,90,95,47,93,8,12,9,92,94]},
   {'m':'RVT-2','avg':81.4,'fps':20.6,'s':[100.0,99.0,40.0,99.0,74.0,38.0,95.0,100.0,66.0,96.0,96.0,88.0,92.0,35.0,80.0,69.0,100.0,99.0]},
 ]}

# ---------- aggregate ----------
cats=OrderedDict()
for r in recs:
    cats.setdefault(r['category'],0); cats[r['category']]+=1
cat_list=[{'cat':k,'n':v} for k,v in sorted(cats.items(),key=lambda x:-x[1])]

# word freq from task names (verbs/objects)
STOP=set('the a an to in on of and or with from out off into at'.split())
wc=Counter()
for r in recs:
    for tok in r['task'].split('_'):
        if tok in STOP or len(tok)<2: continue
        wc[tok]+=1
words=wc.most_common(60)

DATA={'tasks':recs,'lb':LB,'cats':cat_list,'words':words,'bench18':BENCH18}
data_json=json.dumps(DATA,separators=(',',':'))
NTASK=len(recs); NBENCH=len(T18)

HTML = r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>RLBench · Task &amp; Multi-Task Leaderboard Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0c0d0f; --paper2:#131519; --card:#16181d; --ink:#e8eaed; --dim:#878d99; --line:#242832;
    --red:#e0533a; --orange:#e89b3c; --teal:#3fb6a8; --blue:#5b8def; --green:#74c476; --violet:#9a7bff;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(224,83,58,.10), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(63,182,168,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--red)}
  .top:after{right:30px;border:1.5px solid var(--teal)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--red);border:1px solid var(--red);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--orange)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--red),var(--orange));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.r{color:var(--red)} .stat .num.t{color:var(--teal)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--red);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .twocol{display:grid;gap:18px}
  @media(min-width:880px){.twocol{grid-template-columns:.85fr 1.15fr}}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .donutwrap{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
  #catdonut{flex:0 0 168px}
  .dl{display:flex;flex-direction:column;gap:8px;font-size:12.5px}
  .dl span{display:flex;align-items:center;gap:9px}
  .dl i{width:12px;height:12px;border-radius:2px;flex:none}
  .dl b{font-family:'Space Mono',monospace;color:var(--dim);font-weight:400;margin-left:auto;padding-left:12px}
  .bar-wrap{display:flex;flex-direction:column;gap:8px}
  .bar-row{display:grid;grid-template-columns:130px 1fr 44px;align-items:center;gap:12px}
  .bar-row .name{font-size:12.5px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:'Space Mono',monospace}
  .track{height:18px;background:var(--paper);border:1px solid var(--line);border-radius:3px;overflow:hidden;position:relative;background-image:repeating-linear-gradient(90deg,transparent,transparent calc(25% - 1px),var(--line) calc(25% - 1px),var(--line) 25%)}
  .fill{height:100%;position:relative;z-index:1;transition:width .5s cubic-bezier(.2,.8,.2,1)}
  .bar-row .v{font-family:'Space Mono',monospace;font-size:12.5px;font-weight:700;text-align:right}
  /* heatmap */
  .heatwrap{overflow-x:auto;padding-bottom:6px}
  table.heat{border-collapse:collapse;font-size:11px;min-width:760px}
  table.heat th{font-family:'Space Mono',monospace;font-weight:400;color:var(--dim);font-size:9.5px;padding:4px 5px;text-align:center;vertical-align:bottom}
  table.heat th.rowh{text-align:right;white-space:nowrap;color:var(--ink);font-size:11px;padding-right:10px;font-weight:700}
  table.heat th.col{height:96px}
  table.heat th.col div{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;margin:0 auto}
  table.heat td{width:30px;height:26px;text-align:center;font-family:'Space Mono',monospace;font-size:9.5px;border:1px solid var(--paper);color:#0c0d0f;font-weight:700}
  table.heat td.avg{color:var(--ink);background:none!important;font-weight:700;font-size:11.5px;border-left:2px solid var(--line)}
  table.heat tr:hover td{outline:1px solid var(--ink)}
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;align-items:center}
  .controls input,.controls select{font-family:'IBM Plex Sans';font-size:13px;padding:9px 12px;border:1.5px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:8px}
  .controls input{flex:1;min-width:220px}
  .controls input:focus,.controls select:focus{outline:none;border-color:var(--teal)}
  .chip{font-family:'Space Mono',monospace;font-size:10.5px;padding:8px 11px;border:1.5px solid var(--line);background:var(--paper2);color:var(--dim);cursor:pointer;border-radius:8px;letter-spacing:.04em}
  .chip.on{border-color:var(--teal);color:var(--teal)}
  .count-line{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:10px}
  #cloud{width:100%;height:260px;display:block}
  .tasklist{display:grid;grid-template-columns:1fr;gap:8px}
  @media(min-width:760px){.tasklist{grid-template-columns:1fr 1fr}}
  .tcard{border:1.5px solid var(--line);border-radius:10px;background:var(--paper2);padding:11px 14px;display:flex;align-items:center;gap:10px}
  .tcard.b18{border-color:var(--orange)}
  .tcard .dot{width:9px;height:9px;border-radius:50%;flex:none}
  .tcard .tt{font-family:'Space Mono',monospace;font-size:12.5px;color:var(--ink)}
  .tcard .sub{font-size:11px;color:var(--dim)}
  .b18tag{margin-left:auto;font-family:'Space Mono',monospace;font-size:8.5px;color:var(--orange);border:1px solid var(--orange);border-radius:9px;padding:2px 7px;letter-spacing:.04em}
  mark{background:rgba(232,155,60,.35);color:inherit;padding:0 1px}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--blue)} footer code{color:var(--teal)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">18-TASK MULTI-TASK</div>
    <div class="kick">RLBench · The Robot Learning Benchmark</div>
    <h1>RLBench<br><em>Task Atlas</em></h1>
    <p class="lede">RLBench is the classic large-scale manipulation benchmark: <b>''' + str(NTASK) + r''' hand-designed task classes</b> on a 7-DoF Franka with four RGB-D cameras, each carrying multiple <b>variations</b> and template language. Most policies are <b>keypose</b> learners (predict next end-effector pose, not dense actions). The community converged on an <b>18-task multi-task split</b> &mdash; this atlas catalogs all ''' + str(NTASK) + r''' tasks and renders the canonical per-task leaderboard across nine methods, from Image-BC to RVT-2.</p>
    <div class="statbar">
      <div class="stat"><div class="num">''' + str(NTASK) + r'''</div><div class="lab">task classes</div></div>
      <div class="stat"><div class="num r">18</div><div class="lab">multi-task split</div></div>
      <div class="stat"><div class="num t">9</div><div class="lab">methods compared</div></div>
      <div class="stat"><div class="num">4</div><div class="lab">RGB-D cameras</div></div>
      <div class="stat"><div class="num">7</div><div class="lab">DoF Franka arm</div></div>
    </div>
  </header>

  <div class="note">
    <b>The 18-task benchmark.</b> PerAct / RVT / RVT-2 train one multi-task policy on 18 tasks from 100 demos each, evaluated over 25 episodes &times; multiple seeds. Cells below are <b>success %</b>. Tasks like <code>Insert Peg</code>, <code>Sort Shape</code> and <code>Stack Cups</code> are high-precision and stay hard even for the best policy; <code>Push Buttons</code> and <code>Meat off Grill</code> saturate. RLBench reports no single "language instruction" per task &mdash; each variation samples a template &mdash; so this atlas shows the task taxonomy and success matrix rather than an instruction pool.
  </div>

  <!-- 01 TAXONOMY -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>Task taxonomy</h2><span class="desc">''' + str(NTASK) + r''' tasks across 8 skill families</span></div>
    <div class="twocol">
      <div class="panel">
        <div class="lbl">TASKS PER FAMILY</div>
        <div class="donutwrap"><svg id="catdonut" viewBox="0 0 168 168"></svg><div class="dl" id="catLegend"></div></div>
      </div>
      <div class="panel">
        <div class="lbl">AVERAGE SUCCESS ON THE 18-TASK SPLIT · one multi-task policy · sorted</div>
        <div class="bar-wrap" id="avgBars"></div>
        <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">From the imitation floor (<b style="color:var(--ink)">~1%</b>, Image-BC) to <b style="color:var(--ink)">RVT-2 at 81.4%</b> &mdash; and RVT-2 is also the fastest (20.6 fps). The leap from PerAct (voxel) to RVT/RVT-2 (multi-view re-rendering) is the defining RLBench story.</div>
      </div>
    </div>
  </section>

  <!-- 02 HEATMAP -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>Per-task success matrix</h2><span class="desc">9 methods &times; 18 tasks · the signature RLBench heatmap</span></div>
    <div class="panel">
      <div class="lbl">SUCCESS % · darker red = harder · darker teal = solved · sorted by method average</div>
      <div class="heatwrap"><table class="heat" id="heat"></table></div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">Read down a column to see which tasks resist every method: <b style="color:var(--ink)">Insert Peg</b>, <b style="color:var(--ink)">Sort Shape</b> and <b style="color:var(--ink)">Stack Cups</b> stay red across the board, while <b style="color:var(--ink)">Push Buttons</b> is solved by almost everyone. Read across a row to see a method's profile.</div>
    </div>
  </section>

  <!-- 03 WORD CLOUD -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>Task vocabulary</h2><span class="desc">verbs &amp; objects tokenized from all ''' + str(NTASK) + r''' task names</span></div>
    <div class="panel"><canvas id="cloud"></canvas></div>
  </section>

  <!-- 04 CATALOG -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>Full task catalog</h2><span class="desc">all ''' + str(NTASK) + r''' task classes · search · filter · the 18-task split is flagged</span></div>
    <div class="panel">
      <div class="controls">
        <input id="search" placeholder="Search task… (e.g. drawer, stack, button, fridge)">
        <select id="catsel"><option value="">All families</option></select>
        <span class="chip" id="b18chip">&#9673; 18-task split only</span>
      </div>
      <div class="count-line" id="countLine"></div>
      <div class="tasklist" id="tasklist"></div>
    </div>
  </section>

  <footer>
    SOURCE · Task list: RLBench repo <code>rlbench/tasks/*.py</code> (James et al., <a href="https://arxiv.org/abs/1909.12271">arXiv 1909.12271</a>, RA-L 2020) &mdash; ''' + str(NTASK) + r''' task classes (the paper headlines "100 unique tasks"; each has multiple variations &amp; template language). Skill families are grouped from task names. Leaderboard verbatim from RVT-2, <a href="https://arxiv.org/abs/2406.08545">arXiv 2406.08545v1</a>, Table I (18-task multi-task split, 100 demos/task, 25 eval episodes): Image-BC, C2F-ARM-BC, HiveFormer, PolarNet, PerAct, RVT, Act3D, RVT-2. Numbers are success %; ± and per-method seed counts omitted for legibility.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const RECS=DATA.tasks, LB=DATA.lb;
const CATCOLORS=['--red','--orange','--teal','--blue','--green','--violet','#e08fb0','#7fd6c9'].map(c=>c.startsWith('--')?css(c):c);
const COLORMAP={};DATA.cats.forEach((c,i)=>COLORMAP[c.cat]=CATCOLORS[i%CATCOLORS.length]);

// donut
(function(){
  const segs=DATA.cats.map(c=>({n:c.cat,v:c.n,c:COLORMAP[c.cat]}));
  const tot=segs.reduce((s,x)=>s+x.v,0);let a0=-Math.PI/2,s='';const cx=84,cy=84,R=70,r=42;
  segs.forEach(seg=>{const a1=a0+seg.v/tot*6.283;const lp=(a1-a0)>Math.PI?1:0;
    const p=(a,rad)=>[cx+rad*Math.cos(a),cy+rad*Math.sin(a)];
    const A=p(a0,R),B=p(a1,R),C=p(a1,r),D=p(a0,r);
    s+=`<path d="M${A[0]} ${A[1]} A${R} ${R} 0 ${lp} 1 ${B[0]} ${B[1]} L${C[0]} ${C[1]} A${r} ${r} 0 ${lp} 0 ${D[0]} ${D[1]} Z" fill="${seg.c}" opacity="0.92"/>`;a0=a1;});
  s+=`<text x="84" y="80" text-anchor="middle" style="font-size:26px;fill:${css('--ink')};font-family:Fraunces">'''+str(NTASK)+r'''</text><text x="84" y="98" text-anchor="middle" style="font-size:9px;fill:${css('--dim')};font-family:Space Mono">TASKS</text>`;
  document.getElementById('catdonut').innerHTML=s;
  document.getElementById('catLegend').innerHTML=segs.map(seg=>`<span><i style="background:${seg.c}"></i>${seg.n}<b>${seg.v}</b></span>`).join('');
})();

// avg bars
(function(){
  const rows=LB.methods.slice().sort((a,b)=>b.avg-a.avg);
  const lerp=(a,b,t)=>a+(b-a)*t;
  function col(v){const t=v/100;const r=Math.round(lerp(224,63,t)),g=Math.round(lerp(83,182,t)),b=Math.round(lerp(58,168,t));return `rgb(${r},${g},${b})`;}
  document.getElementById('avgBars').innerHTML=rows.map(m=>
    `<div class="bar-row"><div class="name" title="${m.m}">${m.m}</div>
      <div class="track"><div class="fill" style="width:${m.avg}%;background:${col(m.avg)}"></div></div>
      <div class="v" style="color:${col(m.avg)}">${m.avg.toFixed(1)}</div></div>`).join('');
})();

// heatmap
(function(){
  const methods=LB.methods.slice().sort((a,b)=>b.avg-a.avg);
  const tasks=LB.tasks;
  const lerp=(a,b,t)=>a+(b-a)*t;
  function cell(v){const t=Math.max(0,Math.min(1,v/100));
    const r=Math.round(lerp(224,63,t)),g=Math.round(lerp(83,182,t)),b=Math.round(lerp(58,168,t));return `rgb(${r},${g},${b})`;}
  let h='<tr><th class="rowh">method</th>';
  tasks.forEach(t=>h+=`<th class="col"><div>${t}</div></th>`);
  h+='<th class="col"><div>AVG</div></th></tr>';
  methods.forEach(m=>{
    h+=`<tr><th class="rowh">${m.m}</th>`;
    m.s.forEach(v=>{h+=`<td style="background:${cell(v)}" title="${v}%">${v?Math.round(v):''}</td>`;});
    h+=`<td class="avg">${m.avg.toFixed(1)}</td></tr>`;
  });
  document.getElementById('heat').innerHTML=h;
})();

// word cloud
(function(){
  const cv=document.getElementById('cloud');const ctx=cv.getContext('2d');
  function draw(){
    const dpr=window.devicePixelRatio||1;const W=cv.clientWidth,H=260;
    cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const words=DATA.words;if(!words.length)return;const mx=words[0][1],mn=words[words.length-1][1];
    const pal=[css('--red'),css('--orange'),css('--teal'),css('--blue'),css('--green'),css('--ink')];
    const placed=[];
    words.forEach((w,i)=>{
      const fs=12+(w[1]-mn)/Math.max(1,(mx-mn))*38;
      ctx.font=`${fs>26?900:600} ${fs}px Fraunces, serif`;
      const tw=ctx.measureText(w[0]).width, th=fs;let tries=0,ok=false,x,y;
      while(tries++<400){x=Math.random()*(W-tw-10)+5;y=Math.random()*(H-th-6)+th;
        const box={x,y:y-th,w:tw,h:th};ok=true;
        for(const p of placed){if(box.x<p.x+p.w&&box.x+box.w>p.x&&box.y<p.y+p.h&&box.y+box.h>p.y){ok=false;break;}}
        if(ok)break;}
      if(!ok)return;placed.push({x,y:y-th,w:tw,h:th});
      ctx.fillStyle=pal[i%pal.length];ctx.fillText(w[0],x,y);});
  }
  draw();let t;window.addEventListener('resize',()=>{clearTimeout(t);t=setTimeout(draw,200);});
})();

// catalog
(function(){
  const sel=document.getElementById('catsel');
  DATA.cats.forEach(c=>sel.innerHTML+=`<option value="${c.cat}">${c.cat} (${c.n})</option>`);
  const state={b18:false};
  const chip=document.getElementById('b18chip');
  chip.onclick=()=>{state.b18=!state.b18;chip.classList.toggle('on',state.b18);render();};
  function render(){
    const q=document.getElementById('search').value.toLowerCase().trim();
    const cat=sel.value;
    let rows=RECS.filter(t=>(!q||t.task.includes(q)||t.label.toLowerCase().includes(q))&&(!cat||t.category===cat)&&(!state.b18||t.bench18));
    const hl=s=>q?s.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>'):s;
    document.getElementById('countLine').textContent=`Showing ${rows.length} / ${RECS.length} tasks`;
    document.getElementById('tasklist').innerHTML=rows.map(t=>
      `<div class="tcard ${t.bench18?'b18':''}"><span class="dot" style="background:${COLORMAP[t.category]}"></span>
        <div><div class="tt">${hl(t.label)}</div><div class="sub">${t.category}</div></div>
        ${t.bench18?'<span class="b18tag">18-TASK</span>':''}</div>`).join('');
  }
  document.getElementById('search').addEventListener('input',render);
  sel.addEventListener('change',render);
  render();
})();
</script>
'''
open(f'{HERE}/rlbench_dashboard.html','w').write(HTML)
print('wrote rlbench_dashboard.html', len(HTML),'bytes')
