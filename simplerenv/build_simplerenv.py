#!/usr/bin/env python3
"""Builds simplerenv_tasks.csv + simplerenv_dashboard.html (+ _cn.html), blueprint style.

Task names, env IDs and the verbatim language instructions are from the SimplerEnv repo
(simpler-env/SimplerEnv, Li et al. arXiv 2405.05941, CoRL 2024). Per-task success matrices
are verbatim from the SpatialVLA result tables (Qu et al. arXiv 2501.15830, RSS 2025), which
consolidate SimplerEnv real-to-sim numbers across policies.

The full task catalog (section 01) lists all four Google-Robot tasks and all four WidowX/Bridge
tasks with their instruction strings. The result matrices show only the tasks the consolidated
tables report per-task numbers for: Google Robot drops `place_in_closed_drawer` (≈0 for nearly
every policy, omitted by HPT/TraceVLA/SpatialVLA), so its per-task matrix has 3 columns.
"""
import json, csv
HERE = __file__.rsplit('/', 1)[0]

# ============================================================================
# FULL TASK CATALOG — robot, display name, env_id, verbatim instruction, eval setups,
# in_matrix = whether the consolidated result tables report a per-task number for it.
# Source: simpler-env/SimplerEnv repo (arXiv 2405.05941).
# ============================================================================
CATALOG = [
 ('Google Robot','Pick Coke Can','google_robot_pick_coke_can','pick coke can','visual_matching;variant_aggregation',True),
 ('Google Robot','Move Near','google_robot_move_near','move {obj} near {obj}','visual_matching;variant_aggregation',True),
 ('Google Robot','Open/Close Drawer','google_robot_open_drawer · google_robot_close_drawer','open drawer / close drawer','visual_matching;variant_aggregation',True),
 ('Google Robot','Place in Closed Drawer','google_robot_place_in_closed_drawer','place apple in closed top drawer','visual_matching;variant_aggregation',False),
 ('WidowX (Bridge)','Put Spoon on Towel','widowx_spoon_on_towel','put spoon on towel','visual_matching',True),
 ('WidowX (Bridge)','Put Carrot on Plate','widowx_carrot_on_plate','put carrot on plate','visual_matching',True),
 ('WidowX (Bridge)','Stack Green on Yellow','widowx_stack_cube','stack green cube on yellow cube','visual_matching',True),
 ('WidowX (Bridge)','Put Eggplant in Basket','widowx_put_eggplant_in_basket','put eggplant in basket','visual_matching',True),
]

# heatmap task columns = the in-matrix subset, in catalog order
GTASKS = [c[1] for c in CATALOG if c[0]=='Google Robot' and c[5]]      # 3 tasks
WTASKS = [c[1] for c in CATALOG if c[0]=='WidowX (Bridge)' and c[5]]   # 4 tasks

# ---- Google Robot (Visual Matching + Variant Aggregation), per-task + avg ----
GOOGLE=[
 # model, [VM per-task], VM#avg, [VA per-task], VA#avg
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
gmap={g[0]:g[2] for g in GOOGLE}
wmap={m:ov for (m,_,ov) in WIDOWX}
GAP=[{'m':m,'g':gmap[m],'w':wmap[m]} for m in wmap if m in gmap and gmap[m] is not None]

# ---- CSV (full catalog, now with env_id + verbatim instruction) ----
with open(f'{HERE}/simplerenv_tasks.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['robot','task','env_id','instruction','eval_setups','in_result_matrix'])
    for robot,name,env,instr,setups,inm in CATALOG:
        w.writerow([robot,name,env,instr,setups,'yes' if inm else 'no'])
print('wrote simplerenv_tasks.csv',f'({len(CATALOG)} tasks)')

GOOGLE_J=[{'m':m,'vm':vm,'vmavg':va,'va':vapt,'vaavg':vaa} for (m,vm,va,vapt,vaa) in GOOGLE]
WIDOWX_J=[{'m':m,'s':s,'avg':a} for (m,s,a) in WIDOWX]
CATALOG_J=[{'robot':r,'name':n,'env':e,'instr':i,'inMatrix':inm} for (r,n,e,i,_,inm) in CATALOG]
DATA={'gtasks':GTASKS,'wtasks':WTASKS,'catalog':CATALOG_J,'google':GOOGLE_J,'widowx':WIDOWX_J,'gap':GAP}
data_json=json.dumps(DATA,separators=(',',':'),ensure_ascii=False)

# ============================================================================
# language bundles
# ============================================================================
EN=dict(
 lang='en', other='simplerenv_dashboard_cn.html', toggle='中文', toggle_title='切换到中文版',
 title='SimplerEnv · Real-to-Sim VLA Evaluation Atlas',
 kick='SimplerEnv · Real-to-Sim Manipulation Policy Evaluation',
 h1b='Real-to-Sim Atlas',
 lede='SimplerEnv evaluates real-robot manipulation policies <b>in simulation</b> by closing the visual gap to two real setups &mdash; Google\'s <b style="color:var(--google)">RT-1 robot</b> and the <b style="color:var(--widowx)">WidowX + Bridge</b> arm &mdash; so that sim success <i>predicts</i> real success without running hardware. Two eval modes: <b>Visual Matching</b> (overlay real backgrounds, match textures) and <b>Variant Aggregation</b> (sweep lighting / background / distractors). This atlas renders the per-task success matrices and exposes the headline finding: <b>capability does not transfer across embodiments</b>.',
 s1='real robot setups', s2='manipulation tasks', s3='eval modes · VM / VA', s4='policies compared', s5='configurations',
 note='<b>Why real-to-sim.</b> Running a VLA on a real arm for hundreds of trials is slow and irreproducible. SimplerEnv builds digital twins of two real labs so a policy\'s <b>sim</b> success rate tracks its <b>real</b> success rate. The catch: a policy tuned for one embodiment\'s action space and camera can be near-SOTA on Google Robot yet near-zero on WidowX. Numbers below are <b>success %</b>; the WidowX figures are the <i>task-success</i> column (a separate <i>grasp</i> sub-metric exists). <code>Place in Closed Drawer</code> (instruction: <i>&ldquo;place apple in closed top drawer&rdquo;</i>) is listed in the catalog but dropped from the result matrices, following HPT/TraceVLA/SpatialVLA, since almost every policy scores ~0.',
 sec1='The two embodiments', sec1d='different arms · different action spaces · their task instructions',
 grb='RT-1 mobile manipulator · fractal data', wrb='6-DoF tabletop arm · BridgeData V2',
 sec2='The embodiment gap', sec2d='Google Robot vs WidowX · same policy, two bodies',
 gaplbl='EACH LINE = ONE POLICY · left dot = Google Robot (VM avg) · right dot = WidowX (overall) · longer line = worse transfer',
 gaptxt='<b style="color:var(--rust)">OpenVLA</b> is the cautionary tale: <b style="color:var(--ink)">27.7%</b> on Google Robot but <b style="color:var(--ink)">1.0%</b> on WidowX &mdash; a known controller/action-space artifact, not a real-world ability gap. Even the best policy, <b style="color:var(--green)">SpatialVLA</b>, drops from <b style="color:var(--ink)">71.9% &rarr; 34.4%</b>. The lesson the survey draws: <b style="color:var(--ink)">always report per-embodiment</b>.',
 sec3='Google Robot · per-task matrix', sec3d='Visual Matching vs Variant Aggregation',
 sec4='WidowX (Bridge) · per-task matrix', sec4d='task-success % · sorted by overall',
 wtxt='<b style="color:var(--ink)">Put Eggplant in Basket</b> is the easy one (SpatialVLA fine-tuned hits 100%); <b style="color:var(--ink)">Stack Green on Yellow</b> resists everyone. The whole WidowX board sits far below Google Robot &mdash; Bridge is the harder embodiment to transfer to.',
 footer='SOURCE · Task names, env IDs &amp; instruction strings: SimplerEnv repo <code>simpler-env/SimplerEnv</code> (Li et al., <a href="https://arxiv.org/abs/2405.05941">arXiv 2405.05941</a>, CoRL 2024). Per-task success matrices verbatim from the SpatialVLA result tables (Qu et al., <a href="https://arxiv.org/abs/2501.15830">arXiv 2501.15830</a>, RSS 2025), which consolidate SimplerEnv numbers for RT-1/RT-1-X/RT-2-X, Octo, OpenVLA, RoboVLM, HPT, TraceVLA and SpatialVLA. Google Robot reports Visual Matching &amp; Variant Aggregation; WidowX shows task-success (a grasp sub-metric is also tracked upstream). OpenVLA\'s ~1% WidowX result is a controller artifact flagged in the SimplerEnv repo, not real-world ability.',
 th_policy='policy', avg='#AVG', omit='catalog only — omitted from matrices',
)
CN=dict(
 lang='cn', other='simplerenv_dashboard.html', toggle='EN', toggle_title='Switch to English',
 title='SimplerEnv · 真实到仿真 VLA 评估图谱',
 kick='SimplerEnv · 真实到仿真操作策略评估',
 h1b='真实到仿真图谱',
 lede='SimplerEnv 通过缩小与两套真实平台的视觉差距，<b>在仿真中</b>评估真实机器人操作策略 &mdash; Google 的 <b style="color:var(--google)">RT-1 机器人</b> 与 <b style="color:var(--widowx)">WidowX + Bridge</b> 机械臂 &mdash; 从而让仿真成功率能够<i>预测</i>真实成功率，而无需运行实机硬件。两种评估模式：<b>Visual Matching</b>（叠加真实背景、匹配纹理）与 <b>Variant Aggregation</b>（扫描光照 / 背景 / 干扰物）。本图谱呈现逐任务的成功率矩阵，并揭示了核心发现：<b>能力无法在不同本体（embodiment）间迁移</b>。',
 s1='真实机器人平台', s2='操作任务', s3='评估模式 · VM / VA', s4='对比策略', s5='配置组合',
 note='<b>为何采用真实到仿真。</b> 在真实机械臂上运行 VLA 进行数百次试验既缓慢又难以复现。SimplerEnv 为两个真实实验室构建数字孪生（digital twin），使策略的<b>仿真</b>成功率能够追踪其<b>真实</b>成功率。问题在于：针对某一本体的动作空间与相机调优的策略，在 Google Robot 上可能接近 SOTA，而在 WidowX 上却几乎为零。下方数字均为<b>成功率 %</b>；WidowX 数据取<i>任务成功（task-success）</i>列（另有独立的<i>抓取（grasp）</i>子指标）。<code>Place in Closed Drawer</code>（指令：<i>&ldquo;place apple in closed top drawer&rdquo;</i>）已列入任务目录，但遵循 HPT/TraceVLA/SpatialVLA 的做法从结果矩阵中省略，因为几乎所有策略在该任务上的得分都约为 0。',
 sec1='两种本体', sec1d='不同的机械臂 · 不同的动作空间 · 各自的任务指令',
 grb='RT-1 移动操作机器人 · fractal 数据', wrb='6-DoF 桌面机械臂 · BridgeData V2',
 sec2='本体差异', sec2d='Google Robot vs WidowX · 同一策略，两种本体',
 gaplbl='每条线 = 一个策略 · 左点 = Google Robot（VM 均值）· 右点 = WidowX（总体）· 线越长 = 迁移越差',
 gaptxt='<b style="color:var(--rust)">OpenVLA</b> 是一个警示案例：在 Google Robot 上达到 <b style="color:var(--ink)">27.7%</b>，但在 WidowX 上仅 <b style="color:var(--ink)">1.0%</b> &mdash; 这是已知的控制器/动作空间问题（artifact），而非真实世界中的能力差距。即便是最强的策略 <b style="color:var(--green)">SpatialVLA</b>，也从 <b style="color:var(--ink)">71.9% &rarr; 34.4%</b> 大幅下滑。综述得出的教训是：<b style="color:var(--ink)">始终按本体分别报告</b>。',
 sec3='Google Robot · 逐任务矩阵', sec3d='Visual Matching vs Variant Aggregation',
 sec4='WidowX (Bridge) · 逐任务矩阵', sec4d='任务成功率 % · 按总体排序',
 wtxt='<b style="color:var(--ink)">Put Eggplant in Basket</b> 是最简单的任务（SpatialVLA 微调版达到 100%）；<b style="color:var(--ink)">Stack Green on Yellow</b> 则对所有策略都构成挑战。整个 WidowX 面板的成绩远低于 Google Robot &mdash; Bridge 是更难迁移到的本体。',
 footer='SOURCE · 任务名称、env ID 与指令字符串：SimplerEnv 仓库 <code>simpler-env/SimplerEnv</code>（Li et al., <a href="https://arxiv.org/abs/2405.05941">arXiv 2405.05941</a>, CoRL 2024）。逐任务成功率矩阵逐字取自 SpatialVLA 结果表（Qu et al., <a href="https://arxiv.org/abs/2501.15830">arXiv 2501.15830</a>, RSS 2025），其中整合了 RT-1/RT-1-X/RT-2-X、Octo、OpenVLA、RoboVLM、HPT、TraceVLA 与 SpatialVLA 的 SimplerEnv 数据。Google Robot 报告 Visual Matching 与 Variant Aggregation；WidowX 展示任务成功率（上游另有跟踪一个 grasp 子指标）。OpenVLA 在 WidowX 上约 1% 的结果是 SimplerEnv 仓库中标注的控制器问题（artifact），而非真实世界能力。',
 th_policy='策略', avg='#均值', omit='仅目录 — 矩阵中省略',
)

TEMPLATE=r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
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
  .byline{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2}
  .byline a,.byline b{color:var(--ink)} .byline a{text-decoration:underline}
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
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto;text-align:right}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .setupwrap{display:grid;gap:18px}
  @media(min-width:760px){.setupwrap{grid-template-columns:1fr 1fr}}
  .setup{border:1.5px solid var(--line);border-radius:12px;padding:18px;background:var(--paper2)}
  .setup h3{font-family:'Fraunces',serif;font-size:20px;margin:0 0 4px}
  .setup .rb{font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
  .setup ul{margin:0;padding-left:18px;list-style:none} .setup li{font-size:13px;color:var(--ink);margin:9px 0 9px -18px;line-height:1.45}
  .setup li .nm{font-weight:600}
  .setup li .instr{display:block;font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-top:2px}
  .setup li .omit{font-family:'Space Mono',monospace;font-size:9.5px;color:var(--widowx);letter-spacing:.04em}
  .setup li .env{font-family:'Space Mono',monospace;font-size:9.5px;color:var(--teal)}
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
  .langtoggle{position:fixed;top:14px;right:14px;z-index:9999;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#e8ebf1;background:rgba(20,24,33,.82);border:1.5px solid #3fb6a8;border-radius:9px;padding:7px 13px;text-decoration:none;backdrop-filter:blur(6px);transition:background .15s,color .15s,transform .15s}
  .langtoggle:hover{background:#3fb6a8;color:#0a0c11;transform:translateY(-1px)}
</style>
<a class="langtoggle" href="__OTHER__" title="__TOGGLE_TITLE__">__TOGGLE__</a>
<div class="shell">
  <header class="top">
    <div class="stamp">REAL &rarr; SIM</div>
    <div class="kick">__KICK__</div>
    <h1>SimplerEnv<br><em>__H1B__</em></h1>
    <div class="byline"><b>Jie Wang</b> &middot; <a href="https://everloom-129.github.io/" target="_blank" rel="noopener">everloom-129.github.io</a> &middot; GRASP Lab, UPenn &nbsp;&middot;&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener">Claude Code</a> &nbsp;&middot;&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
    <p class="lede">__LEDE__</p>
    <div class="statbar">
      <div class="stat"><div class="num g">2</div><div class="lab">__S1__</div></div>
      <div class="stat"><div class="num w">8</div><div class="lab">__S2__</div></div>
      <div class="stat"><div class="num">2</div><div class="lab">__S3__</div></div>
      <div class="stat"><div class="num">13</div><div class="lab">__S4__</div></div>
      <div class="stat"><div class="num">~137</div><div class="lab">__S5__</div></div>
    </div>
  </header>

  <div class="note">__NOTE__</div>

  <!-- 01 SETUPS -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>__SEC1__</h2><span class="desc">__SEC1D__</span></div>
    <div class="setupwrap">
      <div class="setup" style="border-color:var(--google)">
        <h3>Google Robot</h3><div class="rb" style="color:var(--google)">__GRB__</div>
        <ul id="gtaskList"></ul>
      </div>
      <div class="setup" style="border-color:var(--widowx)">
        <h3>WidowX + Bridge</h3><div class="rb" style="color:var(--widowx)">__WRB__</div>
        <ul id="wtaskList"></ul>
      </div>
    </div>
  </section>

  <!-- 02 EMBODIMENT GAP -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>__SEC2__</h2><span class="desc">__SEC2D__</span></div>
    <div class="panel">
      <div class="lbl">__GAPLBL__</div>
      <svg id="gap" viewBox="0 0 760 360"></svg>
      <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">__GAPTXT__</div>
    </div>
  </section>

  <!-- 03 GOOGLE HEATMAP -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>__SEC3__</h2><span class="desc">__SEC3D__</span></div>
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
    <div class="sec-h"><span class="idx">04</span><h2>__SEC4__</h2><span class="desc">__SEC4D__</span></div>
    <div class="panel"><div class="heatwrap"><table class="heat" id="wheat"></table></div>
    <div style="margin-top:14px;font-size:12.5px;line-height:1.55;color:var(--dim)">__WTXT__</div>
    </div>
  </section>

  <footer>__FOOTER__</footer>
</div>
<script>
const DATA=__DATA__;
const TXT=__TXT__;
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();

// ---- 01 task catalog with verbatim instructions ----
function taskLi(c){
  const env='<span class="env">'+c.env+'</span>';
  const omit=c.inMatrix?'':' <span class="omit">'+TXT.omit+'</span>';
  return '<li><span class="nm">'+c.name+'</span>'+omit+'<span class="instr">&ldquo;'+c.instr+'&rdquo; &middot; '+env+'</span></li>';
}
document.getElementById('gtaskList').innerHTML=DATA.catalog.filter(c=>c.robot==='Google Robot').map(taskLi).join('');
document.getElementById('wtaskList').innerHTML=DATA.catalog.filter(c=>c.robot==='WidowX (Bridge)').map(taskLi).join('');

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
  let h='<tr><th class="rowh">'+TXT.th_policy+'</th>'+tasks.map(t=>`<th>${t}</th>`).join('')+`<th>${TXT.avg}</th></tr>`;
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
  let h='<tr><th class="rowh">'+TXT.th_policy+'</th>'+tasks.map(t=>`<th>${t}</th>`).join('')+`<th>${TXT.avg}</th></tr>`;
  rows.forEach(m=>{
    h+=`<tr><th class="rowh">${m.m}</th>`;
    m.s.forEach(v=>{const c=cellCol(v);h+=`<td style="background:${c}">${Math.round(v)}</td>`;});
    h+=`<td class="avg">${m.avg.toFixed(1)}</td></tr>`;
  });
  document.getElementById('wheat').innerHTML=h;
})();
</script>
'''

def render(L):
    txt_js=json.dumps({k:L[k] for k in ('th_policy','avg','omit')}, ensure_ascii=False)
    repl={
      '__TITLE__':L['title'],'__OTHER__':L['other'],'__TOGGLE__':L['toggle'],'__TOGGLE_TITLE__':L['toggle_title'],
      '__KICK__':L['kick'],'__H1B__':L['h1b'],'__LEDE__':L['lede'],
      '__S1__':L['s1'],'__S2__':L['s2'],'__S3__':L['s3'],'__S4__':L['s4'],'__S5__':L['s5'],
      '__NOTE__':L['note'],'__SEC1__':L['sec1'],'__SEC1D__':L['sec1d'],'__GRB__':L['grb'],'__WRB__':L['wrb'],
      '__SEC2__':L['sec2'],'__SEC2D__':L['sec2d'],'__GAPLBL__':L['gaplbl'],'__GAPTXT__':L['gaptxt'],
      '__SEC3__':L['sec3'],'__SEC3D__':L['sec3d'],'__SEC4__':L['sec4'],'__SEC4D__':L['sec4d'],'__WTXT__':L['wtxt'],
      '__FOOTER__':L['footer'],'__DATA__':data_json,'__TXT__':txt_js,
    }
    html=TEMPLATE
    for k,v in repl.items():
        html=html.replace(k,v)
    return html

for L,fn in [(EN,'simplerenv_dashboard.html'),(CN,'simplerenv_dashboard_cn.html')]:
    out=render(L)
    open(f'{HERE}/{fn}','w').write(out)
    print('wrote',fn,len(out),'bytes')
