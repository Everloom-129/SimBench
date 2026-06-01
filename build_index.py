#!/usr/bin/env python3
"""Generates index.html — a blueprint-style gallery linking every benchmark dashboard."""
import os, json
HERE=os.path.dirname(os.path.abspath(__file__))

# section -> cards. each card: title, sub, path, stat, statlab, accent
SECTIONS=[
 ("Overview","the cross-benchmark survey that frames the collection",[
   {"t":"VLA Simulation Benchmarks","s":"Visual survey across 20+ benchmarks — word cloud, capability-vs-robustness, model heatmap, sourced stats.","p":"vla_benchmark_dashboard.html","stat":"20+","lab":"benchmarks","c":"#ff5436"},
 ]),
 ("Capability classics","standalone atlases · what models can do in-distribution",[
   {"t":"LIBERO","s":"4 evaluation suites + LIBERO-90; the saturated capability standard, Long suite the bottleneck.","p":"libero/libero_dashboard.html","stat":"131","lab":"tasks","c":"#5b8def"},
   {"t":"CALVIN","s":"34 tasks · 389 instructions; long-horizon language chaining, the signature decay curve.","p":"calvin/calvin_dashboard.html","stat":"34","lab":"tasks","c":"#46c4c0"},
   {"t":"RLBench","s":"106 task classes + the 18-task multi-task success matrix across 9 methods.","p":"rlbench/rlbench_dashboard.html","stat":"106","lab":"tasks","c":"#e0533a"},
   {"t":"Meta-World","s":"50 skills recombined into MT1/10/50 & ML1/10/45; config-membership matrix.","p":"metaworld/metaworld_dashboard.html","stat":"50","lab":"skills","c":"#5bbf6a"},
   {"t":"SimplerEnv","s":"Real-to-sim eval; Google Robot + WidowX heatmaps and the embodiment gap.","p":"simplerenv/simplerenv_dashboard.html","stat":"2","lab":"embodiments","c":"#e08a3c"},
   {"t":"RoboTwin","s":"50 dual-arm tasks · 2,961 instruction templates; bimanual capability with language diversity.","p":"RoboTwin/robotwin_tasks.html","stat":"50","lab":"dual-arm tasks","c":"#e0a93b"},
   {"t":"RoboLab","s":"NVIDIA SRL · RoboLab-120: 120 tasks × 3 language tiers (vague/default/specific), 3 difficulties & 3 competency axes; 1,200-eval leaderboard (SR/Score/motion), RoboArena-Elo correlated.","p":"RoboLab/robolab_dashboard.html","stat":"120","lab":"tasks","c":"#76b900"},
 ]),
 ("Robustness & perturbation","same tasks under controlled shifts · highest signal",[
   {"t":"LIBERO-Plus","s":"11 VLAs × 7 perturbations; camera & robot-state collapse, language ignored.","p":"libero-plus/libero_plus_dashboard.html","stat":"10,030","lab":"eval runs","c":"#e0463a"},
   {"t":"LIBERO-PRO","s":"Anti-memorization probe; position & task changes drive success to 0%.","p":"libero-pro/libero_pro_dashboard.html","stat":"90%→0","lab":"collapse","c":"#a06be0"},
   {"t":"THE COLOSSEUM","s":"14 perturbation factors × 20 RLBench tasks; object color & distractors hurt most.","p":"colosseum/colosseum_dashboard.html","stat":"14","lab":"factors","c":"#c89b4a"},
   {"t":"RoboCasa365 · Atomic","s":"65 atomic kitchen skills evaluated across thousands of randomized scenes, layouts & textures.","p":"robocasa365/robocasa365_atomic_skills.html","stat":"65","lab":"atomic tasks","c":"#d8b878"},
   {"t":"RoboCasa365 · Composite","s":"300 composite kitchen activities (2–16 subtasks) under broad scene & object randomization.","p":"robocasa365/robocasa365_composite_tasks.html","stat":"300","lab":"composite tasks","c":"#e0a93b"},
 ]),
 ("Long-horizon & memory","non-Markovian / memory-dependent · emerging 2026",[
   {"t":"BEHAVIOR Challenge 2025","s":"50 long-horizon household tasks across full rooms; durations to ~460s — the long-horizon extreme.","p":"Behavior1K/behavior_challenge_2025.html","stat":"50","lab":"long-horizon tasks","c":"#46c4c0"},
   {"t":"Memory Landscape","s":"6 memory-dependent benchmarks organized by memory taxonomy & type coverage.","p":"memory/memory_dashboard.html","stat":"6","lab":"benchmarks","c":"#9a7bff"},
 ]),
 ("Sim ↔ Real bridge","real-robot evaluation & the reality gap · capstone",[
   {"t":"Sim ↔ Real","s":"The reality ladder: clean-sim 97% → real-robot ~50%; RoboChallenge & ManipArena.","p":"sim2real/sim2real_dashboard.html","stat":"~2×","lab":"sim→real drop","c":"#5bbf6a"},
 ]),
 ("Ecosystems & aggregators","asset ecosystems and multi-benchmark task tables in a unified format",[
   {"t":"MolmoSpaces","s":"Ai2 open ecosystem: 230k scenes · 130k objects · 42M grasps; 8-task bench from a 10-template instruction grammar; sim↔real R≈0.96.","p":"molmospaces/molmospaces_dashboard.html","stat":"42M","lab":"annotated grasps","c":"#9a7bff"},
   {"t":"RoboVerse","s":"MetaSim unifies 6 simulators + 18 source benchmarks; the manipulation migration alone = 276 task categories, ~500k trajectories.","p":"roboverse/roboverse_dashboard.html","stat":"18","lab":"source benchmarks","c":"#5bbf6a"},
   {"t":"LW-BenchHub","s":"275 tasks re-exported into one gym format (LIBERO + RoboCasa families).","p":"lightwheel/lw_benchhub_tasks.html","stat":"275","lab":"tasks","c":"#74c476"},
 ]),
]

# count dashboards that exist
ncards=sum(len(cards) for _,_,cards in SECTIONS)
present=sum(1 for _,_,cards in SECTIONS for c in cards if os.path.exists(os.path.join(HERE,c['p'])))

data_json=json.dumps([[title,sub,cards] for title,sub,cards in SECTIONS],separators=(',',':'))

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VLA Sim-Benchmark Atlas · Index</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0a0c10; --paper2:#11151d; --card:#141a24; --ink:#e9edf4; --dim:#828ca0; --line:#212a39;
    --hot:#ff5436; --amber:#e0a93b; --cyan:#46c4c0; --violet:#9a7bff; --green:#74c476; --blue:#5b8def;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(1200px 600px at 85% -5%, rgba(154,123,255,.10), transparent 60%),radial-gradient(900px 500px at -5% 8%, rgba(255,84,54,.08), transparent 55%)}
  .shell{max-width:1180px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:28px 30px;position:relative;overflow:hidden;border-radius:16px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:140px;height:140px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.4}
  .top:before{right:130px;border:1.5px solid var(--hot)}
  .top:after{right:34px;border:1.5px solid var(--cyan)}
  .kick{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.34em;text-transform:uppercase;color:var(--hot)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(36px,6.5vw,74px);line-height:.95;margin:.16em 0 .14em;letter-spacing:-.02em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--hot),var(--amber));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:74ch;font-size:15.5px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden;max-width:560px}
  .stat{padding:14px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:26px;line-height:1;color:var(--cyan)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:5px}
  section{margin-top:38px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:16px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:23px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .grid{display:grid;gap:14px;grid-template-columns:1fr}
  @media(min-width:640px){.grid{grid-template-columns:1fr 1fr}}
  @media(min-width:980px){.grid{grid-template-columns:1fr 1fr 1fr}}
  a.cardlink{text-decoration:none;color:inherit}
  .ccard{border:1.5px solid var(--line);border-left-width:4px;background:var(--card);border-radius:13px;padding:18px 20px;height:100%;display:flex;flex-direction:column;gap:8px;transition:transform .15s,border-color .15s,box-shadow .15s;position:relative;overflow:hidden}
  a.cardlink:hover .ccard{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.35)}
  .ccard .ch{display:flex;align-items:baseline;gap:10px}
  .ccard .ct{font-family:'Fraunces',serif;font-weight:900;font-size:20px;line-height:1.05}
  .ccard .cstat{margin-left:auto;text-align:right}
  .ccard .cstat .n{font-family:'Space Mono',monospace;font-weight:700;font-size:15px}
  .ccard .cstat .l{font-family:'Space Mono',monospace;font-size:8px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
  .ccard .cs{font-size:12.5px;color:var(--dim);line-height:1.5;flex:1}
  .ccard .go{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.08em;text-transform:uppercase;display:flex;align-items:center;gap:6px;margin-top:4px}
  .ccard .miss{color:var(--hot)}
  footer{margin-top:42px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer code{color:var(--cyan)}
  .langtoggle{position:fixed;top:14px;right:14px;z-index:9999;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#e9edf4;background:rgba(20,26,36,.82);border:1.5px solid #46c4c0;border-radius:9px;padding:7px 13px;text-decoration:none;backdrop-filter:blur(6px);transition:background .15s,color .15s,transform .15s}
  .langtoggle:hover{background:#46c4c0;color:#0a0c10;transform:translateY(-1px)}
</style>
<a class="langtoggle" href="index_cn.html" title="切换到中文版">中文</a>
<div class="shell">
  <header class="top">
    <div class="kick">VLA Simulation Benchmarks · Task &amp; Robustness Atlases</div>
    <h1>The Benchmark<br><em>Atlas Index</em></h1>
    <div class="byline" style="font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2"><b style="color:var(--ink);font-weight:600">Jie Wang</b> · <a href="https://everloom-129.github.io/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">everloom-129.github.io</a> · GRASP Lab, UPenn &nbsp;·&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">Claude Code</a> &nbsp;·&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
    <p class="lede">One front door to every dashboard in this collection &mdash; interactive, single-file, blueprint-style atlases of the task suites and leaderboards used to evaluate <b>Vision-Language-Action</b> models. Grouped from <b>capability</b> (what models do in-distribution) through <b>robustness</b> and <b>memory</b> to the <b>sim&#8202;↔&#8202;real</b> reality gap. Click any card to open its atlas in a new tab.</p>
    <div class="statbar">
      <div class="stat"><div class="num">''' + str(present) + r'''</div><div class="lab">dashboards</div></div>
      <div class="stat"><div class="num">6</div><div class="lab">tiers</div></div>
      <div class="stat"><div class="num">15+</div><div class="lab">benchmarks</div></div>
    </div>
  </header>
  <div id="sections"></div>
  <footer>
    Each atlas is a standalone HTML file with its data parsed to a sibling CSV; every figure is traced to its origin paper in that atlas's footer. Open this <code>index.html</code> directly, or serve the folder (<code>python3 -m http.server</code>) and browse to it. Cards open in a new tab so this index stays as your hub.
  </footer>
</div>
<script>
const SECTIONS=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const root=document.getElementById('sections');
SECTIONS.forEach(([title,sub,cards],si)=>{
  const sec=document.createElement('section');
  sec.innerHTML=`<div class="sec-h"><span class="idx">${String(si+1).padStart(2,'0')}</span><h2>${title}</h2><span class="desc">${sub}</span></div>`;
  const grid=document.createElement('div');grid.className='grid';
  cards.forEach(c=>{
    const a=document.createElement('a');a.className='cardlink';a.href=c.p;a.target='_blank';a.rel='noopener';
    a.innerHTML=`<div class="ccard" style="border-left-color:${c.c}">
      <div class="ch"><span class="ct">${c.t}</span>
        <span class="cstat"><div class="n" style="color:${c.c}">${c.stat}</div><div class="l">${c.lab}</div></span></div>
      <div class="cs">${c.s}</div>
      <div class="go" style="color:${c.c}">open atlas →</div></div>`;
    grid.appendChild(a);
  });
  sec.appendChild(grid);root.appendChild(sec);
});
</script>
'''
open(os.path.join(HERE,'index.html'),'w').write(HTML)
print(f'wrote index.html · {present}/{ncards} dashboards present, {len(HTML)} bytes')
