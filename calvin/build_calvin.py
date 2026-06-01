#!/usr/bin/env python3
"""Builds calvin_tasks.csv and calvin_dashboard.html (blueprint style) from calvin_tasks.json."""
import json, csv, re, html

HERE = __file__.rsplit('/', 1)[0]
recs = json.load(open(f'{HERE}/calvin_tasks.json'))

# ---- clean semantic categories / interaction type / object ----
def categorize(t):
    if t.startswith('rotate_'):      return 'Rotate block', 'rotate'
    if t.startswith('push_') and '_block_' in t: return 'Push block', 'push'
    if t in ('move_slider_left','move_slider_right'): return 'Slide door', 'slide'
    if t in ('open_drawer','close_drawer'):           return 'Open / close drawer', 'articulate'
    if t.startswith('lift_'):        return 'Lift block', 'pick'
    if t.startswith('place_'):       return 'Place block', 'place'
    if t == 'push_into_drawer':      return 'Sweep into drawer', 'push'
    if t in ('stack_block','unstack_block'): return 'Stack / unstack', 'stack'
    if 'lightbulb' in t:             return 'Lightbulb switch', 'toggle'
    if 'led' in t:                   return 'LED button', 'press'
    return 'Other', 'other'

COLORS = {  # block color extracted from task name
    'red':'red','blue':'blue','pink':'pink'
}
def obj_color(t):
    for c in COLORS:
        if c in t: return c
    return ''

for r in recs:
    cat, skill = categorize(r['task'])
    r['cat'] = cat
    r['skill'] = skill
    r['color'] = obj_color(r['task'])

# ---- write CSV ----
with open(f'{HERE}/calvin_tasks.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['task','category','skill','block_color','n_instructions','canonical_instruction','all_instructions'])
    for r in recs:
        w.writerow([r['task'], r['cat'], r['skill'], r['color'], r['n_instr'],
                    r['canonical'], ' | '.join(r['instructions'])])
print(f'wrote calvin_tasks.csv ({len(recs)} tasks)')

# ---- leaderboards (verbatim from origin papers) ----
# ABCD->D : GR-1 paper (arXiv 2312.13139v2), Table; all rows trained on A,B,C,D tested on D.
# ABC->D  : 3D Diffuser Actor paper (arXiv 2402.10885v2), Table IV; zero-shot to unseen env D.
LB = {
  "ABCD->D": {
     "note": "Train on environments A,B,C,D · test on D · 1000 instruction chains. Source: GR-1, arXiv 2312.13139v2.",
     "rows": [
        {"model":"MCIL",   "seq":[37.3,2.7,0.2,0.0,0.0],  "avg":0.40},
        {"model":"RT-1",   "seq":[84.4,61.7,43.8,32.3,22.7],"avg":2.45},
        {"model":"MT-R3M", "seq":[75.2,52.7,37.5,25.8,16.3],"avg":2.08},
        {"model":"HULC",   "seq":[88.9,73.3,58.7,47.5,38.3],"avg":3.06},
        {"model":"GR-1",   "seq":[94.9,89.6,84.4,78.9,73.1],"avg":4.21},
     ]},
  "ABC->D": {
     "note": "Zero-shot: train on A,B,C · test on UNSEEN env D · 1000 instruction chains. Source: 3D Diffuser Actor, arXiv 2402.10885v2, Table IV.",
     "rows": [
        {"model":"MCIL",   "seq":[30.4,1.3,0.2,0.0,0.0],  "avg":0.31},
        {"model":"HULC",   "seq":[41.8,16.5,5.7,1.9,1.1], "avg":0.67},
        {"model":"RT-1",   "seq":[53.3,22.2,9.4,3.8,1.3], "avg":0.90},
        {"model":"RoboFlamingo","seq":[82.4,61.9,46.6,33.1,23.5],"avg":2.48},
        {"model":"SuSIE",  "seq":[87.0,69.0,49.0,38.0,26.0],"avg":2.69},
        {"model":"GR-1",   "seq":[85.4,71.2,59.6,49.7,40.1],"avg":3.06},
        {"model":"3D Diffuser Actor","seq":[92.2,78.7,63.9,51.2,41.2],"avg":3.27},
     ]},
}

# ---- per-category aggregation ----
from collections import OrderedDict, Counter
cats = OrderedDict()
for r in recs:
    cats.setdefault(r['cat'], {'n':0,'instr':0})
    cats[r['cat']]['n'] += 1
    cats[r['cat']]['instr'] += r['n_instr']

# ---- word frequencies (placeholders/colors kept; stopwords dropped) ----
STOP = set("the a an to it of on in and then is into so that with at by from your you up down".split())
wc = Counter()
for r in recs:
    for ins in r['instructions']:
        for tok in re.findall(r"[a-z]+", ins.lower()):
            if tok in STOP or len(tok) < 3: continue
            wc[tok]+=1
words = wc.most_common(70)

DATA = {"tasks": recs, "lb": LB,
        "cats": [{"cat":k,"n":v['n'],"instr":v['instr']} for k,v in cats.items()],
        "words": words}

total_instr = sum(r['n_instr'] for r in recs)
data_json = json.dumps(DATA, separators=(',',':'))

# =========================== HTML ===========================
HTML = r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CALVIN · Language &amp; Long-Horizon Chaining Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0b0e14; --paper2:#11151e; --card:#141925; --ink:#e9ecf2; --dim:#828 aa; --line:#222a39;
    --blue:#5b8def; --cyan:#46c4c0; --amber:#e0a93b; --pink:#d27ab0; --green:#74c476; --rust:#e0703a;
  }
  :root{--dim:#838ba3}
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(91,141,239,.10), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(70,196,192,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--blue)}
  .top:after{right:30px;border:1.5px solid var(--cyan)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--blue);border:1px solid var(--blue);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--amber)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--blue),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:76ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.b{color:var(--blue)} .stat .num.c{color:var(--cyan)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--blue);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .twocol{display:grid;gap:18px}
  @media(min-width:880px){.twocol{grid-template-columns:1fr 1fr}}
  .twocol.bias{grid-template-columns:1fr}
  @media(min-width:880px){.twocol.bias{grid-template-columns:.85fr 1.15fr}}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .donutwrap{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
  #catdonut{flex:0 0 168px}
  .dl{display:flex;flex-direction:column;gap:8px;font-size:12.5px}
  .dl span{display:flex;align-items:center;gap:9px}
  .dl i{width:12px;height:12px;border-radius:2px;flex:none}
  .dl b{font-family:'Space Mono',monospace;color:var(--dim);font-weight:400;margin-left:auto;padding-left:12px}
  .barscroll{max-height:520px;overflow-y:auto;padding-right:8px}
  .bar-wrap{display:flex;flex-direction:column;gap:6px}
  .bar-row{display:grid;grid-template-columns:182px 1fr 34px;align-items:center;gap:12px}
  .bar-row .name{font-size:12px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .track{height:16px;background:var(--paper);border:1px solid var(--line);border-radius:3px;overflow:hidden;position:relative;background-image:repeating-linear-gradient(90deg,transparent,transparent calc(25% - 1px),var(--line) calc(25% - 1px),var(--line) 25%)}
  .fill{height:100%;position:relative;z-index:1;transition:width .5s cubic-bezier(.2,.8,.2,1)}
  .bar-row .v{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;text-align:right;color:var(--dim)}
  /* chaining decay chart */
  #decay{width:100%;height:340px;display:block}
  .dx{font-family:'Space Mono',monospace;font-size:10px;fill:var(--dim)}
  .legend{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:12px}
  .legend .li{display:flex;align-items:center;gap:7px;font-size:12px;color:var(--ink);cursor:pointer;font-family:'Space Mono',monospace}
  .legend .li .sw{width:16px;height:3px;border-radius:2px}
  .legend .li.off{opacity:.32}
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;align-items:center}
  .controls input,.controls select{font-family:'IBM Plex Sans';font-size:13px;padding:9px 12px;border:1.5px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:8px}
  .controls input{flex:1;min-width:220px}
  .controls input:focus,.controls select:focus{outline:none;border-color:var(--cyan)}
  .chip{font-family:'Space Mono',monospace;font-size:10.5px;padding:8px 11px;border:1.5px solid var(--line);background:var(--paper2);color:var(--dim);cursor:pointer;border-radius:8px;letter-spacing:.04em}
  .chip.on{border-color:var(--cyan);color:var(--cyan)}
  .chip.setb.on{border-color:var(--blue);color:var(--blue)}
  .count-line{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:10px}
  #cloud{width:100%;height:300px;display:block}
  .tasklist{display:flex;flex-direction:column;gap:10px}
  .tcard{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);overflow:hidden}
  .tcard>summary{cursor:pointer;list-style:none;padding:14px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
  .tcard>summary::-webkit-details-marker{display:none}
  .tcard>summary:after{content:"\25B8";margin-left:auto;color:var(--cyan);transition:transform .2s}
  .tcard[open]>summary:after{transform:rotate(90deg)}
  .tcard .title{font-family:'Space Mono',monospace;font-weight:700;font-size:14px;color:var(--ink)}
  .catpill{font-family:'Space Mono',monospace;font-size:9.5px;padding:3px 9px;border-radius:11px;border:1px solid var(--line);color:var(--dim);letter-spacing:.03em}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block}
  .cnt-pill{font-family:'Space Mono',monospace;font-size:10px;padding:3px 9px;border-radius:11px;border:1px solid var(--line);color:var(--dim)}
  .cnt-pill b{color:var(--amber)}
  .tcard .body{padding:0 18px 16px;border-top:1px solid var(--line)}
  .tcard .desc{font-size:13.5px;color:var(--ink);line-height:1.5;margin:14px 0 6px}
  .tcard .desc:before{content:"canonical \2014 ";font-family:'Space Mono',monospace;font-size:9px;color:var(--amber);text-transform:uppercase;letter-spacing:.06em}
  .samp-h{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;margin:12px 0 6px}
  .samp{display:flex;flex-direction:column;gap:4px}
  .samp .row{font-size:12.5px;color:var(--ink);line-height:1.4;padding-left:14px;position:relative}
  .samp .row:before{content:"\203A";position:absolute;left:2px;color:var(--line)}
  mark{background:rgba(224,169,59,.3);color:inherit;padding:0 1px}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--blue)}
  footer code{color:var(--cyan)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">D / ABC / ABCD &rarr; D</div>
    <div class="kick">CALVIN · Language-Conditioned Long-Horizon Manipulation</div>
    <h1>CALVIN<br><em>Chaining Atlas</em></h1>
    <p class="lede">CALVIN (Composing Actions from Language and Vision) is a tabletop benchmark whose signature is the <b>long-horizon language chain</b>: a policy must complete <b>five language instructions in a row</b> from raw RGB-D + proprioception, re-grounding a fresh natural-language command at each step. This atlas covers the <b>34 tasks</b> and <b>''' + str(total_instr) + r''' crowd-sourced instructions</b>, the four play environments <b>A&middot;B&middot;C&middot;D</b>, and the official chaining leaderboard &mdash; where the real story is how fast success <b>decays</b> from task&nbsp;1 to task&nbsp;5, and how far it falls on an <b>unseen environment</b>.</p>
    <div class="statbar">
      <div class="stat"><div class="num">34</div><div class="lab">manipulation tasks</div></div>
      <div class="stat"><div class="num b" id="s-instr">0</div><div class="lab">language instructions</div></div>
      <div class="stat"><div class="num c">4</div><div class="lab">play environments</div></div>
      <div class="stat"><div class="num">5</div><div class="lab">tasks chained / rollout</div></div>
      <div class="stat"><div class="num">1000</div><div class="lab">eval instruction chains</div></div>
    </div>
  </header>

  <div class="note">
    <b>How CALVIN scores.</b> At eval, the agent is given a sequence of 5 instructions and must finish each before the next is revealed &mdash; if it fails one, the chain stops. The headline metric is <b>average rollout length</b> (mean tasks completed in a row, out of 5). The standard splits: <code>D&rarr;D</code> (single env), <code>ABCD&rarr;D</code> (train all, test D), and the hard <code>ABC&rarr;D</code> (train A,B,C &mdash; test the <b>unseen</b> environment D). Instructions are real human annotations, so each task carries many paraphrases (here <code>place_in_slider</code> has 20, the <code>push_*</code> tasks 9 each).
  </div>

  <!-- 01 TAXONOMY -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>Task taxonomy</h2><span class="desc">34 tasks across 10 interaction families</span></div>
    <div class="twocol bias">
      <div class="panel">
        <div class="lbl">TASKS PER FAMILY</div>
        <div class="donutwrap"><svg id="catdonut" viewBox="0 0 168 168"></svg><div class="dl" id="catLegend"></div></div>
        <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">Three block colors (<span style="color:#e0703a">red</span>, <span style="color:#5b8def">blue</span>, <span style="color:#d27ab0">pink</span>) multiply the manipulation verbs &mdash; rotate, push, lift, place &mdash; while a slider door, drawer, lightbulb and LED add articulation and toggle skills.</div>
      </div>
      <div class="panel">
        <div class="lbl">INSTRUCTIONS PER TASK · how many human paraphrases each task carries · sorted</div>
        <div class="barscroll"><div class="bar-wrap" id="instrBars"></div></div>
      </div>
    </div>
  </section>

  <!-- 02 CHAINING DECAY -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>Long-horizon chaining decay</h2><span class="desc">success vs. tasks-in-a-row · the signature CALVIN curve</span></div>
    <div class="panel">
      <div class="controls" style="margin-bottom:6px">
        <span class="chip setb on" data-set="ABCD->D" id="setMulti">&#9673; ABCD &rarr; D (seen)</span>
        <span class="chip setb" data-set="ABC->D" id="setZero">&#9711; ABC &rarr; D (zero-shot, unseen env)</span>
      </div>
      <div class="lbl" id="decayNote"></div>
      <svg id="decay" viewBox="0 0 720 340"></svg>
      <div class="legend" id="decayLegend"></div>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)" id="decayCaption"></div>
    </div>
  </section>

  <!-- 03 AVG LENGTH LEADERBOARD -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>Average rollout length</h2><span class="desc">mean tasks completed in a row · out of 5</span></div>
    <div class="twocol">
      <div class="panel">
        <div class="lbl">ABCD &rarr; D &nbsp;·&nbsp; trained on all four envs</div>
        <div class="bar-wrap" id="avgMulti"></div>
      </div>
      <div class="panel">
        <div class="lbl">ABC &rarr; D &nbsp;·&nbsp; zero-shot to unseen env D</div>
        <div class="bar-wrap" id="avgZero"></div>
      </div>
    </div>
    <div class="note" style="border-left-color:var(--rust)">The same models that chain ~4&ndash;5 tasks on a seen environment can <b>collapse on the unseen one</b>: HULC falls from <b>3.06</b> to <b>0.67</b>, and even GR-1 drops from <b>4.21</b> to <b>3.06</b>. CALVIN's <code>ABC&rarr;D</code> split is precisely a visual-generalization stress test &mdash; reporting <code>ABCD&rarr;D</code> alone hides it.</div>
  </section>

  <!-- 04 WORD CLOUD -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>Instruction vocabulary</h2><span class="desc">tokenized from all ''' + str(total_instr) + r''' human instructions</span></div>
    <div class="panel"><canvas id="cloud"></canvas></div>
  </section>

  <!-- 05 CATALOG -->
  <section>
    <div class="sec-h"><span class="idx">05</span><h2>Task &amp; instruction catalog</h2><span class="desc">expand a task to see every human phrasing · search · sort</span></div>
    <div class="panel">
      <div class="controls">
        <input id="search" placeholder="Search task, family, or instruction… (e.g. drawer, rotate, slider)">
        <select id="sortsel"><option value="cat">Sort: by family</option><option value="az">Sort: A–Z</option><option value="most">Sort: most paraphrases</option></select>
      </div>
      <div class="count-line" id="countLine"></div>
      <div class="tasklist" id="tasklist"></div>
    </div>
  </section>

  <footer>
    SOURCE · Tasks &amp; instructions: CALVIN repo <code>calvin_models/conf/annotations/new_playtable.yaml</code> (Mees et al., <a href="https://arxiv.org/abs/2112.03227">arXiv 2112.03227</a>, RA-L 2022) &mdash; 34 tasks, ''' + str(total_instr) + r''' human instructions. Leaderboard numbers verbatim: <code>ABCD&rarr;D</code> from GR-1 (<a href="https://arxiv.org/abs/2312.13139">arXiv 2312.13139v2</a>); <code>ABC&rarr;D</code> from 3D Diffuser Actor (<a href="https://arxiv.org/abs/2402.10885">arXiv 2402.10885v2</a>, Table IV). Avg length = mean number of instructions completed consecutively (max 5) over 1000 eval chains. CALVIN provides no per-task success breakdown, so only the chaining metric is shown. Official leaderboard: <a href="http://calvin.cs.uni-freiburg.de/">calvin.cs.uni-freiburg.de</a>.
  </footer>
</div>
<script>
const DATA = ''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const TASKS=DATA.tasks, LB=DATA.lb;
const CATCOLORS=['--blue','--cyan','--amber','--green','--pink','--rust','#9a7bff','#e08fb0','#7fd6c9'].map(c=>c.startsWith('--')?css(c):c);
const COLORMAP={};DATA.cats.forEach((c,i)=>COLORMAP[c.cat]=CATCOLORS[i%CATCOLORS.length]);
const BLOCKCOL={red:'#e0703a',blue:'#5b8def',pink:'#d27ab0'};

document.getElementById('s-instr').textContent=TASKS.reduce((s,t)=>s+t.n_instr,0);

// donut
(function(){
  const segs=DATA.cats.map(c=>({n:c.cat,v:c.n,c:COLORMAP[c.cat]}));
  const tot=segs.reduce((s,x)=>s+x.v,0); let a0=-Math.PI/2,s='';const cx=84,cy=84,R=70,r=42;
  segs.forEach(seg=>{const a1=a0+seg.v/tot*6.283;const lp=(a1-a0)>Math.PI?1:0;
    const p=(a,rad)=>[cx+rad*Math.cos(a),cy+rad*Math.sin(a)];
    const A=p(a0,R),B=p(a1,R),C=p(a1,r),D=p(a0,r);
    s+=`<path d="M${A[0]} ${A[1]} A${R} ${R} 0 ${lp} 1 ${B[0]} ${B[1]} L${C[0]} ${C[1]} A${r} ${r} 0 ${lp} 0 ${D[0]} ${D[1]} Z" fill="${seg.c}" opacity="0.92"/>`;a0=a1;});
  s+=`<text x="84" y="80" text-anchor="middle" class="dx" style="font-size:26px;fill:${css('--ink')};font-family:Fraunces">34</text><text x="84" y="98" text-anchor="middle" class="dx">TASKS</text>`;
  document.getElementById('catdonut').innerHTML=s;
  document.getElementById('catLegend').innerHTML=segs.map(seg=>`<span><i style="background:${seg.c}"></i>${seg.n}<b>${seg.v}</b></span>`).join('');
})();

// instructions-per-task bars
(function(){
  const rows=TASKS.slice().sort((a,b)=>b.n_instr-a.n_instr);
  const mx=Math.max(...rows.map(t=>t.n_instr));
  document.getElementById('instrBars').innerHTML=rows.map(t=>{
    const col=COLORMAP[t.cat];
    return `<div class="bar-row"><div class="name" title="${t.task}">${t.task}</div>
      <div class="track"><div class="fill" style="width:${t.n_instr/mx*100}%;background:${col}"></div></div>
      <div class="v">${t.n_instr}</div></div>`;}).join('');
})();

// chaining decay chart
const decayState={set:'ABCD->D',hidden:new Set()};
const MODELCOLORS=['#5b8def','#46c4c0','#e0a93b','#74c476','#d27ab0','#e0703a','#9a7bff'];
function modelColor(i){return MODELCOLORS[i%MODELCOLORS.length];}
function renderDecay(){
  const set=LB[decayState.set];const rows=set.rows;
  const W=720,H=340,padL=52,padR=18,padT=18,padB=46;
  const x=i=>padL+(i)*(W-padL-padR)/4;            // i=0..4 -> tasks 1..5
  const y=v=>padT+(100-v)*(H-padT-padB)/100;
  let s='';
  // grid
  for(let g=0;g<=100;g+=20){const yy=y(g);s+=`<line x1="${padL}" y1="${yy}" x2="${W-padR}" y2="${yy}" stroke="${css('--line')}" stroke-width="1"/>`;s+=`<text x="${padL-8}" y="${yy+3}" text-anchor="end" class="dx">${g}</text>`;}
  for(let i=0;i<5;i++){s+=`<text x="${x(i)}" y="${H-padB+18}" text-anchor="middle" class="dx">${i+1} task${i?'s':''}</text>`;}
  s+=`<text x="${(padL+W-padR)/2}" y="${H-6}" text-anchor="middle" class="dx" style="letter-spacing:.1em">TASKS COMPLETED IN A ROW &rarr;</text>`;
  rows.forEach((r,mi)=>{
    if(decayState.hidden.has(r.model))return;
    const col=modelColor(mi);
    let d=r.seq.map((v,i)=>`${i?'L':'M'}${x(i)} ${y(v)}`).join(' ');
    s+=`<path d="${d}" fill="none" stroke="${col}" stroke-width="2.5" stroke-linejoin="round" opacity="0.95"/>`;
    r.seq.forEach((v,i)=>{s+=`<circle cx="${x(i)}" cy="${y(v)}" r="3.4" fill="${col}"/>`;});
    // label at end
    s+=`<text x="${x(4)+5}" y="${y(r.seq[4])+3}" class="dx" style="fill:${col};font-size:9px">${r.model}</text>`;
  });
  document.getElementById('decay').innerHTML=s;
  document.getElementById('decayLegend').innerHTML=rows.map((r,mi)=>
    `<span class="li ${decayState.hidden.has(r.model)?'off':''}" data-m="${r.model}"><span class="sw" style="background:${modelColor(mi)}"></span>${r.model} · ${r.avg.toFixed(2)}</span>`).join('');
  document.getElementById('decayNote').textContent=set.note;
  document.querySelectorAll('#decayLegend .li').forEach(el=>el.onclick=()=>{
    const m=el.dataset.m; if(decayState.hidden.has(m))decayState.hidden.delete(m);else decayState.hidden.add(m);renderDecay();});
  const cap=decayState.set==='ABCD->D'
    ? 'On the seen environment, GR-1 holds <b style="color:var(--ink)">73%</b> success even after five chained instructions; older baselines like MCIL effectively die after task&nbsp;1.'
    : 'On the <b style="color:var(--ink)">unseen</b> environment, every curve sags harder &mdash; the gap between the best (3D Diffuser Actor) and the imitation baselines (HULC, MCIL) widens at every additional step.';
  document.getElementById('decayCaption').innerHTML=cap;
}
document.querySelectorAll('.chip.setb').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip.setb').forEach(x=>x.classList.remove('on'));c.classList.add('on');
  decayState.set=c.dataset.set;decayState.hidden.clear();renderDecay();});
renderDecay();

// avg length bars
function avgBars(elId,setKey,col){
  const rows=LB[setKey].rows.slice().sort((a,b)=>b.avg-a.avg);
  document.getElementById(elId).innerHTML=rows.map(r=>
    `<div class="bar-row"><div class="name">${r.model}</div>
      <div class="track"><div class="fill" style="width:${r.avg/5*100}%;background:${col}"></div></div>
      <div class="v" style="color:${col}">${r.avg.toFixed(2)}</div></div>`).join('');
}
avgBars('avgMulti','ABCD->D',css('--blue'));
avgBars('avgZero','ABC->D',css('--rust'));

// word cloud
(function(){
  const cv=document.getElementById('cloud');const ctx=cv.getContext('2d');
  function draw(){
    const dpr=window.devicePixelRatio||1;const W=cv.clientWidth,H=300;
    cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const words=DATA.words;const mx=words[0][1],mn=words[words.length-1][1];
    const pal=[css('--blue'),css('--cyan'),css('--amber'),css('--green'),css('--pink'),css('--ink')];
    const placed=[];
    words.forEach((w,i)=>{
      const fs=12+(w[1]-mn)/(mx-mn)*40;
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
const ORDER=DATA.cats.map(c=>c.cat);
function renderCatalog(){
  const q=document.getElementById('search').value.toLowerCase().trim();
  const sort=document.getElementById('sortsel').value;
  let rows=TASKS.filter(t=> !q || t.task.includes(q)||t.cat.toLowerCase().includes(q)||t.instructions.some(i=>i.toLowerCase().includes(q)));
  if(sort==='az')rows=rows.slice().sort((a,b)=>a.task.localeCompare(b.task));
  else if(sort==='most')rows=rows.slice().sort((a,b)=>b.n_instr-a.n_instr);
  else rows=rows.slice().sort((a,b)=>ORDER.indexOf(a.cat)-ORDER.indexOf(b.cat)||a.task.localeCompare(b.task));
  const hl=s=>q?s.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig'),'<mark>$1</mark>'):s;
  document.getElementById('countLine').textContent=`Showing ${rows.length} / ${TASKS.length} tasks · ${rows.reduce((s,t)=>s+t.n_instr,0)} instructions`;
  document.getElementById('tasklist').innerHTML=rows.map(t=>{
    const col=COLORMAP[t.cat];const bc=t.block_color||t.color;const bdot=BLOCKCOL[bc];
    return `<details class="tcard"><summary>
      <span class="dot" style="background:${col}"></span>
      <span class="title">${hl(t.task)}</span>
      ${bdot?`<span class="dot" style="background:${bdot}" title="${bc} block"></span>`:''}
      <span class="catpill">${t.cat}</span>
      <span class="cnt-pill"><b>${t.n_instr}</b> phrasings</span></summary>
      <div class="body">
        <div class="desc">${hl(t.canonical)}</div>
        <div class="samp-h">all human paraphrases</div>
        <div class="samp">${t.instructions.map(i=>`<div class="row">${hl(i)}</div>`).join('')}</div>
      </div></details>`;}).join('');
}
document.getElementById('search').addEventListener('input',renderCatalog);
document.getElementById('sortsel').addEventListener('change',renderCatalog);
renderCatalog();
</script>
'''

# fix accidental space in --dim token (CSS), keep clean
HTML = HTML.replace('#828 aa','#838ba3')
open(f'{HERE}/calvin_dashboard.html','w').write(HTML)
print(f'wrote calvin_dashboard.html ({len(HTML)} bytes)')
