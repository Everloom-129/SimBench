#!/usr/bin/env python3
"""Builds robosuite_tasks.csv + robosuite_dashboard.html (blueprint style) —
an aggregation atlas for robosuite, the modular MuJoCo simulation framework &
benchmark that composes robots x grippers x controllers into standardized tasks.

All figures from robosuite (Zhu et al., 2020; arXiv:2009.12293,
"robosuite: A Modular Simulation Framework and Benchmark for Robot Learning")
and the v1.5 release docs (robosuite.ai, released 2024-10-28):
  - 9 standard benchmark environments: 6 single-arm (Block Lifting, Block
    Stacking, Pick-and-Place, Nut Assembly, Door Opening, Table Wiping) + 3
    two-arm (Two Arm Lifting, Two Arm Peg-In-Hole, Two Arm Handover).
  - Robot models out of the box: 6 single-arm fixed-base (Panda, Sawyer, IIWA,
    Jaco, Kinova3, UR5e), 1 bimanual (Baxter), 1 humanoid (GR1, + variants),
    2 mobile/legged (Spot, Tiago) = 10; "an additional 8 robots, 8 grippers,
    and 3 bases can be installed separately."
  - 9 gripper models (BD, Inspire Hands, Jaco 3-finger, Panda, Rethink,
    Robotiq-85, Robotiq-140, Robotiq 3-finger, Wiping).
  - Controllers: joint-space velocity, joint position, inverse kinematics,
    operational-space control (OSC), composite / whole-body control.
  - Two modeling/simulation APIs; multimodal sensing (RGB-D, force-torque,
    proprioception). v1.5 adds humanoids, custom robot composition, composite
    whole-body controllers, more teleop devices, photorealistic rendering.
  Built on MuJoCo; maintained by the ARISE Initiative.
"""
import json, csv, html as _h
HERE=__file__.rsplit('/',1)[0]

# 9 standard benchmark tasks. arms = single|two (drives colour). desc = one line.
TASKS=[
 {'name':'Block Lifting','arms':'single','desc':'Lift a single cube above a threshold height &mdash; the canonical sanity task.'},
 {'name':'Block Stacking','arms':'single','desc':'Pick one cube and stack it stably on top of another.'},
 {'name':'Pick-and-Place','arms':'single','desc':'Sort four objects from a bin into their matching target bins.'},
 {'name':'Nut Assembly','arms':'single','desc':'Fit square &amp; round nuts onto their corresponding pegs.'},
 {'name':'Door Opening','arms':'single','desc':'Turn the handle and swing a door open.'},
 {'name':'Table Wiping','arms':'single','desc':'Wipe markings off a whiteboard surface &mdash; contact-rich, sensor-driven.'},
 {'name':'Two Arm Lifting','arms':'two','desc':'Two arms lift a pot by both handles while keeping it level.'},
 {'name':'Two Arm Peg-In-Hole','arms':'two','desc':'Two arms coordinate to insert a peg held by one into a hole held by the other.'},
 {'name':'Two Arm Handover','arms':'two','desc':'One arm hands an object across to the other in a coordinated handoff.'},
]

# the modular stack — the composable axes that make robosuite an aggregator.
AXES=[
 {'name':'Robots','n':'10+','desc':'6 single-arm (Panda, Sawyer, IIWA, Jaco, Kinova3, UR5e) + Baxter (bimanual) + GR1 (humanoid) + Spot &amp; Tiago (mobile). +8 more installable.'},
 {'name':'Grippers','n':'9','desc':'Panda, Rethink, Robotiq-85 / 140 / 3-finger, Jaco 3-finger, BD, Inspire Hands, Wiping &mdash; any gripper on any compatible arm.'},
 {'name':'Controllers','n':'5','desc':'Joint-space velocity &amp; position, inverse kinematics, operational-space control (OSC), and composite whole-body control.'},
 {'name':'Sensing','n':'3','desc':'RGB-D cameras, force-torque measurements, and proprioception &mdash; multimodal observations out of the box.'},
]

# robot embodiments for the chip row. kind drives colour.
ROBOTS=[
 {'name':'Panda','kind':'arm'},
 {'name':'Sawyer','kind':'arm'},
 {'name':'IIWA','kind':'arm'},
 {'name':'Jaco','kind':'arm'},
 {'name':'Kinova3','kind':'arm'},
 {'name':'UR5e','kind':'arm'},
 {'name':'Baxter','kind':'bimanual'},
 {'name':'GR1','kind':'humanoid'},
 {'name':'Tiago','kind':'mobile'},
 {'name':'Spot','kind':'mobile'},
]

with open(f'{HERE}/robosuite_tasks.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['task','arms','description'])
    for t in TASKS:
        w.writerow([_h.unescape(t['name']),t['arms'],_h.unescape(t['desc'])])
print('wrote robosuite_tasks.csv',len(TASKS))

DATA={'tasks':TASKS,'axes':AXES,'robots':ROBOTS}
data_json=json.dumps(DATA,separators=(',',':'),ensure_ascii=False)
N_TASK=len(TASKS); N_SINGLE=sum(1 for t in TASKS if t['arms']=='single'); N_TWO=N_TASK-N_SINGLE

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>robosuite · Modular Framework &amp; Benchmark Atlas</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#080b12; --paper2:#0e131d; --card:#111722; --ink:#e6ecf5; --dim:#7e8aa0; --line:#1f293a;
    --rust:#e0673c; --cyan:#46c4c0; --blue:#5b8def; --violet:#9a7bff; --amber:#e0a93b; --green:#5bbf6a;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(820px 460px at 84% -8%, rgba(224,103,60,.13), transparent 60%),radial-gradient(820px 460px at 6% 3%, rgba(70,196,192,.08), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.45}
  .top:before{right:120px;border:1.5px solid var(--rust)}
  .top:after{right:30px;border:1.5px solid var(--cyan)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.2em;color:var(--rust);border:1px solid var(--rust);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.34em;text-transform:uppercase;color:var(--cyan)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(32px,5.5vw,60px);line-height:.96;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--rust),var(--amber));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:80ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(4,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1}
  .stat .num.r{color:var(--rust)} .stat .num.c{color:var(--cyan)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--amber);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.6;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:24px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  /* task cards */
  .task-grid{display:grid;grid-template-columns:1fr;gap:10px}
  @media(min-width:680px){.task-grid{grid-template-columns:1fr 1fr}}
  @media(min-width:980px){.task-grid{grid-template-columns:1fr 1fr 1fr}}
  .tcard{border:1.5px solid var(--line);border-left-width:4px;border-radius:11px;background:var(--paper2);padding:14px 16px}
  .tcard .th{display:flex;align-items:baseline;gap:8px}
  .tcard .nm{font-family:'Fraunces',serif;font-weight:900;font-size:16px;line-height:1.1}
  .tcard .ar{margin-left:auto;font-family:'Space Mono',monospace;font-size:8.5px;padding:2px 7px;border-radius:8px;border:1px solid var(--line);white-space:nowrap}
  .tcard .ds{font-size:11.5px;color:var(--dim);line-height:1.5;margin-top:8px}
  /* modular axis cards */
  .axis{display:grid;grid-template-columns:1fr;gap:12px}
  @media(min-width:720px){.axis{grid-template-columns:1fr 1fr}}
  .acard{border:1.5px solid var(--line);border-radius:11px;background:var(--paper2);padding:16px 18px;display:flex;gap:16px;align-items:flex-start}
  .acard .an{font-family:'Fraunces',serif;font-weight:900;font-size:30px;line-height:1;color:var(--rust);min-width:62px}
  .acard .at{font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--cyan)}
  .acard .ad{font-size:12px;color:var(--dim);line-height:1.55;margin-top:6px}
  /* robot chips */
  .chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
  .chip{font-family:'Space Mono',monospace;font-size:11px;padding:5px 11px;border-radius:18px;border:1.5px solid var(--line);background:var(--paper2)}
  .chip .k{font-size:8.5px;color:var(--dim);margin-left:6px;text-transform:uppercase;letter-spacing:.06em}
  .chip.more{color:var(--dim);border-style:dashed}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:12px;letter-spacing:.06em}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--blue)} footer code{color:var(--cyan)}
  .langtoggle{position:fixed;top:14px;right:14px;z-index:9999;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#e9edf4;background:rgba(20,26,36,.82);border:1.5px solid #46c4c0;border-radius:9px;padding:7px 13px;text-decoration:none;backdrop-filter:blur(6px);transition:background .15s,color .15s,transform .15s}
  .langtoggle:hover{background:#46c4c0;color:#0a0c10;transform:translateY(-1px)}
</style>
<a class="langtoggle" href="robosuite_dashboard_cn.html" title="切换到中文版">中文</a>
<div class="shell">
  <header class="top">
    <div class="stamp">FRAMEWORK · MuJoCo</div>
    <div class="kick">Modular Simulation Framework &amp; Benchmark</div>
    <h1>robosuite<br><em>Modular Atlas</em></h1>
    <div class="byline" style="font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2"><b style="color:var(--ink);font-weight:600">Jie Wang</b> · <a href="https://everloom-129.github.io/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">everloom-129.github.io</a> · GRASP Lab, UPenn &nbsp;·&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">Claude Code</a> &nbsp;·&nbsp; <span style="color:var(--ink)">2026.6.2</span></div>
    <p class="lede">Where ManiSkill3 aggregates task <i>domains</i> behind one GPU engine, <b>robosuite</b> aggregates <b>modular components</b>: a MuJoCo-based framework whose modeling API composes any <b>robot &times; gripper &times; controller</b> into standardized tasks. It ships <b>''' + str(N_TASK) + r''' standard benchmark environments</b> (''' + str(N_SINGLE) + r''' single-arm + ''' + str(N_TWO) + r''' two-arm), <b>10+ robot embodiments</b> (arms, bimanual, humanoid &amp; mobile bases), <b>9 grippers</b>, and a stack of controllers from joint-space to <b>whole-body control</b> &mdash; the de-facto substrate for robomimic, MimicGen, and many VLA pipelines.</p>
    <div class="statbar">
      <div class="stat"><div class="num r">''' + str(N_TASK) + r'''</div><div class="lab">standard tasks</div></div>
      <div class="stat"><div class="num c">10+</div><div class="lab">robot embodiments</div></div>
      <div class="stat"><div class="num">9</div><div class="lab">gripper models</div></div>
      <div class="stat"><div class="num">MuJoCo</div><div class="lab">physics · v1.5</div></div>
    </div>
  </header>

  <div class="note">
    <b>What "aggregator" means here.</b> robosuite does not migrate other benchmarks &mdash; it is a <b>modular construction kit</b>. Two APIs (modeling + simulation) let you swap the <code>robot</code>, <code>gripper</code>, and <code>controller</code> of any task independently, so the same Door-Opening environment can run a Panda with OSC or a GR1 humanoid under whole-body control. That composability is why it underpins downstream datasets &amp; benchmarks (robomimic, MimicGen) rather than competing with them.
  </div>

  <!-- 01 STANDARD TASKS -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>The ''' + str(N_TASK) + r''' standard tasks</h2><span class="desc">''' + str(N_SINGLE) + r''' single-arm · ''' + str(N_TWO) + r''' two-arm</span></div>
    <div class="task-grid" id="taskGrid"></div>
  </section>

  <!-- 02 MODULAR STACK -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>The modular stack</h2><span class="desc">compose · don't rebuild</span></div>
    <div class="panel"><div class="axis" id="axisGrid"></div></div>
  </section>

  <!-- 03 EMBODIMENTS -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>Robot embodiments</h2><span class="desc">10+ out of the box · +8 installable</span></div>
    <div class="panel">
      <div class="lbl">// any of these drops into any compatible task &mdash; see the robosuite robot gallery for the full set</div>
      <div class="chips" id="robotChips"></div>
    </div>
  </section>

  <footer>
    SOURCE · robosuite: <i>A Modular Simulation Framework and Benchmark for Robot Learning</i>, Zhu, Wong, Mandlekar, Mart&iacute;n-Mart&iacute;n, Joshi, Lin, Nasiriany, Zhu, 2020 (<a href="https://arxiv.org/abs/2009.12293">arXiv:2009.12293</a>) · <a href="https://robosuite.ai/">robosuite.ai</a> · <a href="https://github.com/ARISE-Initiative/robosuite">code</a> · built on <a href="https://mujoco.org/">MuJoCo</a>, maintained by the ARISE Initiative. Figures (9 standard environments, 10 out-of-the-box robots + 8 installable, 9 grippers, controller &amp; sensing modalities, v1.5 features) from the paper and the v1.5 release docs (released 2024-10-28). Task / axis groupings are summaries for navigation, not robosuite-reported taxonomy labels.
  </footer>
</div>
<script>
const DATA=''' + data_json + r''';
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const ARMCOL={single:css('--cyan'),two:css('--violet')};
const ARMLAB={single:'single-arm',two:'two-arm'};

// 01 — task cards (single-arm first, then two-arm)
(function(){
  const order=['single','two'];
  const sorted=DATA.tasks.slice().sort(function(a,b){return order.indexOf(a.arms)-order.indexOf(b.arms);});
  document.getElementById('taskGrid').innerHTML=sorted.map(function(t){
    const col=ARMCOL[t.arms]||css('--dim');
    return '<div class="tcard" style="border-left-color:'+col+'"><div class="th">'+
      '<span class="nm">'+t.name+'</span>'+
      '<span class="ar" style="color:'+col+';border-color:'+col+'">'+ARMLAB[t.arms]+'</span></div>'+
      '<div class="ds">'+t.desc+'</div></div>';
  }).join('');
})();

// 02 — modular axis cards
(function(){
  document.getElementById('axisGrid').innerHTML=DATA.axes.map(function(a){
    return '<div class="acard"><div class="an">'+a.n+'</div><div><div class="at">'+a.name+'</div><div class="ad">'+a.desc+'</div></div></div>';
  }).join('');
})();

// 03 — embodiment chips
(function(){
  const KCOL={arm:css('--cyan'),bimanual:css('--blue'),humanoid:css('--violet'),mobile:css('--green')};
  let h=DATA.robots.map(function(r){
    const col=KCOL[r.kind]||css('--dim');
    return '<span class="chip" style="border-color:'+col+'">'+r.name+'<span class="k" style="color:'+col+'">'+r.kind+'</span></span>';
  }).join('');
  h+='<span class="chip more">+ 8 more …</span>';
  document.getElementById('robotChips').innerHTML=h;
})();
</script>
'''
open(f'{HERE}/robosuite_dashboard.html','w').write(HTML)
print('wrote robosuite_dashboard.html',len(HTML),'bytes')
