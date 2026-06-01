#!/usr/bin/env python3
"""Builds molmospaces_templates.csv and molmospaces_dashboard.html (blueprint style).

MolmoSpaces is structurally unlike the other atlases: it is primarily an ASSET
ECOSYSTEM (objects/scenes/grasps/robots), and its task language is not a stored
instruction list but a small GENERATIVE GRAMMAR. Instructions live in two layers:
  (1) 10 task-description templates in molmo_spaces/tasks/*.py  (the grammar)
  (2) per-episode resolved `language.task_description` in the bench JSON  (the surface)
This dashboard surfaces both, plus the 8 MolmoSpaces-Bench task definitions,
the asset-ecosystem scale, and the model + sim-to-real results.

Every figure is traceable to: blog (allenai.org/blog/molmospaces), HF dataset card
(allenai/molmospaces, 1,003,624 rows / 13.1 TB / 51 subsets), the tech report
(arXiv 2602.11337v2) and the GitHub repo (allenai/molmospaces).
"""
import json, csv

HERE = __file__.rsplit('/', 1)[0]

# ============================================================================
# LAYER 1 — the 10 task-description templates (the generative grammar).
# Verbatim f-string templates from molmo_spaces/tasks/*.py get_task_description().
# `examples` are real resolved instructions from the bench JSON / paper Fig. 8.
# ============================================================================
TEMPLATES = [
 {"cls":"PickTask","family":"pick","tmpl":"Pick up the {pickup_obj_name}",
  "bench":"Pick","crit":"Object lifted ≥ 1 cm from its start height.",
  "examples":["Pick up the green glossy cup with spherical base",
              "Pick up the cylindrical blue lighter with red button",
              "Pick up the white bowl"]},
 {"cls":"PickAndPlaceTask","family":"place","tmpl":"Pick up the {pickup_name} and place it in or on the {place_name}",
  "bench":"Pick-and-place","crit":"≥50% of object weight vertically supported by the receptacle; receptacle not displaced >10 cm or 45°.",
  "examples":["Pick up the spray and place it in or on the bowl",
              "Pick up the apple and place it in or on the plate"]},
 {"cls":"PickAndPlaceNextToTask","family":"place","tmpl":"Pick up the {pickup_name} and place it next to the {place_name}",
  "bench":"Pick-and-place-next-to","crit":"Object within 5 cm surface-to-surface of the receptacle on the same support; receptacle not moved >5 cm or 45°.",
  "examples":["Pick up the fork and place it next to the plate",
              "Pick up the mug and place it next to the kettle"]},
 {"cls":"PickAndPlaceColorTask","family":"place","tmpl":"Pick up the {pickup_name} and place it in or on the {color} {place_name}",
  "bench":"Pick-and-place-color","crit":"Same as pick-and-place, but the correct receptacle is selected among multiple color-differentiated ones (color named in the prompt).",
  "examples":["Pick up the block and place it in or on the red bowl",
              "Pick up the sponge and place it in or on the blue tray"]},
 {"cls":"PackingTask","family":"place","tmpl":"Pick up the {pickup_name} and place it into the {place_name}",
  "bench":"(pick-and-place variant)","crit":"Object placed INTO a container (containment, not just support).",
  "examples":["Pick up the toy and place it into the box",
              "Pick up the marker and place it into the cup"]},
 {"cls":"OpeningTask","family":"articulate","tmpl":"Open the {pickup_obj_name}",
  "bench":"Open / Close","crit":"Open: articulated fixture (drawer, cabinet, microwave, fridge) from fully-closed opened ≥15%. Close: from half-open closed to ≤15% open.",
  "examples":["Open the oven","Open the drawer","Close the drawer","Open the microwave"]},
 {"cls":"DoorOpeningTask","family":"door","tmpl":"Push the door open",
  "bench":"Open-door","crit":"Hinged door opened ≥67% by manipulating its handle or surface.",
  "examples":["Push the door open"]},
 {"cls":"DoorOpeningTask","family":"door","tmpl":"Pull the door open",
  "bench":"Open-door","crit":"Hinged door opened ≥67% by manipulating its handle or surface.",
  "examples":["Pull the door open"]},
 {"cls":"NavToObjTask","family":"navigate","tmpl":"Navigate to the {object_name}",
  "bench":"Navigate-to","crit":"Target initialized 4–20 m away; success = target visible from head camera AND within 1.5 m.",
  "examples":["Navigate to the refrigerator","Navigate to the sofa"]},
 {"cls":"NavToObjTask","family":"navigate","tmpl":"Navigate to any {object_name} ({n} available)",
  "bench":"Navigate-to","crit":"Multiple valid targets exist; reaching any one within 1.5 m and in view succeeds.",
  "examples":["Navigate to any chair (4 available)","Navigate to any potted plant (3 available)"]},
]

# the 8 official MolmoSpaces-Bench tasks (paper) — name, family, threshold value (for the viz), unit, blurb
BENCH = [
 {"task":"Navigate-to","family":"navigate","thr":"≤ 1.5 m","blurb":"Search for and navigate to a named object initialized 4–20 m away. Success = object visible from the head camera and within 1.5 m.","prog":0.10},
 {"task":"Pick","family":"pick","thr":"≥ 1 cm","blurb":"Grasp and lift the named object at least 1 cm from its initial height.","prog":0.18},
 {"task":"Pick-and-place","family":"place","thr":"≥ 50% wt","blurb":"Move the object so ≥50% of its weight is supported in/on the receptacle, which may not move >10 cm / 45°.","prog":0.55},
 {"task":"Pick-and-place-color","family":"place","thr":"color match","blurb":"As pick-and-place, but choose the correctly-colored receptacle among several; color is named in the prompt.","prog":0.62},
 {"task":"Pick-and-place-next-to","family":"place","thr":"≤ 5 cm","blurb":"Place the object within 5 cm surface-to-surface of the receptacle on the same support surface.","prog":0.66},
 {"task":"Open","family":"articulate","thr":"≥ 15%","blurb":"Open an articulated fixture (drawer, cabinet, microwave, fridge) from fully closed by at least 15%.","prog":0.40},
 {"task":"Close","family":"articulate","thr":"≤ 15% open","blurb":"Close an articulated fixture initialized half-open down to at most 15% open (≥85% closed).","prog":0.40},
 {"task":"Open-door","family":"door","thr":"≥ 67%","blurb":"Open a hinged door by manipulating its handle or surface, by at least 67%.","prog":0.50},
]

# ============================================================================
# ASSET ECOSYSTEM — headline scale (blog) + HF subset families (dataset card)
# ============================================================================
ECOSYSTEM = {
 "headline":[
   {"n":"230k+","lab":"indoor scenes","c":"--cyan"},
   {"n":"130k+","lab":"object models","c":"--violet"},
   {"n":"42M","lab":"annotated grasps","c":"--amber"},
   {"n":"48k","lab":"objects w/ grasps","c":"--green"},
 ],
 # HF subsets grouped into families (rows summed across Isaac+MuJoCo sides where they mirror)
 "families":[
   {"name":"Scenes","rows":230000,"c":"--cyan","detail":"holodeck-objaverse, iTHOR-120, ProcTHOR-10K, ProcTHOR-Objaverse · homes, offices, classrooms, hospitals, museums · >95% pass validation"},
   {"name":"Objects","rows":130000,"c":"--violet","detail":"129k curated Objaverse assets across ~3,000 WordNet synsets + THOR · 1,600+ rigid graspable instances / 134 categories"},
   {"name":"Grasps","rows":48111,"c":"--amber","detail":"42M annotated 6-DoF grasps across 48,111 objects (up to ~1,000 per object) · sampled with a Robotiq-2F85 gripper, DROID-derived"},
   {"name":"Robots","rows":6,"c":"--green","detail":"Franka FR3 / DROID, RBY1, RUM, floating Robotiq-2F85 · USD (Isaac) + XML (MuJoCo)"},
   {"name":"Bench","rows":8,"c":"--rust","detail":"MolmoSpaces-Bench v1/v2 · 8 tasks · episode specs with scene, robot pose, object poses, cameras, language"},
 ],
 "totals":{"rows":"1,003,624","size":"13.1 TB","subsets":51},
}

# ============================================================================
# MODELS — verbatim from tech report (arXiv 2602.11337v2). Approx success rates.
# ============================================================================
LEADER = {
 "manip":{
   "note":"Pick task · MSProc-1k benchmark · success rate (approx., from the tech report).",
   "rows":[
     {"model":"π₀.₅","sr":65},
     {"model":"π₀-FAST","sr":60},
     {"model":"π₀","sr":45},
   ]},
 "nav":{
   "note":"Navigate-to task · 2,000 trajectories · success rate (approx.).",
   "rows":[
     {"model":"RING","sr":50},
     {"model":"DualVLN","sr":15},
   ]},
}

# evaluation axes that MolmoSpaces-Bench systematically perturbs
AXES = [
 {"axis":"Object properties","ex":"category, shape, graspability (side- vs top-graspable)"},
 {"axis":"Layouts","ex":"scene complexity, multi-room navigation distance (4–20 m)"},
 {"axis":"Task complexity","ex":"atomic skills → LLM-composed long-horizon tasks"},
 {"axis":"Sensory conditions","ex":"lighting intensity, point-cloud noise, camera occlusion, wrist vs. exo view"},
 {"axis":"Dynamics","ex":"joint noise, initial joint positions, gripper state"},
 {"axis":"Task semantics","ex":"prompt phrasing / referral-expression variation"},
]

# ---- word frequencies from templates + example instructions (placeholders kept) ----
import re
from collections import Counter
STOP = set("the a an to it of on in and or into next up your you".split())
wc = Counter()
for t in TEMPLATES:
    txt = t["tmpl"].replace("{","").replace("}","") + " " + " ".join(t["examples"])
    for tok in re.findall(r"[a-z_]+", txt.lower()):
        tok = tok.strip("_")
        if not tok or tok in STOP or len(tok) < 3: continue
        wc[tok] += 1
# weight the action verbs up so they read as the spine of the grammar
for verb,boost in [("pick",6),("place",6),("navigate",4),("open",4),("up",0)]:
    if verb in wc: wc[verb]+=boost
words = wc.most_common(60)

# ---- write CSV (the grammar) ----
with open(f'{HERE}/molmospaces_templates.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['task_class','task_family','bench_task','instruction_template','success_criterion','example_resolved_instructions'])
    for t in TEMPLATES:
        w.writerow([t['cls'],t['family'],t['bench'],t['tmpl'],t['crit'],' | '.join(t['examples'])])
print(f'wrote molmospaces_templates.csv ({len(TEMPLATES)} templates)')

DATA = {"templates":TEMPLATES,"bench":BENCH,"eco":ECOSYSTEM,"leader":LEADER,"axes":AXES,"words":words}
data_json = json.dumps(DATA, separators=(',',':'))

# =========================== HTML ===========================
HTML = r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MolmoSpaces · Ecosystem &amp; Instruction-Grammar Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0a0d12; --paper2:#10141d; --card:#141a25; --ink:#e9edf4; --dim:#838ba3; --line:#212a3a;
    --cyan:#46c4c0; --violet:#9a7bff; --amber:#e0a93b; --green:#74c476; --rust:#e0703a; --blue:#5b8def;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(900px 480px at 84% -8%, rgba(154,123,255,.12), transparent 60%),radial-gradient(880px 470px at 4% 3%, rgba(70,196,192,.08), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--violet)}
  .top:after{right:30px;border:1.5px solid var(--cyan)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--violet);border:1px solid var(--violet);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--amber)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--violet),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:78ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:28px;line-height:1}
  .stat .num.v{color:var(--violet)} .stat .num.c{color:var(--cyan)} .stat .num.a{color:var(--amber)} .stat .num.g{color:var(--green)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--violet);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.62;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .twocol{display:grid;gap:18px}
  @media(min-width:880px){.twocol{grid-template-columns:1fr 1fr}}
  .twocol.bias{grid-template-columns:1fr}
  @media(min-width:880px){.twocol.bias{grid-template-columns:1.15fr .85fr}}
  /* layer diagram */
  .layers{display:grid;gap:14px}
  @media(min-width:760px){.layers{grid-template-columns:1fr auto 1fr;align-items:center}}
  .layer{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);padding:16px 18px}
  .layer .lt{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--violet);margin-bottom:6px}
  .layer.l2 .lt{color:var(--cyan)}
  .layer .lh{font-family:'Fraunces',serif;font-weight:600;font-size:17px;margin-bottom:4px}
  .layer .ld{font-size:12.5px;color:var(--dim);line-height:1.5}
  .layer code{font-family:'Space Mono',monospace;font-size:11px;color:var(--amber);background:var(--paper);padding:1px 5px;border-radius:3px}
  .arrow{font-family:'Space Mono',monospace;font-size:24px;color:var(--dim);text-align:center}
  @media(max-width:759px){.arrow{transform:rotate(90deg)}}
  /* template grammar table / catalog */
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;align-items:center}
  .controls input{font-family:'IBM Plex Sans';font-size:13px;padding:9px 12px;border:1.5px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:8px;flex:1;min-width:220px}
  .controls input:focus{outline:none;border-color:var(--cyan)}
  .chip{font-family:'Space Mono',monospace;font-size:10.5px;padding:8px 11px;border:1.5px solid var(--line);background:var(--paper2);color:var(--dim);cursor:pointer;border-radius:8px;letter-spacing:.04em}
  .chip.on{border-color:var(--cyan);color:var(--cyan)}
  .count-line{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:10px}
  .tasklist{display:flex;flex-direction:column;gap:10px}
  .tcard{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);overflow:hidden}
  .tcard>summary{cursor:pointer;list-style:none;padding:14px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
  .tcard>summary::-webkit-details-marker{display:none}
  .tcard>summary:after{content:"\25B8";margin-left:auto;color:var(--cyan);transition:transform .2s}
  .tcard[open]>summary:after{transform:rotate(90deg)}
  .tcard .tmpl{font-family:'Space Mono',monospace;font-weight:700;font-size:13.5px;color:var(--ink)}
  .tcard .tmpl .ph{color:var(--amber)}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex:none}
  .catpill{font-family:'Space Mono',monospace;font-size:9.5px;padding:3px 9px;border-radius:11px;border:1px solid var(--line);color:var(--dim);letter-spacing:.03em}
  .tcard .body{padding:0 18px 16px;border-top:1px solid var(--line)}
  .tcard .crit{font-size:13px;color:var(--ink);line-height:1.5;margin:14px 0 6px}
  .tcard .crit:before{content:"success \2014 ";font-family:'Space Mono',monospace;font-size:9px;color:var(--green);text-transform:uppercase;letter-spacing:.06em}
  .tcard .clsname{font-family:'Space Mono',monospace;font-size:9.5px;color:var(--violet)}
  .samp-h{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;margin:12px 0 6px}
  .samp{display:flex;flex-direction:column;gap:4px}
  .samp .row{font-size:12.5px;color:var(--ink);line-height:1.4;padding-left:14px;position:relative}
  .samp .row:before{content:"\203A";position:absolute;left:2px;color:var(--line)}
  mark{background:rgba(224,169,59,.3);color:inherit;padding:0 1px}
  /* bench task bars */
  .bar-wrap{display:flex;flex-direction:column;gap:9px}
  .bench-row{display:grid;grid-template-columns:172px 1fr 76px;align-items:center;gap:12px}
  .bench-row .name{font-family:'Space Mono',monospace;font-size:12.5px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .track{height:18px;background:var(--paper);border:1px solid var(--line);border-radius:3px;overflow:hidden;position:relative}
  .fill{height:100%;position:relative;z-index:1;transition:width .6s cubic-bezier(.2,.8,.2,1)}
  .bench-row .thr{font-family:'Space Mono',monospace;font-size:11px;font-weight:700;text-align:right;color:var(--dim)}
  /* donut */
  .donutwrap{display:flex;gap:22px;align-items:center;flex-wrap:wrap}
  #ecoDonut{flex:0 0 168px}
  .dl{display:flex;flex-direction:column;gap:9px;font-size:12.5px;flex:1;min-width:200px}
  .dl span.r{display:flex;align-items:center;gap:9px}
  .dl i{width:12px;height:12px;border-radius:2px;flex:none}
  .dl b{font-family:'Space Mono',monospace;color:var(--dim);font-weight:400;margin-left:auto;padding-left:12px}
  /* leaderboard */
  .lb-row{display:grid;grid-template-columns:96px 1fr 46px;align-items:center;gap:12px;margin-bottom:9px}
  .lb-row .name{font-family:'Space Mono',monospace;font-size:13px;color:var(--ink)}
  .lb-row .v{font-family:'Space Mono',monospace;font-size:12.5px;font-weight:700;text-align:right}
  .s2r{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-top:6px}
  .s2r .big{font-family:'Fraunces',serif;font-weight:900;font-size:46px;line-height:1;color:var(--green)}
  .s2r .big small{font-size:18px;color:var(--dim);font-family:'Space Mono',monospace;font-weight:400}
  .s2r .txt{font-size:13px;color:var(--dim);line-height:1.5;flex:1;min-width:220px}
  /* axes grid */
  .axgrid{display:grid;gap:12px;grid-template-columns:1fr}
  @media(min-width:680px){.axgrid{grid-template-columns:1fr 1fr}}
  @media(min-width:980px){.axgrid{grid-template-columns:1fr 1fr 1fr}}
  .axcard{border:1.5px solid var(--line);border-radius:11px;background:var(--paper2);padding:14px 16px}
  .axcard .an{font-family:'Fraunces',serif;font-weight:600;font-size:15.5px;margin-bottom:4px}
  .axcard .ae{font-size:12px;color:var(--dim);line-height:1.5}
  #cloud{width:100%;height:280px;display:block}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--violet)} footer code{color:var(--cyan)}
  .langtoggle{position:fixed;top:14px;right:14px;z-index:9999;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#e9edf4;background:rgba(20,26,36,.82);border:1.5px solid #46c4c0;border-radius:9px;padding:7px 13px;text-decoration:none;backdrop-filter:blur(6px);transition:background .15s,color .15s,transform .15s}
  .langtoggle:hover{background:#46c4c0;color:#0a0c10;transform:translateY(-1px)}
</style>
<a class="langtoggle" href="molmospaces_dashboard_cn.html" title="切换到中文版">中文</a>
<div class="shell">
  <header class="top">
    <div class="stamp">1.0M rows &middot; 13.1 TB</div>
    <div class="kick">MolmoSpaces &middot; Ai2 &middot; Open Robot Learning Ecosystem</div>
    <h1>MolmoSpaces<br><em>Ecosystem Atlas</em></h1>
    <div class="byline" style="font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2"><b style="color:var(--ink);font-weight:600">Jie Wang</b> &middot; <a href="https://everloom-129.github.io/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">everloom-129.github.io</a> &middot; GRASP Lab, UPenn &nbsp;&middot;&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">Claude Code</a> &nbsp;&middot;&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
    <p class="lede">MolmoSpaces is not a task-instruction benchmark like the others &mdash; it is an <b>open ecosystem</b>: <b>230k+ scenes</b>, <b>130k+ objects</b>, <b>42M grasps</b>, and a thin <b>8-task</b> evaluation suite on top. Its instructions are <b>not a stored list</b> &mdash; they are a <b>generative grammar</b> of just <b>10 templated f-strings</b> that resolve, per episode, into concrete language. This atlas maps <b>where the instructions live</b> (the two layers), the 8 <b>MolmoSpaces-Bench</b> task definitions, the <b>asset ecosystem</b> at scale, and the model &amp; <b>sim&#8202;↔&#8202;real</b> results &mdash; where the pick task tracks real-robot success at <b>R&nbsp;≈&nbsp;0.96</b>.</p>
    <div class="statbar">
      <div class="stat"><div class="num v">8</div><div class="lab">bench tasks</div></div>
      <div class="stat"><div class="num c">10</div><div class="lab">instruction templates</div></div>
      <div class="stat"><div class="num a">230k+</div><div class="lab">scenes</div></div>
      <div class="stat"><div class="num g">130k+</div><div class="lab">objects</div></div>
      <div class="stat"><div class="num">42M</div><div class="lab">annotated grasps</div></div>
    </div>
  </header>

  <div class="note">
    <b>Where the instructions live &mdash; the question this dataset really answers.</b> Unlike CALVIN or RoboTwin, MolmoSpaces has <b>no flat instruction table to scrape</b>. The HF dataset (<code>1,003,624 rows</code>, <code>13.1 TB</code>, 51 subsets) is ~99.9% assets; only the tiny <code>molmospaces-bench</code> subsets carry task data, and those are episode manifests, not text. Instructions are <b>generated</b>: each task class in <code>molmo_spaces/tasks/*.py</code> has a <code>get_task_description()</code> returning a templated f-string, and each evaluation episode stores a resolved <code>language.task_description</code> filled from its <code>referral_expressions</code>. Two layers, below.
  </div>

  <!-- 01 WHERE INSTRUCTIONS LIVE -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>Where the instructions live</h2><span class="desc">grammar (10 templates) → resolved per-episode surface</span></div>
    <div class="panel">
      <div class="layers">
        <div class="layer l1">
          <div class="lt">Layer 1 &middot; the grammar</div>
          <div class="lh">10 task-description templates</div>
          <div class="ld"><code>get_task_description()</code> in <code>molmo_spaces/tasks/*.py</code> returns a templated f-string per task class. A finite, scrapeable grammar &mdash; the complete set is in section 02.</div>
        </div>
        <div class="arrow">→</div>
        <div class="layer l2">
          <div class="lt">Layer 2 &middot; the surface</div>
          <div class="lh">Resolved <code>language.task_description</code></div>
          <div class="ld">Each bench episode fills the template from its <code>referral_expressions</code> dict &mdash; e.g. <i>&ldquo;Pick up the green glossy cup with spherical base&rdquo;</i>. LLM/metadata phrasing &rarr; effectively unlimited surface strings.</div>
        </div>
      </div>
      <div class="note" style="margin-top:16px;border-left-color:var(--cyan)">To get the <b>grammar</b>, parse the 10 templates (shipped here as <code>molmospaces_templates.csv</code>). To get <b>concrete instructions</b>, download a <code>molmospaces-bench-v2</code> subset and read each episode's <code>language.task_description</code> &mdash; some manifests reference Ai2-internal <code>/weka/</code> paths and may not be in the public release.</div>
    </div>
  </section>

  <!-- 02 THE 10-TEMPLATE GRAMMAR -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>The instruction grammar</h2><span class="desc">10 templates · click to expand resolved examples · search</span></div>
    <div class="panel">
      <div class="controls">
        <input id="search" placeholder="Search template, family, or example… (e.g. place, door, navigate)">
        <span class="chip on" data-f="all">all</span>
        <span class="chip" data-f="pick">pick</span>
        <span class="chip" data-f="place">place</span>
        <span class="chip" data-f="articulate">open/close</span>
        <span class="chip" data-f="door">door</span>
        <span class="chip" data-f="navigate">navigate</span>
      </div>
      <div class="count-line" id="countLine"></div>
      <div class="tasklist" id="tasklist"></div>
    </div>
  </section>

  <!-- 03 THE 8 BENCH TASKS -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>MolmoSpaces-Bench &middot; 8 tasks</h2><span class="desc">oracle success thresholds · from the tech report</span></div>
    <div class="panel">
      <div class="lbl">EACH BAR'S FILL IS ILLUSTRATIVE OF TASK DIFFICULTY/PROGRESS GEOMETRY · THE BADGE IS THE ACTUAL SUCCESS THRESHOLD</div>
      <div class="bar-wrap" id="benchBars"></div>
      <div class="note" style="margin-top:16px;border-left-color:var(--green)">A bench episode spec packs <b>everything to recreate the task</b>: scene, robot pose, object poses, cameras, and the language instruction. <b>Open</b> and <b>Close</b> share one articulation task class; <b>color</b> / <b>next-to</b> / <b>packing</b> are pick-and-place variants &mdash; so 8 bench tasks map onto the 10-template grammar, not 1:1.</div>
    </div>
  </section>

  <!-- 04 ASSET ECOSYSTEM -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>The asset ecosystem at scale</h2><span class="desc">~99.9% of the dataset is assets, not language</span></div>
    <div class="twocol bias">
      <div class="panel">
        <div class="lbl">DATASET FAMILIES · by representative row count (log-area) · hover legend for detail</div>
        <div class="donutwrap"><svg id="ecoDonut" viewBox="0 0 168 168"></svg><div class="dl" id="ecoLegend"></div></div>
      </div>
      <div class="panel">
        <div class="lbl">HEADLINE SCALE · from the blog</div>
        <div id="ecoHead" style="display:flex;flex-direction:column;gap:14px"></div>
        <div style="margin-top:16px;font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;border-top:1px solid var(--line);padding-top:14px">
          <span style="color:var(--ink)">1,003,624</span> rows &middot; <span style="color:var(--ink)">13.1 TB</span> &middot; <span style="color:var(--ink)">51</span> subsets<br>
          USD (Isaac) + XML (MuJoCo) &middot; MuJoCo / ManiSkill / Isaac Lab compatible<br>
          ODC-BY 1.0 (Objaverse) + CC&nbsp;BY&nbsp;4.0 &middot; released 2026.02.11
        </div>
      </div>
    </div>
  </section>

  <!-- 05 MODELS + SIM2REAL -->
  <section>
    <div class="sec-h"><span class="idx">05</span><h2>Models &amp; sim&#8202;↔&#8202;real</h2><span class="desc">approx. success rates + the predictive-validity result</span></div>
    <div class="twocol">
      <div class="panel">
        <div class="lbl" id="manipNote">MANIPULATION · PICK</div>
        <div id="manipBars"></div>
        <div class="lbl" style="margin-top:18px" id="navNote">NAVIGATION · NAVIGATE-TO</div>
        <div id="navBars"></div>
      </div>
      <div class="panel">
        <div class="lbl">SIM ↔ REAL CORRELATION · PICK</div>
        <div class="s2r">
          <div class="big">0.96<small> R</small></div>
          <div class="txt">Simulated pick success tracks <b style="color:var(--ink)">real-robot</b> pick success across <b style="color:var(--ink)">752 RoboArena</b> tasks &mdash; Spearman <b style="color:var(--ink)">ρ&nbsp;=&nbsp;0.98</b>. This is the ecosystem's headline claim: the sim is <b style="color:var(--ink)">predictively valid</b>, so a number on MolmoSpaces-Bench is expected to transfer.</div>
        </div>
        <div class="lbl" style="margin-top:22px">EVALUATION AXES · what the bench systematically perturbs</div>
        <div class="axgrid" id="axGrid"></div>
      </div>
    </div>
  </section>

  <!-- 06 VOCAB -->
  <section>
    <div class="sec-h"><span class="idx">06</span><h2>Instruction vocabulary</h2><span class="desc">tokenized from the 10 templates + resolved examples</span></div>
    <div class="panel"><canvas id="cloud"></canvas></div>
  </section>

  <footer>
    SOURCE &middot; Ecosystem scale &amp; tasks: Ai2 blog (<a href="https://allenai.org/blog/molmospaces">allenai.org/blog/molmospaces</a>) and tech report <b>MolmoSpaces</b> (<a href="https://arxiv.org/abs/2602.11337">arXiv 2602.11337v2</a>). Dataset figures (<code>1,003,624</code> rows / <code>13.1 TB</code> / 51 subsets / licenses): HuggingFace <a href="https://huggingface.co/datasets/allenai/molmospaces">allenai/molmospaces</a> dataset card. The 10 instruction templates are the verbatim <code>get_task_description()</code> f-strings in <code>molmo_spaces/tasks/*.py</code> (<a href="https://github.com/allenai/molmospaces">github.com/allenai/molmospaces</a>); resolved per-episode strings come from each bench episode's <code>language.task_description</code>. 8 bench-task success thresholds and sim↔real numbers (R≈0.96, ρ=0.98 over 752 RoboArena pick tasks) from the tech report; model success rates (π₀/π₀-FAST/π₀.₅ on MSProc-1k; RING/DualVLN nav) are approximate report figures. Bench-task bar fills are illustrative geometry, not success rates &mdash; the badge is the real threshold.
  </footer>
</div>
<script>
const DATA = ''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const FAMCOL={pick:'--violet',place:'--cyan',articulate:'--amber',door:'--rust',navigate:'--green'};
function fc(f){var v=FAMCOL[f]||'--blue';return css(v);}

// ---------- 02 grammar catalog ----------
const T=DATA.templates;
let famFilter='all';
function renderGrammar(){
  const q=document.getElementById('search').value.toLowerCase().trim();
  let rows=T.filter(function(t){
    if(famFilter!=='all'&&t.family!==famFilter)return false;
    if(!q)return true;
    return (t.tmpl+' '+t.family+' '+t.bench+' '+t.examples.join(' ')+' '+t.cls).toLowerCase().indexOf(q)>=0;
  });
  function esc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
  function hl(s){return q?s.replace(new RegExp('('+esc(q)+')','ig'),'<mark>$1</mark>'):s;}
  function ph(s){return s.replace(/\{([^}]+)\}/g,'<span class="ph">{$1}</span>');}
  document.getElementById('countLine').textContent='Showing '+rows.length+' / '+T.length+' templates';
  document.getElementById('tasklist').innerHTML=rows.map(function(t){
    const col=fc(t.family);
    return '<details class="tcard"><summary>'
      +'<span class="dot" style="background:'+col+'"></span>'
      +'<span class="tmpl">'+ph(hl(t.tmpl))+'</span>'
      +'<span class="catpill">'+t.family+'</span>'
      +'<span class="catpill" style="border-color:'+col+';color:'+col+'">'+t.bench+'</span></summary>'
      +'<div class="body">'
      +'<div class="crit">'+hl(t.crit)+'</div>'
      +'<div class="clsname">class &middot; '+t.cls+'</div>'
      +'<div class="samp-h">resolved example instructions</div>'
      +'<div class="samp">'+t.examples.map(function(e){return '<div class="row">'+hl(e)+'</div>';}).join('')+'</div>'
      +'</div></details>';
  }).join('');
}
document.getElementById('search').addEventListener('input',renderGrammar);
Array.prototype.forEach.call(document.querySelectorAll('.chip[data-f]'),function(c){
  c.onclick=function(){
    Array.prototype.forEach.call(document.querySelectorAll('.chip[data-f]'),function(x){x.classList.remove('on');});
    c.classList.add('on');famFilter=c.dataset.f;renderGrammar();
  };
});
renderGrammar();

// ---------- 03 bench task bars ----------
(function(){
  const B=DATA.bench;
  document.getElementById('benchBars').innerHTML=B.map(function(b){
    const col=fc(b.family);
    return '<div class="bench-row"><div class="name" title="'+b.blurb+'">'+b.task+'</div>'
      +'<div class="track"><div class="fill" style="width:'+(b.prog*100)+'%;background:'+col+'"></div></div>'
      +'<div class="thr" style="color:'+col+'">'+b.thr+'</div></div>';
  }).join('');
})();

// ---------- 04 ecosystem donut (log-area so 6 robots stay visible vs 230k scenes) ----------
(function(){
  const F=DATA.eco.families;
  const segs=F.map(function(f){return {n:f.name,rows:f.rows,c:css(f.c),detail:f.detail};});
  // weight by log10(rows) for visible area, but show true rows in legend
  const w=segs.map(function(s){return Math.log10(s.rows+10);});
  const tot=w.reduce(function(a,b){return a+b;},0);
  let a0=-Math.PI/2,s='';const cx=84,cy=84,R=70,r=40;
  segs.forEach(function(seg,i){
    const a1=a0+w[i]/tot*6.283;const lp=(a1-a0)>Math.PI?1:0;
    function p(a,rad){return [cx+rad*Math.cos(a),cy+rad*Math.sin(a)];}
    const A=p(a0,R),Bp=p(a1,R),C=p(a1,r),D=p(a0,r);
    s+='<path d="M'+A[0]+' '+A[1]+' A'+R+' '+R+' 0 '+lp+' 1 '+Bp[0]+' '+Bp[1]+' L'+C[0]+' '+C[1]+' A'+r+' '+r+' 0 '+lp+' 0 '+D[0]+' '+D[1]+' Z" fill="'+seg.c+'" opacity="0.92"/>';
    a0=a1;
  });
  s+='<text x="84" y="80" text-anchor="middle" style="font-size:20px;fill:'+css('--ink')+';font-family:Fraunces;font-weight:900">1M</text>';
  s+='<text x="84" y="96" text-anchor="middle" style="font-size:9px;fill:'+css('--dim')+';font-family:Space Mono">ROWS</text>';
  document.getElementById('ecoDonut').innerHTML=s;
  function fmt(n){return n>=1000?(n/1000>=100?Math.round(n/1000)+'k':(n/1000).toFixed(1).replace(/\.0$/,'')+'k'):String(n);}
  document.getElementById('ecoLegend').innerHTML=segs.map(function(seg){
    return '<span class="r" title="'+seg.detail+'"><i style="background:'+seg.c+'"></i>'+seg.n+'<b>'+fmt(seg.rows)+'</b></span>';
  }).join('');
  // headline tiles
  document.getElementById('ecoHead').innerHTML=DATA.eco.headline.map(function(h){
    return '<div style="display:flex;align-items:baseline;gap:12px"><div style="font-family:Fraunces;font-weight:900;font-size:30px;line-height:1;color:'+css(h.c)+';min-width:90px">'+h.n+'</div>'
      +'<div style="font-family:Space Mono,monospace;font-size:11px;color:'+css('--dim')+';text-transform:uppercase;letter-spacing:.06em">'+h.lab+'</div></div>';
  }).join('');
})();

// ---------- 05 leaderboards ----------
function lbBars(elId,obj,col){
  const rows=obj.rows.slice().sort(function(a,b){return b.sr-a.sr;});
  const mx=100;
  document.getElementById(elId).innerHTML=rows.map(function(r){
    return '<div class="lb-row"><div class="name">'+r.model+'</div>'
      +'<div class="track"><div class="fill" style="width:'+(r.sr/mx*100)+'%;background:'+col+'"></div></div>'
      +'<div class="v" style="color:'+col+'">'+r.sr+'%</div></div>';
  }).join('');
}
lbBars('manipBars',DATA.leader.manip,css('--violet'));
lbBars('navBars',DATA.leader.nav,css('--green'));
document.getElementById('manipNote').textContent='MANIPULATION · '+DATA.leader.manip.note;
document.getElementById('navNote').textContent='NAVIGATION · '+DATA.leader.nav.note;
document.getElementById('axGrid').innerHTML=DATA.axes.map(function(a){
  return '<div class="axcard"><div class="an">'+a.axis+'</div><div class="ae">'+a.ex+'</div></div>';
}).join('');

// ---------- 06 word cloud (spiral packing) ----------
(function(){
  const cv=document.getElementById('cloud');const ctx=cv.getContext('2d');
  function draw(){
    const dpr=window.devicePixelRatio||1;const W=cv.clientWidth,H=280;
    cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const words=DATA.words;if(!words.length)return;
    const mx=words[0][1],mn=words[words.length-1][1];
    const pal=[css('--violet'),css('--cyan'),css('--amber'),css('--green'),css('--rust'),css('--ink')];
    const placed=[];
    words.forEach(function(w,i){
      const fs=13+(mx===mn?20:(w[1]-mn)/(mx-mn)*38);
      ctx.font=(fs>26?900:600)+' '+fs+'px Fraunces, serif';
      const tw=ctx.measureText(w[0]).width, th=fs*0.92, pad=2, cx=W/2, cy=H/2;
      for(let sp=0;sp<3000;sp++){const rr=sp*0.42,ang=sp*0.42;
        const x=cx+rr*Math.cos(ang)-tw/2, y=cy+rr*Math.sin(ang)+th/2;
        if(x<3||x+tw>W-3||y-th<3||y>H-3)continue;
        const box={x:x-pad,y:y-th-pad,w:tw+2*pad,h:th+2*pad};let ok=true;
        for(let k=0;k<placed.length;k++){const p=placed[k];if(box.x<p.x+p.w&&box.x+box.w>p.x&&box.y<p.y+p.h&&box.y+box.h>p.y){ok=false;break;}}
        if(ok){placed.push(box);ctx.fillStyle=pal[i%pal.length];ctx.fillText(w[0],x,y);break;}
      }
    });
  }
  draw();let t;window.addEventListener('resize',function(){clearTimeout(t);t=setTimeout(draw,200);});
})();
</script>
'''
open(f'{HERE}/molmospaces_dashboard.html','w').write(HTML)
print(f'wrote molmospaces_dashboard.html ({len(HTML)} bytes)')
