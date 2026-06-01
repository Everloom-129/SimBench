#!/usr/bin/env python3
"""Regenerates vla_benchmark_dashboard.html — the cross-benchmark survey — with in-depth
analysis synthesized from the per-benchmark atlases. Reads real parsed data from the
sibling CSVs and embeds leaderboard numbers traced to origin papers."""
import csv, json, re, os
from collections import Counter
HERE=os.path.dirname(os.path.abspath(__file__))
def P(*a): return os.path.join(HERE,*a)

# ---------------- 1. instruction corpus (REAL, from atlases) ----------------
corpus=[]
for r in csv.DictReader(open(P('calvin','calvin_tasks.csv'))):
    corpus += [s.strip() for s in r['all_instructions'].split('|')]
for r in csv.DictReader(open(P('libero','libero_tasks.csv'))):
    corpus.append(r['instruction'])
corpus=[c for c in corpus if c]
STOP=set("the a an and in it on of to up an into onto off at front is be with your you this that it's its for from down over under as".split())
VERB=set("open put pick place push turn move lift rotate stack close insert screw take reach press sweep grasp pull slide store hold turn-on serve set put-down".split())
SPAT=set("top middle near left right front side between back bottom inside center upper lower behind".split())
COLOR=set("green yellow blue red pink black white orange purple".split())
tok=Counter(); verbtok=0; alltok=0
for s in corpus:
    for w in re.findall(r"[a-z]+", s.lower()):
        if w in STOP or len(w)<2: continue
        alltok+=1; tok[w]+=1
        if w in VERB: verbtok+=1
top=tok.most_common(48)
def cat(w): return 'verb' if w in VERB else 'color' if w in COLOR else 'spatial' if w in SPAT else 'object'
cloud=[{'w':w,'c':c,'cat':cat(w)} for w,c in top]
verbshare=round(100*sum(tok[w] for w in tok if w in VERB)/max(1,alltok))
top12verbshare=round(100*sum(c for w,c in tok.most_common() if w in VERB)/max(1,alltok))  # all verbs share
# share of tokens covered by the single most common 10 content words
top10share=round(100*sum(c for _,c in tok.most_common(10))/max(1,alltok))
corpusN=len(corpus); vocabN=len(tok)

# ---------------- 2. LIBERO-Plus factor retention + model totals (REAL csv) -------------
lp_rows=list(csv.DictReader(open(P('libero-plus','libero_plus.csv'))))
LP_FACTORS=['Camera','Robot','Language','Light','Background','Noise','Layout']
lp_factor=[{'f':f,'retain':round(sum(float(r[f]) for r in lp_rows)/len(lp_rows),1)} for f in LP_FACTORS]
lp_factor.sort(key=lambda x:x['retain'])  # most damaging first
lp_total={r['model']:float(r['Total']) for r in lp_rows}

# ---------------- 3. COLOSSEUM factor degradation (REAL csv) ----------------
col_rows=list(csv.DictReader(open(P('colosseum','colosseum.csv'))))
col_factor=[{'f':r['perturbation_factor'].replace('_',' '),'group':r['group'],
             'deg':float(r['degradation_pct'])} for r in col_rows]
col_factor.sort(key=lambda x:-x['deg'])

# ---------------- 4. reality ladder (REAL csv) ----------------
ladder=[{'b':r['benchmark'],'tier':r['realism_tier'],
         'v':float(r['best_reported_success_pct']),'best':r['best_model']}
        for r in csv.DictReader(open(P('sim2real','sim2real.csv')))]
ladder.sort(key=lambda x:-x['v'])

# ---------------- 5. memory frontier (REAL csv) ----------------
mem=list(csv.DictReader(open(P('memory','memory_benchmarks.csv'))))
mem_names=[m['benchmark'] for m in mem]

# ---------------- 6. embedded leaderboard constants (traced to origin papers) ----------
# LIBERO clean 4-suite (OpenVLA-OFT paper 2502.19645, filtered protocol)
libero_clean={'OpenVLA':[84.7,88.4,79.2,53.7],'OpenVLA-OFT':[96.2,98.3,96.2,90.7],
              'π0':[96.8,98.8,95.8,85.2],'π0-FAST':[96.4,96.8,88.6,60.2],
              'Octo':[78.9,85.7,84.6,51.1],'SpatialVLA':[88.2,89.9,78.6,55.5]}
def avg(x): return round(sum(x)/len(x),1)
# capability(x)=LIBERO clean avg ; robustness(y)=LIBERO-Plus Total — both this session's sources
scatter=[]
for m,key in [('OpenVLA','OpenVLA'),('π0-FAST','π0-Fast'),('π0','π0'),('OpenVLA-OFT','OpenVLA-OFT')]:
    scatter.append({'n':m,'x':avg(libero_clean[m]),'y':lp_total[key]})
robust_gap=round(sum(p['x']-p['y'] for p in scatter)/len(scatter),1)

# CALVIN long-horizon decay (GR-1 2312.13139 ; 3D Diffuser Actor 2402.10885 Tbl IV)
decay={'x':[1,2,3,4,5],'series':[
  {'n':'GR-1 · ABCD→D (seen env)','v':[94.9,89.6,84.4,78.9,73.1],'c':'var(--green)'},
  {'n':'GR-1 · ABC→D (unseen)','v':[85.4,71.2,59.6,49.7,40.1],'c':'var(--cyan)'},
  {'n':'RoboFlamingo · ABC→D','v':[82.4,61.9,46.6,33.1,23.5],'c':'var(--amber)'},
  {'n':'HULC · ABC→D','v':[41.8,16.5,5.7,1.9,1.1],'c':'var(--hot)'},
]}

# benchmark × model heatmap (all values traced to this session's sources)
heat_cols=["L·Spatial","L·Object","L·Goal","L·Long","SE·Google","SE·WidowX","RLBench-18","LIBERO-Plus"]
heat_rows=[
 {"n":"OpenVLA",     "v":[84.7,88.4,79.2,53.7,27.7,1.0,None,15.6]},
 {"n":"OpenVLA-OFT", "v":[96.2,98.3,96.2,90.7,None,None,None,69.6]},
 {"n":"π0",          "v":[96.8,98.8,95.8,85.2,None,None,None,53.6]},
 {"n":"π0-FAST",     "v":[96.4,96.8,88.6,60.2,None,None,None,61.6]},
 {"n":"Octo",        "v":[78.9,85.7,84.6,51.1,16.8,16.0,None,None]},
 {"n":"SpatialVLA",  "v":[88.2,89.9,78.6,55.5,75.1,42.7,None,None]},
 {"n":"RVT-2",       "v":[None,None,None,None,None,None,81.4,None]},
]
# SimplerEnv embodiment gap (SpatialVLA consolidation 2501.15830)
embgap=[{"n":"OpenVLA","g":27.7,"w":1.0},{"n":"Octo","g":16.8,"w":16.0},
        {"n":"RoboVLM","g":56.3,"w":13.5},{"n":"SpatialVLA","g":75.1,"w":42.7}]
# simulator backbone
sims=[{"n":"MuJoCo / robosuite","v":5,"c":"var(--hot)","x":"LIBERO · LIBERO-Plus · LIBERO-PRO · RoboCasa · Meta-World"},
      {"n":"SAPIEN / ManiSkill","v":3,"c":"var(--amber)","x":"SimplerEnv · ManiSkill · RoboTwin"},
      {"n":"CoppeliaSim / PyRep","v":2,"c":"var(--cyan)","x":"RLBench · COLOSSEUM"},
      {"n":"PyBullet","v":1,"c":"var(--violet)","x":"CALVIN"},
      {"n":"OmniGibson","v":1,"c":"#d98cff","x":"BEHAVIOR-1K"},
      {"n":"Real / real2sim","v":3,"c":"var(--green)","x":"ManipArena · RoboChallenge · RoboMemArena"}]

DATA={'cloud':cloud,'ladder':ladder,'scatter':scatter,'lpFactor':lp_factor,'colFactor':col_factor[:8],
      'decay':decay,'heatCols':heat_cols,'heatRows':heat_rows,'embgap':embgap,'sims':sims,
      'mem':mem_names,'stats':{'corpusN':corpusN,'vocabN':vocabN,'verbshare':verbshare,
      'top10share':top10share,'robustGap':robust_gap,
      'cleanBest':max(l['v'] for l in ladder if l['tier']=='clean-sim'),
      'realBest':max(l['v'] for l in ladder if l['tier']=='real-robot')}}
dj=json.dumps(DATA,separators=(',',':'),ensure_ascii=False)

HTML=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VLA Simulation Benchmarks — In-Depth Visual Survey</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{--bg:#0c0e12;--panel:#13161d;--panel2:#171b24;--ink:#e7e3d8;--dim:#8b8f9c;--line:#262b36;
    --hot:#ff5436;--amber:#f5b840;--cyan:#46c4c0;--violet:#9a7bff;--green:#74c476;font-synthesis:none;}
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans',sans-serif}
  body{background-image:radial-gradient(1200px 600px at 85% -5%, rgba(154,123,255,.08), transparent 60%),radial-gradient(900px 500px at -5% 10%, rgba(255,84,54,.07), transparent 55%);padding:clamp(18px,4vw,56px);max-width:1280px;margin:0 auto;}
  .kicker{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:var(--hot)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,72px);line-height:.96;margin:.18em 0 .1em;letter-spacing:-.01em}
  h1 em{font-style:italic;color:var(--amber)}
  .sub{color:var(--dim);max-width:66ch;font-size:15.5px;line-height:1.6}
  .sub b{color:var(--ink);font-weight:600}
  .statstrip{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:26px;border:1px solid var(--line);border-radius:14px;overflow:hidden}
  @media(min-width:760px){.statstrip{grid-template-columns:repeat(5,1fr)}}
  .ss{padding:15px 18px;border-right:1px solid var(--line);background:var(--panel2)}
  .ss:last-child{border-right:none}
  .ss .n{font-family:'Fraunces',serif;font-weight:900;font-size:25px;line-height:1;color:var(--amber)}
  .ss .l{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-top:6px;line-height:1.4}
  .grid{display:grid;gap:18px;margin-top:22px}
  @media(min-width:880px){.grid{grid-template-columns:1fr 1fr}}
  .card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:16px;padding:22px 22px 24px;position:relative;overflow:hidden}
  .card.wide{grid-column:1/-1}
  .card h2{font-family:'Fraunces',serif;font-weight:600;font-size:22px;margin:0 0 2px;letter-spacing:-.01em}
  .card .note{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);letter-spacing:.04em;margin-bottom:16px;line-height:1.55}
  .tag{position:absolute;top:18px;right:18px;font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);border:1px solid var(--line);padding:3px 8px;border-radius:20px}
  .insight{font-size:13.5px;line-height:1.6;color:var(--ink);margin-top:16px;border-left:2px solid var(--amber);padding-left:14px}
  .insight b{color:var(--amber)} .insight i{color:var(--cyan);font-style:normal}
  #cloud{width:100%;height:380px;display:block;border-radius:10px}
  .legendrow{display:flex;flex-wrap:wrap;gap:14px;margin-top:14px;font-family:'Space Mono',monospace;font-size:11px;color:var(--dim)}
  .legendrow span{display:inline-flex;align-items:center;gap:6px}
  .dot{width:10px;height:10px;border-radius:50%;display:inline-block}
  #scatter{width:100%;height:430px;display:block}
  .axislbl{font-family:'Space Mono',monospace;font-size:10px;fill:var(--dim)}
  .pt-lbl{font-family:'IBM Plex Sans';font-size:11px;fill:var(--ink);font-weight:600}
  table.heat{border-collapse:separate;border-spacing:3px;width:100%;font-size:12.5px}
  table.heat th{font-family:'Space Mono',monospace;font-weight:400;font-size:10px;color:var(--dim);text-align:center;padding:4px;vertical-align:bottom}
  table.heat th.row{text-align:left;width:120px;color:var(--ink);font-weight:600}
  table.heat td{text-align:center;border-radius:6px;padding:9px 4px;font-family:'Space Mono',monospace;font-weight:700;color:#0c0e12}
  table.heat td.na{background:#1c2029!important;color:var(--dim)!important;font-weight:400}
  .ladder{display:flex;flex-direction:column;gap:7px}
  .lrow{display:grid;grid-template-columns:188px 1fr 42px;align-items:center;gap:12px}
  .lrow .name{font-size:12.5px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .lrow .name small{color:var(--dim);font-family:'Space Mono',monospace;font-size:9px}
  .ltrack{height:18px;background:#1c2029;border-radius:5px;overflow:hidden}
  .lfill{height:100%;border-radius:5px}
  .lrow .v{font-family:'Space Mono',monospace;font-size:12px;font-weight:700;text-align:right}
  .lgnd{display:flex;flex-wrap:wrap;gap:7px 16px;margin-top:14px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim)}
  .lgnd span{display:flex;align-items:center;gap:6px} .lgnd i{width:11px;height:11px;border-radius:3px}
  .bar-wrap{display:flex;flex-direction:column;gap:9px;margin-top:4px}
  .bar-row{display:grid;grid-template-columns:128px 1fr 40px;align-items:center;gap:12px}
  .bar-row .name{font-size:12px;color:var(--ink);font-family:'Space Mono',monospace}
  .track{height:16px;background:#1c2029;border-radius:8px;overflow:hidden}
  .fill{height:100%;border-radius:8px}
  .bar-row .val{font-family:'Space Mono',monospace;font-size:12px;text-align:right}
  #decay{width:100%;height:330px;display:block}
  .dl{display:flex;flex-wrap:wrap;gap:7px 16px;margin-top:10px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim)}
  .dl span{display:flex;align-items:center;gap:6px} .dl i{width:14px;height:3px;border-radius:2px}
  #donut{flex:0 0 168px} .donut-wrap{display:flex;gap:20px;align-items:center;flex-wrap:wrap}
  .donut-legend{display:flex;flex-direction:column;gap:9px;font-size:12px}
  .donut-legend span{display:flex;align-items:baseline;gap:9px} .donut-legend b{font-family:'Space Mono',monospace;color:var(--dim);font-weight:400;margin-left:auto}
  .donut-legend small{display:block;color:var(--dim);font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.02em}
  .memlist{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
  .memchip{font-family:'Space Mono',monospace;font-size:11px;color:var(--violet);border:1px solid var(--line);border-radius:9px;padding:5px 10px}
  .takeaway{grid-column:1/-1;background:none;border:1px dashed var(--line);border-radius:16px;padding:24px 26px}
  .takeaway h2{color:var(--amber);font-family:'Fraunces',serif;font-weight:600;font-size:23px;margin:0 0 10px}
  .takeaway ol{margin:0;padding-left:20px;line-height:1.65;color:var(--ink);font-size:14px}
  .takeaway li{margin-bottom:10px} .takeaway b{color:var(--hot)} .takeaway code{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .cta{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:var(--panel2);border:1px solid var(--line);border-left:3px solid var(--cyan);border-radius:14px;padding:18px 22px}
  .cta .t{font-family:'Fraunces',serif;font-size:19px;color:var(--ink)} .cta .d{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-top:3px}
  .cta a{font-family:'Space Mono',monospace;font-size:12px;letter-spacing:.04em;color:#0c0e12;background:var(--cyan);text-decoration:none;padding:11px 18px;border-radius:10px;font-weight:700;white-space:nowrap}
  footer{margin-top:30px;color:var(--dim);font-family:'Space Mono',monospace;font-size:10.5px;line-height:1.7;border-top:1px solid var(--line);padding-top:18px}
  footer a{color:var(--cyan)}
  .swatch-coral{background:var(--hot)}.swatch-amber{background:var(--amber)}.swatch-cyan{background:var(--cyan)}.swatch-violet{background:var(--violet)}.swatch-green{background:var(--green)}
</style>

<div class="kicker">Simulation Manipulation Benchmarks · VLA Evaluation</div>
<h1>What the robots are<br><em>actually told to do.</em></h1>
<div class="byline" style="font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2"><b style="color:var(--ink);font-weight:600">Jie Wang</b> · <a href="https://everloom-129.github.io/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">everloom-129.github.io</a> · GRASP Lab, UPenn &nbsp;·&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener" style="color:var(--ink);text-decoration:underline">Claude Code</a> &nbsp;·&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
<p class="sub">A deep visual synthesis across <b>16 benchmark atlases</b> — LIBERO, CALVIN, RLBench, Meta-World, SimplerEnv, LIBERO-Plus / PRO, COLOSSEUM, the memory frontier, and the sim↔real bridge. Every chart below is computed from the <b>actual parsed task data</b> and leaderboard numbers in those atlases, each traced to its origin paper. The throughline: <b>standard benchmarks are saturated and optimistic; the moment you perturb the view, move the object, change the embodiment, or extend the horizon, success collapses.</b></p>

<div class="statstrip" id="statstrip"></div>

<div class="grid">

  <div class="card wide">
    <span class="tag">real corpus</span>
    <h2>The language VLAs are trained on is tiny &amp; imperative</h2>
    <div class="note" id="cloudNote"></div>
    <canvas id="cloud"></canvas>
    <div class="legendrow">
      <span><i class="dot swatch-coral"></i>verbs</span>
      <span><i class="dot swatch-amber"></i>objects</span>
      <span><i class="dot swatch-cyan"></i>spatial</span>
      <span><i class="dot swatch-violet"></i>colors</span>
    </div>
    <div class="insight" id="cloudInsight"></div>
  </div>

  <div class="card wide">
    <span class="tag">cross-benchmark</span>
    <h2>The reality gradient</h2>
    <div class="note">best reported success per benchmark · colored by how <i>real</i> the evaluation is · the more real the test, the lower the score</div>
    <div class="ladder" id="ladder"></div>
    <div class="lgnd" id="ladderLegend"></div>
    <div class="insight" id="ladderInsight"></div>
  </div>

  <div class="card wide">
    <span class="tag">measured, not illustrative</span>
    <h2>Capability ≠ robustness</h2>
    <div class="note">x = clean LIBERO 4-suite average · y = LIBERO-Plus total (same model under 7 perturbations) · the drop below the diagonal is the robustness debt</div>
    <svg id="scatter" viewBox="0 0 900 430"></svg>
    <div class="insight" id="scatterInsight"></div>
  </div>

  <div class="card wide">
    <span class="tag">two independent benchmarks agree</span>
    <h2>What actually breaks VLAs</h2>
    <div class="note">LIBERO-Plus: mean success <i>retained</i> under each perturbation (lower = more damaging, avg over 11 models) · COLOSSEUM: success <i>lost</i> per factor (avg over 5 models × 20 tasks)</div>
    <div style="display:grid;gap:22px" id="breakWrap"></div>
    <div class="insight" id="breakInsight"></div>
  </div>

  <div class="card wide">
    <span class="tag">CALVIN · chained instructions</span>
    <h2>The horizon tax</h2>
    <div class="note">success vs. number of language instructions completed in a row · seen vs. unseen environment</div>
    <svg id="decay" viewBox="0 0 880 330"></svg>
    <div class="dl" id="decayLegend"></div>
    <div class="insight" id="decayInsight"></div>
  </div>

  <div class="card wide">
    <span class="tag">origin-paper values</span>
    <h2>Benchmark × model success heatmap</h2>
    <div class="note">capability suites + the embodiment columns + the LIBERO-Plus robustness total in one matrix · green high → red low · "—" = not reported in cited source</div>
    <div id="heat"></div>
    <div class="insight" id="heatInsight"></div>
  </div>

  <div class="card">
    <h2>Simulator backbone</h2>
    <div class="note">which engine powers each surveyed benchmark family</div>
    <div class="donut-wrap"><svg id="donut" viewBox="0 0 180 180"></svg><div class="donut-legend" id="donutLegend"></div></div>
  </div>

  <div class="card">
    <span class="tag">2026 · emerging</span>
    <h2>The next frontier: memory</h2>
    <div class="note">non-Markovian / memory-dependent benchmarks — the axis today's VLAs are not built for</div>
    <div class="memlist" id="memlist"></div>
    <div class="insight">These ask the policy to <b>remember</b> — event order, off-screen locations, what it already did, what happened last trial. Standard VLAs are stateless per frame; this is where the field is headed and where current models have no real baseline yet.</div>
  </div>

  <div class="takeaway">
    <h2>What the data says</h2>
    <ol id="takeaways"></ol>
  </div>

  <div class="cta">
    <div><div class="t">Explore every benchmark in depth</div><div class="d">16 interactive single-file atlases · task catalogs, leaderboards, perturbation matrices</div></div>
    <a href="index.html">open the atlas index →</a>
  </div>

</div>

<footer id="footer"></footer>

<script>
const DATA=''' + dj + r''';
const getCSS=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const S=DATA.stats;

/* stat strip */
document.getElementById('statstrip').innerHTML=[
 [S.corpusN.toLocaleString(),'real instructions parsed'],
 [S.vocabN,'unique content words'],
 [S.verbshare+'%','tokens are just verbs'],
 [S.cleanBest+'%','best on clean sim'],
 [S.realBest+'%','best on a real robot'],
].map(x=>`<div class="ss"><div class="n">${x[0]}</div><div class="l">${x[1]}</div></div>`).join('');

/* notes + insights text */
document.getElementById('cloudNote').textContent=`tokenized from ${S.corpusN.toLocaleString()} verbatim CALVIN + LIBERO instructions · stopwords removed · size ∝ frequency`;
document.getElementById('cloudInsight').innerHTML=`Just <b>${S.verbshare}% of all tokens are verbs</b>, and the ten commonest content words cover <b>${S.top10share}%</b> of everything said to these robots. The distribution is a handful of imperatives (<i>put · pick · open · place</i>) over a handful of nouns (<i>bowl · drawer · block · plate</i>) — a templated micro-language, not natural instruction.`;

/* ===== word cloud (spiral) ===== */
(function(){
  const cv=document.getElementById('cloud'),DPR=Math.min(devicePixelRatio||1,2),W=cv.clientWidth,H=380;
  cv.width=W*DPR;cv.height=H*DPR;const ctx=cv.getContext('2d');ctx.scale(DPR,DPR);
  const words=DATA.cloud,max=words[0].c,min=words[words.length-1].c;
  const colof={verb:getCSS('--hot'),object:getCSS('--amber'),spatial:getCSS('--cyan'),color:getCSS('--violet')};
  const placed=[];
  function fits(x,y,w,h){if(x<4||y<4||x+w>W-4||y+h>H-4)return false;
    for(const p of placed)if(x<p.x+p.w&&x+w>p.x&&y<p.y+p.h&&y+h>p.y)return false;return true;}
  words.forEach((o,i)=>{const t=(o.c-min)/(max-min||1),size=Math.round(13+t*44);o.size=size;
    ctx.font=`${i<3?900:700} ${size}px Fraunces, serif`;const m=ctx.measureText(o.w),w=m.width+8,h=size*1.02;
    let a=i*1.1,r=0,x=0,y=0,ok=false;
    for(let k=0;k<2800;k++){x=W/2+r*Math.cos(a)-w/2;y=H/2+r*Math.sin(a)*0.62-h/2;if(fits(x,y,w,h)){ok=true;break;}a+=0.34;r+=0.52;}
    if(ok){placed.push({x,y,w,h});o.x=x;o.y=y;}});
  words.forEach((o,i)=>{if(o.x==null)return;ctx.font=`${i<3?900:700} ${o.size}px Fraunces, serif`;ctx.textBaseline='top';
    ctx.fillStyle=colof[o.cat];ctx.globalAlpha=0.6+0.4*((o.size-13)/44);ctx.fillText(o.w,o.x+4,o.y);});
  ctx.globalAlpha=1;
})();

/* ===== reality ladder ===== */
(function(){
  const TIERC={'clean-sim':getCSS('--cyan'),'perturbed-sim':getCSS('--violet'),'real2sim':getCSS('--amber'),'real-robot':getCSS('--green')};
  const TIERL={'clean-sim':'clean sim','perturbed-sim':'perturbed sim','real2sim':'real→sim','real-robot':'real robot'};
  document.getElementById('ladder').innerHTML=DATA.ladder.map(r=>{const c=TIERC[r.tier];
    return `<div class="lrow"><div class="name">${r.b} <small>${r.best}</small></div>
      <div class="ltrack"><div class="lfill" style="width:${r.v}%;background:${c}"></div></div>
      <div class="v" style="color:${c}">${r.v}</div></div>`;}).join('');
  document.getElementById('ladderLegend').innerHTML=Object.keys(TIERC).map(t=>`<span><i style="background:${TIERC[t]}"></i>${TIERL[t]}</span>`).join('');
  document.getElementById('ladderInsight').innerHTML=`Clean simulators report <b>95–97%</b>; the same task on a physical arm tops out near <b>${S.realBest}%</b>, and stacking COLOSSEUM's 14 perturbations leaves <b>4%</b>. Sim is a forecast — the real number is roughly <i>half</i>.`;
})();

/* ===== scatter ===== */
(function(){
  const svg=document.getElementById('scatter'),W=900,H=430,P=54;
  const x=v=>P+(v/100)*(W-P-26),y=v=>H-P-(v/100)*(H-P-26);let s='';
  for(let g=0;g<=100;g+=25){s+=`<line x1="${x(g)}" y1="${y(0)}" x2="${x(g)}" y2="${y(100)}" stroke="var(--line)"/>`;
    s+=`<line x1="${x(0)}" y1="${y(g)}" x2="${x(100)}" y2="${y(g)}" stroke="var(--line)"/>`;
    s+=`<text class="axislbl" x="${x(g)}" y="${y(0)+16}" text-anchor="middle">${g}</text>`;
    s+=`<text class="axislbl" x="${x(0)-8}" y="${y(g)+3}" text-anchor="end">${g}</text>`;}
  s+=`<line x1="${x(0)}" y1="${y(0)}" x2="${x(100)}" y2="${y(100)}" stroke="var(--cyan)" stroke-dasharray="5 6" opacity=".5"/>`;
  s+=`<text class="axislbl" x="${x(72)}" y="${y(80)}" fill="var(--cyan)" opacity=".8">robust = capable</text>`;
  s+=`<text class="axislbl" x="${W/2}" y="${H-8}" text-anchor="middle" style="font-size:11px">clean LIBERO capability (%)</text>`;
  s+=`<text class="axislbl" transform="translate(15,${H/2}) rotate(-90)" text-anchor="middle" style="font-size:11px">robustness — LIBERO-Plus total (%)</text>`;
  DATA.scatter.forEach(p=>{const c=getCSS('--hot');
    s+=`<line x1="${x(p.x)}" y1="${y(p.x)}" x2="${x(p.x)}" y2="${y(p.y)}" stroke="${c}" opacity=".3" stroke-dasharray="3 3"/>`;
    s+=`<circle cx="${x(p.x)}" cy="${y(p.y)}" r="8" fill="${c}"/>`;
    s+=`<text class="pt-lbl" x="${x(p.x)+12}" y="${y(p.y)+4}">${p.n} <tspan fill="var(--dim)" font-size="10">${p.x}→${p.y}</tspan></text>`;});
  svg.innerHTML=s;
  document.getElementById('scatterInsight').innerHTML=`Every model sits far below the diagonal — an average <b>${S.robustGap}-point robustness debt</b>. And the ranking <i>flips</i>: <b>π0 (94.2 clean)</b> is <i>less</i> robust (53.6) than <b>π0-FAST (85.5 clean → 61.6)</b>. A higher leaderboard number does not mean a more deployable policy.`;
})();

/* ===== what breaks VLAs ===== */
(function(){
  const lpmax=Math.max(...DATA.lpFactor.map(f=>f.retain));
  function lprow(f){const c=f.retain<40?getCSS('--hot'):f.retain<60?getCSS('--amber'):getCSS('--green');
    return `<div class="bar-row"><div class="name">${f.f}</div><div class="track"><div class="fill" style="width:${f.retain}%;background:${c}"></div></div><div class="val" style="color:${c}">${f.retain}</div></div>`;}
  const colmax=Math.max(...DATA.colFactor.map(f=>f.deg));
  function colrow(f){const c=getCSS('--hot');
    return `<div class="bar-row"><div class="name">${f.f}</div><div class="track"><div class="fill" style="width:${f.deg/colmax*100}%;background:${c};opacity:.85"></div></div><div class="val" style="color:${c}">−${f.deg}</div></div>`;}
  document.getElementById('breakWrap').innerHTML=
    `<div><div class="note" style="margin-bottom:8px;color:var(--cyan)">LIBERO-Plus · % SUCCESS RETAINED (lower = worse)</div><div class="bar-wrap">${DATA.lpFactor.map(lprow).join('')}</div></div>`+
    `<div><div class="note" style="margin-bottom:8px;color:var(--cyan)">COLOSSEUM · % SUCCESS LOST per factor (top 8)</div><div class="bar-wrap">${DATA.colFactor.map(colrow).join('')}</div></div>`;
  document.getElementById('breakInsight').innerHTML=`Two benchmarks built on different simulators converge: <b>geometry breaks policies</b> — camera viewpoint and robot starting pose are the most destructive (LIBERO-Plus retains only ~27–32%), and object color / distractors top COLOSSEUM. <b>Language barely matters</b> (~65% retained) — LIBERO-PRO shows why: models <i>ignore the instruction</i>, reproducing a memorized motion, so a paraphrase changes nothing while a moved object drops them to <code>0%</code>.`;
})();

/* ===== horizon decay ===== */
(function(){
  const svg=document.getElementById('decay'),W=880,H=330,padL=46,padR=150,padT=16,padB=42;
  const X=i=>padL+i*(W-padL-padR)/4, Y=v=>padT+(100-v)*(H-padT-padB)/100;let s='';
  for(let g=0;g<=100;g+=20){s+=`<line x1="${padL}" y1="${Y(g)}" x2="${W-padR}" y2="${Y(g)}" stroke="var(--line)"/>`;
    s+=`<text class="axislbl" x="${padL-7}" y="${Y(g)+3}" text-anchor="end">${g}</text>`;}
  for(let i=0;i<5;i++)s+=`<text class="axislbl" x="${X(i)}" y="${H-padB+17}" text-anchor="middle">${i+1} task${i?'s':''} in a row</text>`;
  DATA.decay.series.forEach(se=>{const c=getCSS(se.c.replace('var(','').replace(')',''))||se.c;
    let d=se.v.map((v,i)=>`${i?'L':'M'}${X(i)} ${Y(v)}`).join(' ');
    s+=`<path d="${d}" fill="none" stroke="${c}" stroke-width="2.5" stroke-linejoin="round"/>`;
    se.v.forEach((v,i)=>s+=`<circle cx="${X(i)}" cy="${Y(v)}" r="3.4" fill="${c}"/>`);
    s+=`<text x="${X(4)+6}" y="${Y(se.v[4])+3}" class="axislbl" style="fill:${c};font-size:9.5px">${se.v[4]}%</text>`;});
  svg.innerHTML=s;
  document.getElementById('decayLegend').innerHTML=DATA.decay.series.map(se=>{const c=getCSS(se.c.replace('var(','').replace(')',''))||se.c;
    return `<span><i style="background:${c}"></i>${se.n}</span>`;}).join('');
  document.getElementById('decayInsight').innerHTML=`Success compounds downward with every chained step, and the <b>unseen-environment penalty</b> widens it: GR-1 holds <b>73%</b> at five tasks in a seen scene but <b>40%</b> zero-shot, while an older policy (HULC) falls to <b>1%</b>. Long-horizon and out-of-distribution are multiplicative, not additive.`;
})();

/* ===== heatmap ===== */
(function(){
  function color(v){if(v==null)return null;const t=v/100;
    return `rgb(${Math.round(255*(1-t)+116*t)},${Math.round(84*(1-t)+196*t)},${Math.round(54*(1-t)+118*t)})`;}
  let h='<table class="heat"><tr><th class="row"></th>';
  DATA.heatCols.forEach(b=>h+=`<th>${b}</th>`);h+='</tr>';
  DATA.heatRows.forEach(m=>{h+=`<tr><th class="row">${m.n}</th>`;
    m.v.forEach(v=>h+=v==null?`<td class="na">—</td>`:`<td style="background:${color(v)}">${v}</td>`);h+='</tr>';});
  document.getElementById('heat').innerHTML=h+'</table>';
  document.getElementById('heatInsight').innerHTML=`The capability block (left) is a wall of green — solved. The robustness column (right) and the WidowX embodiment column are where the green drains out: <b>OpenVLA goes 84.7→1.0</b> across the row. One matrix, the whole problem.`;
})();

/* ===== donut ===== */
(function(){
  const svg=document.getElementById('donut'),tot=DATA.sims.reduce((a,b)=>a+b.v,0);let a0=-Math.PI/2,s='';
  const cx=90,cy=90,R=72,r=44;
  DATA.sims.forEach(seg=>{const a1=a0+(seg.v/tot)*Math.PI*2,lp=(a1-a0)>Math.PI?1:0;
    const p=(an,rad)=>[cx+rad*Math.cos(an),cy+rad*Math.sin(an)];
    const[x0,y0]=p(a0,R),[x1,y1]=p(a1,R),[x2,y2]=p(a1,r),[x3,y3]=p(a0,r);
    s+=`<path d="M${x0},${y0} A${R},${R} 0 ${lp} 1 ${x1},${y1} L${x2},${y2} A${r},${r} 0 ${lp} 0 ${x3},${y3} Z" fill="${seg.c}"/>`;a0=a1;});
  s+=`<text x="90" y="86" text-anchor="middle" style="font-family:Fraunces;font-weight:900;font-size:26px;fill:var(--ink)">${tot}</text>`;
  s+=`<text x="90" y="104" text-anchor="middle" style="font-family:Space Mono;font-size:8px;fill:var(--dim);letter-spacing:.1em">FAMILIES</text>`;
  svg.innerHTML=s;
  document.getElementById('donutLegend').innerHTML=DATA.sims.map(seg=>
    `<span><i class="dot" style="background:${seg.c}"></i><span>${seg.n}<small>${seg.x}</small></span><b>${seg.v}</b></span>`).join('');
})();

/* ===== memory list ===== */
document.getElementById('memlist').innerHTML=DATA.mem.map(m=>`<span class="memchip">${m}</span>`).join('');

/* ===== takeaways ===== */
document.getElementById('takeaways').innerHTML=[
 `The instruction language is a <b>templated micro-vocabulary</b> — ${S.verbshare}% of tokens are verbs and 10 words cover ${S.top10share}% of everything said. VLAs are tested on a sliver of natural language.`,
 `Standard LIBERO is <b>saturated</b> (OpenVLA-OFT 97.1%, π0 94.2%) yet collapses under perturbation — an average <b>${S.robustGap}-point robustness debt</b>, and as low as <code>0%</code> when an object is moved (LIBERO-PRO).`,
 `<b>Capability and robustness rank differently.</b> π0 outscores π0-FAST on clean LIBERO but is <i>less</i> robust. Never report a clean number alone — pair it with LIBERO-Plus / PRO or COLOSSEUM.`,
 `<b>Geometry, not appearance, is the enemy.</b> Camera viewpoint and robot initial pose are the most destructive factors across two independent benchmarks; color/texture/lighting and even <i>language</i> are comparatively cheap (because models largely ignore the instruction).`,
 `<b>Embodiment doesn't transfer.</b> OpenVLA scores 27.7% on SimplerEnv Google-Robot and 1.0% on WidowX. Always report per-embodiment.`,
 `<b>The horizon tax is multiplicative.</b> Chaining five instructions and moving to an unseen scene compounds failure; and memory-dependent tasks (the 2026 frontier) are a capability today's stateless VLAs don't have.`,
].map(t=>`<li>${t}</li>`).join('');

/* ===== footer ===== */
document.getElementById('footer').innerHTML=`SOURCES · LIBERO suites + clean leaderboard: Liu et al. 2023 (<a href="https://arxiv.org/abs/2306.03310">2306.03310</a>), OpenVLA-OFT Kim et al. 2025 (<a href="https://arxiv.org/abs/2502.19645">2502.19645</a>) · SimplerEnv: Li et al. CoRL 2024 (<a href="https://arxiv.org/abs/2405.05941">2405.05941</a>) + SpatialVLA consolidation (<a href="https://arxiv.org/abs/2501.15830">2501.15830</a>) · CALVIN decay: GR-1 (<a href="https://arxiv.org/abs/2312.13139">2312.13139</a>), 3D Diffuser Actor (<a href="https://arxiv.org/abs/2402.10885">2402.10885</a>) · RLBench: RVT-2 (<a href="https://arxiv.org/abs/2406.08545">2406.08545</a>) · LIBERO-Plus (<a href="https://arxiv.org/abs/2510.13626">2510.13626</a>) · LIBERO-PRO (<a href="https://arxiv.org/abs/2510.03827">2510.03827</a>) · THE COLOSSEUM (<a href="https://arxiv.org/abs/2402.08191">2402.08191</a>) · RoboChallenge (<a href="https://arxiv.org/abs/2510.17950">2510.17950</a>) · ManipArena (<a href="https://arxiv.org/abs/2603.28545">2603.28545</a>).<br>
CAVEATS · Word cloud + vocabulary stats computed live from ${S.corpusN.toLocaleString()} parsed CALVIN+LIBERO instructions. Scatter and factor charts computed from the LIBERO-Plus / COLOSSEUM tables in this collection. Heatmap mixes protocols (rollouts, seeds, control mode differ) and is for orientation, not head-to-head ranking. OpenVLA's ~1% WidowX is a controller artifact flagged in the SimplerEnv repo. 2026 arXiv IDs are preliminary.`;
</script>
'''
open(P('vla_benchmark_dashboard.html'),'w').write(HTML)
print('wrote vla_benchmark_dashboard.html',len(HTML),'bytes ·',
      f'corpus={corpusN} vocab={vocabN} verbshare={verbshare}% robustGap={DATA["stats"]["robustGap"]}')
