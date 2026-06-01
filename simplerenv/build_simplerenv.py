#!/usr/bin/env python3
"""Builds simplerenv_tasks.csv + simplerenv_dashboard.html (blueprint style).
Data verbatim from SpatialVLA README result tables (arXiv 2501.15830, RSS 2025),
which consolidate SimplerEnv real-to-sim results across policies."""
import json, csv
HERE = __file__.rsplit('/', 1)[0]

# ---- Google Robot (Visual Matching + Variant Aggregation), per-task + avg ----
# tasks: Pick Coke Can, Move Near, Open/Close Drawer  (Open-Top-Drawer-&-Place-Apple omitted by most papers)
GTASKS=['Pick Coke Can','Move Near','Open/Close Drawer']
def n(x): return None if x in ('--','') else float(x.replace('%',''))
GOOGLE=[
 # model, [VM per-task], VM#avg, [VA per-task], VA#avg, both?
 ('RT-1 (Begin)',     [2.7,5.0,13.9],6.8,  [2.2,4.0,6.9],4.2),
 ('RT-1 (15%)',       [71.0,35.4,56.5],60.2,[81.3,44.6,26.7],56.2),
 ('RT-1 (Converged)', [85.7,44.2,73.0],74.6,[89.8,50.0,32.3],63.3),
 ('HPT',              [56.0,60.0,24.0],46.0,[None,None,31.0],45.0),
 ('TraceVLA',         [28.0,53.7,57.0],42.0,[60.0,56.4,29.4],39.6),
 ('RT-1-X',           [56.7,31.7,59.7],53.4,[49.0,32.3,35.3],None),
 ('RT-2-X',           [78.7,77.9,25.0],60.7,[82.3,79.2,None],None),
 ('Octo-Base',        [17.0,4.2,22.7],16.8, [0.6,3.1,1.1],1.1),
 ('OpenVLA',          [16.3,46.2,35.6],27.7,[54.5,47.7,17.7],39.8),
 ('RoboVLM (zero-shot)',[72.7,66.3,26.8],56.3,[68.3,56.0,8.5],46.3),
 ('RoboVLM (fine-tune)',[77.3,61.7,43.5],63.4,[75.6,60.0,10.6],51.3),
 ('SpatialVLA (zero-shot)',[81.0,69.6,59.3],71.9,[89.5,71.7,36.2],68.8),
 ('SpatialVLA (fine-tune)',[86.0,77.9,57.4],75.1,[88.0,72.7,41.8],70.7),
]
# ---- WidowX / Bridge, per-task Success (grasp sub-metric dropped for heatmap) + overall ----
WTASKS=['Put Spoon on Towel','Put Carrot on Plate','Stack Green on Yellow','Put Eggplant in Basket']
WIDOWX=[
 ('RT-1-X',   [0.0,4.2,0.0,0.0],1.1),
 ('Octo-Base',[12.5,8.3,0.0,43.1],16.0),
 ('Octo-Small',[47.2,9.7,4.2,56.9],30.0),
 ('OpenVLA',  [0.0,0.0,0.0,4.1],1.0),
 ('RoboVLM (zero-shot)',[20.8,25.0,8.3,0.0],13.5),
 ('RoboVLM (fine-tune)',[29.2,25.0,12.5,58.3],31.3),
 ('SpatialVLA (zero-shot)',[20.8,20.8,25.0,70.8],34.4),
 ('SpatialVLA (fine-tune)',[16.7,25.0,29.2,100.0],42.7),
]

# embodiment-gap: models present in BOTH tables -> (google VM avg, widowx overall)
gmap={m:vm for (m,_,vm,_,_) in [(g[0],None,g[2],None,None) for g in GOOGLE]}
wmap={m:ov for (m,_,ov) in WIDOWX}
GAP=[]
for m in wmap:
    if m in gmap and gmap[m] is not None:
        GAP.append({'m':m,'g':gmap[m],'w':wmap[m]})

# ---- CSV ----
with open(f'{HERE}/simplerenv_tasks.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['robot','task','eval_setups'])
    for t in GTASKS: w.writerow(['Google Robot',t,'visual_matching;variant_aggregation'])
    for t in WTASKS: w.writerow(['WidowX (Bridge)',t,'visual_matching'])
print('wrote simplerenv_tasks.csv')

GOOGLE_J=[{'m':m,'vm':vm,'vmavg':va,'va':vapt,'vaavg':vaa} for (m,vm,va,vapt,vaa) in GOOGLE]
WIDOWX_J=[{'m':m,'s':s,'avg':a} for (m,s,a) in WIDOWX]
DATA={'gtasks':GTASKS,'wtasks':WTASKS,'google':GOOGLE_J,'widowx':WIDOWX_J,'gap':GAP}
data_json=json.dumps(DATA,separators=(',',':'))

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SimplerEnv · Real-to-Sim VLA Evaluation Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0a0c11; --paper2:#11141b; --card:#141821; --ink:#e8ebf1; --dim:#828a99; --line:#212835;
    --google:#5b8def; --widowx:#e08a3c; --teal:#3fb6a8; --amber:#e0a93b; --green:#5bbf6a; --rust:#e0533a; --violet:#9a7bff;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(91,141,239,.10), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(224,138,60,.08), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--google)}
  .top:after{right:30px;border:1.5px solid var(--widowx)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--google);border:1px solid var(--google);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--amber)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--google),var(--widowx));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.g{color:var(--google)} .stat .num.w{color:var(--widowx)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--google);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--teal)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .setupwrap{display:grid;gap:18px}
  @media(min-width:760px){.setupwrap{grid-template-columns:1fr 1fr}}
  .setup{border:1.5px solid var(--line);border-radius:12px;padding:18px;background:var(--paper2)}
  .setup h3{font-family:'Fraunces',serif;font-size:20px;margin:0 0 4px}
  .setup .rb{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
  .setup ul{margin:0;padding-left:18px} .setup li{font-size:13px;color:var(--ink);margin:5px 0;line-height:1.4}
  /* gap chart */
  #gap{width:100%;height:360px;display:block}
  .gx{font-family:'Space Mono',monospace;font-size:10px;fill:var(--dim)}
  /* heatmap */
  .heatwrap{overflow-x:auto}
  table.heat{border-collapse:collapse;font-size:11px;width:100%;min-width:520px}
  table.heat th{font-family:'Space Mono',monospace;font-weight:400;color:var(--dim);font-size:10px;padding:6px;text-align:center;vertical-align:bottom}
  table.heat th.rowh{text-align:right;color:var(--ink);font-size:11.5px;white-space:nowrap;padding-right:10px}
  table.heat td{height:30px;text-align:center;font-family:'Space Mono',monospace;font-size:11px;border:1px solid var(--paper);color:#0a0c11;font-weight:700}
  table.heat td.na{background:var(--paper2)!important;color:var(--line)}
  table.heat td.avg{color:var(--ink);background:none!important;border-left:2px solid var(--line);font-size:12px}
  table.heat tr:hover td{outline:1px solid var(--ink)}
  .chip{font-family:'Space Mono',monospace;font-size:10.5px;padding:8px 11px;border:1.5px solid var(--line);background:var(--paper2);color:var(--dim);cursor:pointer;border-radius:8px;letter-spacing:.04em;margin-right:8px}
  .chip.on{border-color:var(--google);color:var(--google)}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--google)} footer code{color:var(--teal)}
</style>
<div class="shell">
  <header class="top">
    <div class="stamp">REAL &rarr; SIM</div>
    <div class="kick">SimplerEnv · Real-to-Sim Manipulation Policy Evaluation</div>
    <h1>SimplerEnv<br><em>Real-to-Sim Atlas</em></h1>
    <p class="lede">SimplerEnv evaluates real-robot manipulation policies <b>in simulation</b> by closing the visual gap to two real setups &mdash; Google's <b style="color:var(--google)">RT-1 robot</b> and the <b style="color:var(--widowx)">WidowX + Bridge</b> arm &mdash; so that sim success <i>predicts</i> real success without running hardware. Two eval modes: <b>Visual Matching</b> (overlay real backgrounds, match textures) and <b>Variant Aggregation</b> (sweep lighting / background / distractors). This atlas renders the per-task success matrices and exposes the headline finding: <b>capability does not transfer across embodiments</b>.</p>
    <div class="statbar">
      <div class="stat"><div class="num g">2</div><div class="lab">real robot setups</div></div>
      <div class="stat"><div class="num w">7</div><div class="lab">manipulation tasks</div></div>
      <div class="stat"><div class="num">2</div><div class="lab">eval modes · VM / VA</div></div>
      <div class="stat"><div class="num">13</div><div class="lab">policies compared</div></div>
      <div class="stat"><div class="num">~137</div><div class="lab">configurations</div></div>
    </div>
  </header>

  <div class="note">
    <b>Why real-to-sim.</b> Running a VLA on a real arm for hundreds of trials is slow and irreproducible. SimplerEnv builds digital twins of two real labs so a policy's <b>sim</b> success rate tracks its <b>real</b> success rate. The catch: a policy tuned for one embodiment's action space and camera can be near-SOTA on Google Robot yet near-zero on WidowX. Numbers below are <b>success %</b>; the WidowX figures are the <i>task-success</i> column (a separate <i>grasp</i> sub-metric exists). <code>Open Top Drawer &amp; Place Apple</code> is omitted, following HPT/TraceVLA/SpatialVLA, since almost every policy scores ~0.
  </div>

  <!-- 01 SETUPS -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>The two embodiments</h2><span class="desc">different arms · different action spaces · different tasks</span></div>
    <div class="setupwrap">
      <div class="setup" style="border-color:var(--google)">
        <h3>Google Robot</h3><div class="rb" style="color:var(--google)">RT-1 mobile manipulator · fractal data</div>
        <ul id="gtaskList"></ul>
      </div>
      <div class="setup" style="border-color:var(--widowx)">
        <h3>WidowX + Bridge</h3><div class="rb" style="color:var(--widowx)">6-DoF tabletop arm · BridgeData V2</div>
        <ul id="wtaskList"></ul>
      </div>
    </div>
  </section>

  <!-- 02 EMBODIMENT GAP -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>The embodiment gap</h2><span class="desc">Google Robot vs WidowX · same policy, two bodies</span></div>
    <div class="panel">
      <div class="lbl">EACH LINE = ONE POLICY · left dot = Google Robot (VM avg) · right dot = WidowX (overall) · longer line = worse transfer</div>
      <svg id="gap" viewBox="0 0 760 360"></svg>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)"><b style="color:var(--rust)">OpenVLA</b> is the cautionary tale: <b style="color:var(--ink)">27.7%</b> on Google Robot but <b style="color:var(--ink)">1.0%</b> on WidowX &mdash; a known controller/action-space artifact, not a real-world ability gap. Even the best policy, <b style="color:var(--green)">SpatialVLA</b>, drops from <b style="color:var(--ink)">71.9% &rarr; 34.4%</b>. The lesson the survey draws: <b style="color:var(--ink)">always report per-embodiment</b>.</div>
    </div>
  </section>

  <!-- 03 GOOGLE HEATMAP -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>Google Robot · per-task matrix</h2><span class="desc">Visual Matching vs Variant Aggregation</span></div>
    <div class="panel">
      <div style="margin-bottom:12px">
        <span class="chip on" data-set="vm" id="cVM">&#9673; Visual Matching</span>
        <span class="chip" data-set="va" id="cVA">&#9711; Variant Aggregation</span>
      </div>
      <div class="heatwrap"><table class="heat" id="gheat"></table></div>
    </div>
  </section>

  <!-- 04 WIDOWX HEATMAP -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>WidowX (Bridge) · per-task matrix</h2><span class="desc">task-success % · sorted by overall</span></div>
    <div class="panel"><div class="heatwrap"><table class="heat" id="wheat"></table></div>
    <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)"><b style="color:var(--ink)">Put Eggplant in Basket</b> is the easy one (SpatialVLA fine-tuned hits 100%); <b style="color:var(--ink)">Stack Green on Yellow</b> resists everyone. The whole WidowX board sits far below Google Robot &mdash; Bridge is the harder embodiment to transfer to.</div>
    </div>
  </section>

  <footer>
    SOURCE · Task names &amp; setups: SimplerEnv repo <code>simpler-env/SimplerEnv</code> (Li et al., <a href="https://arxiv.org/abs/2405.05941">arXiv 2405.05941</a>, CoRL 2024). Per-task success matrices verbatim from the SpatialVLA result tables (Qu et al., <a href="https://arxiv.org/abs/2501.15830">arXiv 2501.15830</a>, RSS 2025), which consolidate SimplerEnv numbers for RT-1/RT-1-X/RT-2-X, Octo, OpenVLA, RoboVLM, HPT, TraceVLA and SpatialVLA. Google Robot reports Visual Matching &amp; Variant Aggregation; WidowX shows task-success (a grasp sub-metric is also tracked upstream). OpenVLA's ~1% WidowX result is a controller artifact flagged in the SimplerEnv repo, not real-world ability.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
document.getElementById('gtaskList').innerHTML=DATA.gtasks.map(t=>`<li>${t}</li>`).join('')+'<li style="color:var(--dim)">(+ Open Top Drawer &amp; Place Apple — usually omitted)</li>';
document.getElementById('wtaskList').innerHTML=DATA.wtasks.map(t=>`<li>${t}</li>`).join('');

const lerp=(a,b,t)=>a+(b-a)*t;
function cellCol(v){if(v==null)return null;const t=Math.max(0,Math.min(1,v/100));
  const r=Math.round(lerp(224,63,t)),g=Math.round(lerp(83,182,t)),b=Math.round(lerp(58,168,t));return `rgb(${r},${g},${b})`;}

// embodiment gap chart (dumbbell)
(function(){
  const rows=DATA.gap.slice().sort((a,b)=>b.g-a.g);
  const W=760,H=360,padL=150,padR=60,padT=22,padB=40;
  const x=v=>padL+v/100*(W-padL-padR);
  const rowH=(H-padT-padB)/rows.length;
  let s='';
  for(let g=0;g<=100;g+=20){const xx=x(g);s+=`<line x1="${xx}" y1="${padT}" x2="${xx}" y2="${H-padB}" stroke="${css('--line')}"/>`;s+=`<text x="${xx}" y="${H-padB+16}" text-anchor="middle" class="gx">${g}%</text>`;}
  s+=`<text x="${(padL+W-padR)/2}" y="${H-6}" text-anchor="middle" class="gx" style="letter-spacing:.1em">SUCCESS RATE &rarr;</text>`;
  rows.forEach((r,i)=>{
    const cy=padT+rowH*(i+0.5);
    s+=`<text x="${padL-12}" y="${cy+4}" text-anchor="end" class="gx" style="fill:${css('--ink')};font-size:11px">${r.m}</text>`;
    s+=`<line x1="${x(r.w)}" y1="${cy}" x2="${x(r.g)}" y2="${cy}" stroke="${css('--line')}" stroke-width="2"/>`;
    s+=`<circle cx="${x(r.g)}" cy="${cy}" r="5.5" fill="${css('--google')}"/>`;
    s+=`<circle cx="${x(r.w)}" cy="${cy}" r="5.5" fill="${css('--widowx')}"/>`;
    s+=`<text x="${x(r.g)+9}" y="${cy+4}" class="gx" style="fill:${css('--google')}">${r.g.toFixed(1)}</text>`;
    s+=`<text x="${x(r.w)-9}" y="${cy+4}" text-anchor="end" class="gx" style="fill:${css('--widowx')}">${r.w.toFixed(1)}</text>`;
  });
  s+=`<circle cx="${padL+8}" cy="12" r="5" fill="${css('--google')}"/><text x="${padL+18}" y="16" class="gx" style="fill:${css('--google')}">Google Robot</text>`;
  s+=`<circle cx="${padL+150}" cy="12" r="5" fill="${css('--widowx')}"/><text x="${padL+160}" y="16" class="gx" style="fill:${css('--widowx')}">WidowX</text>`;
  document.getElementById('gap').innerHTML=s;
})();

// google heatmap
const gState={set:'vm'};
function renderG(){
  const tasks=DATA.gtasks;
  const key=gState.set, akey=gState.set==='vm'?'vmavg':'vaavg';
  const av=x=>x[akey]==null?-1:x[akey];
  const rows=DATA.google.slice().sort((a,b)=>av(b)-av(a));
  let h='<tr><th class="rowh">policy</th>'+tasks.map(t=>`<th>${t}</th>`).join('')+'<th>#AVG</th></tr>';
  rows.forEach(m=>{
    h+=`<tr><th class="rowh">${m.m}</th>`;
    m[key].forEach(v=>{const c=cellCol(v);h+=v==null?'<td class="na">–</td>':`<td style="background:${c}">${Math.round(v)}</td>`;});
    const a=m[akey];h+=`<td class="avg">${a==null?'–':a.toFixed(1)}</td></tr>`;
  });
  document.getElementById('gheat').innerHTML=h;
}
document.querySelectorAll('.chip[data-set]').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip[data-set]').forEach(x=>x.classList.remove('on'));c.classList.add('on');gState.set=c.dataset.set;renderG();});
renderG();

// widowx heatmap
(function(){
  const tasks=DATA.wtasks;
  const rows=DATA.widowx.slice().sort((a,b)=>b.avg-a.avg);
  let h='<tr><th class="rowh">policy</th>'+tasks.map(t=>`<th>${t}</th>`).join('')+'<th>#AVG</th></tr>';
  rows.forEach(m=>{
    h+=`<tr><th class="rowh">${m.m}</th>`;
    m.s.forEach(v=>{const c=cellCol(v);h+=`<td style="background:${c}">${Math.round(v)}</td>`;});
    h+=`<td class="avg">${m.avg.toFixed(1)}</td></tr>`;
  });
  document.getElementById('wheat').innerHTML=h;
})();
</script>
'''
open(f'{HERE}/simplerenv_dashboard.html','w').write(HTML)
print('wrote simplerenv_dashboard.html',len(HTML),'bytes')
