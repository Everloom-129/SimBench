#!/usr/bin/env python3
"""Builds robolab_tasks.csv + robolab_dashboard.html (blueprint style).

RoboLab (NVIDIA Seattle Robotics Lab) is a high-fidelity Isaac-Sim benchmark for
*analysis* of task-generalist policies. Its signature design choices, all surfaced here:
  (1) RoboLab-120 — 120 tabletop manipulation tasks, parsed from RoboLab/tasks.md.
  (2) Three language-specificity tiers per task: vague / default / specific.
  (3) Three difficulty labels: simple / moderate / complex.
  (4) Per-task attribute tags rolled up into three competency axes
      — visual (color/semantics/size), procedural (affordance/reorientation/stacking),
        relational (conjunction/counting/spatial).
  (5) A 1,200-eval leaderboard (120 tasks x 10 episodes) scoring SR%, subtask-progress
      Score, and end-effector motion-quality metrics (EE Speed, EE SPARC).

Two data sources:
  - The 120-task catalog: parsed from the committed RoboLab/tasks.md (auto-generated
    from the RoboLab task metadata CSV; "Last updated: 2026-05-07").
  - The leaderboard + protocol numbers: hardcoded below with inline citations to the
    project leaderboard page (research.nvidia.com/labs/srl/projects/robolab/leaderboard.html).
"""
import json, csv, re, os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# PARSE the 120-task catalog from tasks.md (the committed metadata table).
# ============================================================================
def parse_tasks(md_path):
    rows = []
    with open(md_path) as f:
        for line in f:
            line = line.rstrip('\n')
            # data rows start with "| " and reference a benchmark/ python file
            if not line.startswith('|'):
                continue
            if 'benchmark/' not in line:
                continue
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if len(cells) != 7:
                continue
            name_cell, scene_cell, instr_cell, ep, attrs, subs, diff = cells

            m = re.match(r'(\w+)\s*\(benchmark/([^)]+)\)', name_cell)
            cls = m.group(1) if m else name_cell
            pyfile = m.group(2) if m else ''

            usda = ''
            mu = re.search(r'<br>\s*([\w./-]+\.usda)', scene_cell)
            if mu:
                usda = mu.group(1)

            instr = {}
            for part in instr_cell.split('<br>'):
                mp = re.match(r'\*\*(\w+):\*\*\s*(.*)', part.strip())
                if mp:
                    instr[mp.group(1)] = mp.group(2).strip()

            attr_list = [a.strip() for a in attrs.split(',') if a.strip()]
            rows.append({
                'cls': cls,
                'file': pyfile,
                'scene': usda,
                'default': instr.get('default', ''),
                'vague': instr.get('vague', ''),
                'specific': instr.get('specific', ''),
                'ep': int(ep) if ep.isdigit() else 0,
                'attrs': attr_list,
                'subs': int(subs) if subs.isdigit() else 0,
                'diff': diff.strip(),
            })
    return rows

TASKS = parse_tasks(os.path.join(HERE, 'tasks.md'))
assert len(TASKS) == 120, f'expected 120 tasks, parsed {len(TASKS)}'

# ----------------------------------------------------------------------------
# Competency-axis mapping. Source: leaderboard page —
#   Visual: color, semantics, size
#   Procedural: affordance, reorientation, stacking
#   Relational: conjunction, counting, spatial
# (sorting / vague carry no axis on the page; we keep them as auxiliary tags.)
# ----------------------------------------------------------------------------
AXIS_OF = {
    'color':'visual','semantics':'visual','size':'visual',
    'affordance':'procedural','reorientation':'procedural','stacking':'procedural',
    'conjunction':'relational','counting':'relational','spatial':'relational',
}
for t in TASKS:
    axes = sorted({AXIS_OF[a] for a in t['attrs'] if a in AXIS_OF})
    t['axes'] = axes if axes else ['uncategorized']

# attribute frequency + difficulty / subtask / duration distributions (for JS to use directly)
attr_counts = Counter(a for t in TASKS for a in t['attrs'])
diff_counts = Counter(t['diff'] for t in TASKS)
axis_counts = Counter(ax for t in TASKS for ax in t['axes'])

# ============================================================================
# LEADERBOARD — verbatim from the RoboLab leaderboard page.
# research.nvidia.com/labs/srl/projects/robolab/leaderboard.html
# RoboLab-120 · 120 tasks x 10 episodes = 1,200 evaluations. Metrics:
#   SR% binary success · Score = subtask-progress x100 · EE Speed cm/s · EE SPARC smoothness.
# Policy type: WAM = world-action (world-model) policy · VLA = vision-language-action.
# ============================================================================
LEADER = [  # overall RoboLab-120 ranking
 {"rank":1,"model":"Cosmos3-Nano-Policy","type":"WAM","sr":36.8,"score":51.9,"speed":7.13,"sparc":-5.99},
 {"rank":2,"model":"π0.5",               "type":"VLA","sr":28.0,"score":43.4,"speed":5.35,"sparc":-8.34},
 {"rank":3,"model":"DreamZero",          "type":"WAM","sr":25.7,"score":39.8,"speed":3.64,"sparc":-6.41},
 {"rank":4,"model":"π0-FAST",            "type":"VLA","sr":15.5,"score":26.9,"speed":4.60,"sparc":-9.63},
 {"rank":5,"model":"GR00T N1.6",         "type":"VLA","sr":7.2, "score":17.1,"speed":4.30,"sparc":-6.87},
 {"rank":6,"model":"π0",                 "type":"VLA","sr":5.0, "score":12.2,"speed":4.18,"sparc":-9.49},
 {"rank":7,"model":"paligemma-binning",  "type":"VLA","sr":3.4, "score":9.9, "speed":1.93,"sparc":-16.52},
]

# SR% by difficulty tier (trial counts from the page) — leaderboard page "By Difficulty Level"
DIFF_BREAK = {
 "simple":  {"trials":640,"rows":[("Cosmos3-Nano-Policy",40.6),("π0.5",29.7),("DreamZero",26.1),("π0-FAST",20.2),("GR00T N1.6",8.8),("π0",7.2),("paligemma-binning",3.4)]},
 "moderate":{"trials":390,"rows":[("Cosmos3-Nano-Policy",35.4),("π0.5",31.5),("DreamZero",30.0),("π0-FAST",13.3),("GR00T N1.6",7.9),("π0",3.6),("paligemma-binning",4.9)]},
 "complex": {"trials":170,"rows":[("Cosmos3-Nano-Policy",25.3),("π0.5",13.5),("DreamZero",14.1),("π0-FAST",2.9),("GR00T N1.6",0.0),("π0",0.0),("paligemma-binning",0.0)]},
}

# Leader-of-the-board (Cosmos3-Nano-Policy) per competency axis — page "By Competency Axis"
AXIS_BREAK = [
 {"axis":"relational","trials":420,"attrs":["conjunction","counting","spatial"],"sr":49.3,"score":60.9,
  "note":"interpreting conjunctions, counting, and spatial relations in multi-object instructions — the strongest axis",
  "note_cn":"在多物体指令中理解并列（conjunction）、计数与空间关系——表现最强的一轴"},
 {"axis":"procedural","trials":220,"attrs":["affordance","reorientation","stacking"],"sr":27.3,"score":46.8,
  "note":"action-oriented reasoning across affordances, reorientation, and stacking",
  "note_cn":"面向动作的推理，涉及可供性（affordance）、重新定向与堆叠"},
 {"axis":"visual",    "trials":840,"attrs":["color","semantics","size"],"sr":26.1,"score":42.9,
  "note":"grounding color, object semantics, and size from pixels — the widest axis (840 trials)",
  "note_cn":"从像素中接地（ground）颜色、物体语义与尺寸——覆盖最广的一轴（840 次试验）"},
]

# ---- vocabulary: tokenize the default instructions (the canonical phrasing) ----
STOP = set("the a an to in on of and or it up out off into onto with all any one two three "
           "that this so make sure there are them each both other put place pick".split())
wc = Counter()
for t in TASKS:
    for tok in re.findall(r"[a-zA-Z]+", t['default'].lower()):
        if len(tok) < 3 or tok in STOP:
            continue
        wc[tok] += 1
words = wc.most_common(60)

# one-to-one Chinese rendering of each vocabulary token; counts of tokens that map to
# the same Chinese word are merged so the CN cloud has no overlapping duplicates.
CN_TOK = {
 "bin":"箱","bowl":"碗","grey":"灰色","red":"红色","cube":"方块","plate":"盘子","white":"白色",
 "right":"右侧","table":"桌子","stack":"堆叠","left":"左侧","pack":"打包","shelf":"架子",
 "mugs":"马克杯","rubiks":"魔方","banana":"香蕉","take":"取出","away":"收走","foods":"食物",
 "hammer":"锤子","bananas":"香蕉","blocks":"积木","blue":"蓝色","green":"绿色","yellow":"黄色",
 "box":"盒子","canned":"罐装","objects":"物体","plastic":"塑料","pot":"锅","move":"移动",
 "mug":"马克杯","spoon":"勺子","upright":"直立","crate":"板条箱","sauce":"酱料","bottles":"瓶子",
 "black":"黑色","sort":"分类","tower":"塔","top":"顶部","measuring":"量具","container":"容器",
 "cubes":"方块","boxed":"盒装","object":"物体","orange":"橙色","mustard":"芥末","bottle":"瓶子",
 "block":"积木","small":"小","cartons":"纸盒","opening":"开口","facing":"朝向","upwards":"向上",
 "apple":"苹果","yogurt":"酸奶","then":"然后","bbq":"烧烤","pumpkin":"南瓜",
}
_cnwc = Counter()
for _w, _n in words:
    _cnwc[CN_TOK.get(_w, _w)] += _n
words_cn = _cnwc.most_common(len(_cnwc))

# ---- write CSV (the parsed catalog) ----
with open(os.path.join(HERE, 'robolab_tasks.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['task_class','file','scene_usda','difficulty','num_subtasks','episode_s',
                'attributes','competency_axes','instr_default','instr_vague','instr_specific'])
    for t in TASKS:
        w.writerow([t['cls'],t['file'],t['scene'],t['diff'],t['subs'],t['ep'],
                    ';'.join(t['attrs']),';'.join(t['axes']),t['default'],t['vague'],t['specific']])
print(f"wrote robolab_tasks.csv ({len(TASKS)} tasks)")

def build_data_json(cn):
    """Assemble the injected DATA blob, swapping prose + word cloud to the target language."""
    axis_break = []
    for a in AXIS_BREAK:
        a2 = {k: v for k, v in a.items() if k != "note_cn"}
        a2["note"] = a["note_cn"] if cn else a["note"]
        axis_break.append(a2)
    data = {
     "tasks":TASKS,
     "attrCounts":attr_counts.most_common(),
     "diffCounts":dict(diff_counts),
     "axisCounts":dict(axis_counts),
     "leader":LEADER,
     "diffBreak":DIFF_BREAK,
     "axisBreak":axis_break,
     "words":(words_cn if cn else words),
    }
    return json.dumps(data, separators=(',',':'), ensure_ascii=False)


def render(lang):
    """lang='en' or 'cn'. Returns the full HTML string."""
    cn = (lang == 'cn')
    other = 'robolab_dashboard.html' if cn else 'robolab_dashboard_cn.html'
    toggle_label = 'EN' if cn else '中文'
    toggle_title = 'Switch to English' if cn else '切换到中文版'

    # text bundle
    if cn:
        T = {
          "title":"RoboLab · 任务 / 指令 / 排行榜图谱",
          "stamp":"RoboLab-120 · 1,200 次评估",
          "kick":"RoboLab · NVIDIA Seattle Robotics Lab · 任务通才策略分析",
          "h1a":"RoboLab","h1b":"分析图谱",
          "lede":('RoboLab 是 NVIDIA SRL 面向<b>任务通才策略分析</b>的高保真 Isaac-Sim 操作基准。'
                  '它不只给一个成功率，而是把 <b>RoboLab-120</b> 的 120 个桌面任务在三个维度上展开：'
                  '每个任务配三档<b>语言具体度</b>（vague / default / specific），三档<b>难度</b>'
                  '（simple / moderate / complex），并把逐任务的属性标签归并为三条<b>能力轴</b>'
                  '——visual / procedural / relational。排行榜在 <b>120 任务 × 10 回合 = 1,200 次评估</b>'
                  '上同时报告 <b>SR%</b>、子任务进度 <b>Score</b> 与末端执行器运动质量（EE Speed / EE SPARC），'
                  '且其策略排序与真实世界 <b>RoboArena</b> Elo 强相关。'),
          "s_tasks":"任务","s_modes":"指令档","s_diff":"难度档","s_axes":"能力轴","s_eval":"次评估",
          "note":('<b>这份数据真正回答的问题。</b>RoboLab 把“一个数字”拆成一张<b>诊断网格</b>：'
                  '同一任务在 vague→default→specific 三种措辞下被反复评测，难度被显式标注，'
                  '属性标签（color、spatial、counting、stacking…）被归并为三条能力轴。'
                  '于是失败不再是“失败”，而能被定位到——是看不懂（visual）、不会做（procedural），'
                  '还是想不清多物体关系（relational）。下方目录即由仓库内 <code>tasks.md</code> 解析而来。'),
          "sec1":"RoboLab-120 任务目录","sec1d":"120 个任务 · 三档指令 · 点击展开 · 可搜索/筛选",
          "search_ph":"搜索任务、场景、属性或指令文本…（如 stack、pour、bin、spatial）",
          "all":"全部",
          "cnt_pre":"显示","cnt_post":"个任务",
          "m_scene":"场景","m_subtasks":"子任务","m_budget":"时长预算",
          "attr_freq":"属性标签频次 · 跨 120 个任务",
          "ax_tasks":"个 RoboLab-120 任务","ax_trials":"次评估试验","ax_top":"榜首策略 SR · 得分 ",
          "tier_ex":"<b>__CLS__</b> · 同一目标，三种措辞。<b>vague</b> 档隐去指代与计数，<b>specific</b> 档则逐一言明。某策略在 vague 档与 specific 档成功率之间的差距，直接反映它在多大程度上依赖<b>语言对齐（language grounding）</b>而非脚本化先验。",
          "th_rank":"#","th_policy":"策略","th_sr":"SR%","th_score":"Score","th_speed":"EE&nbsp;Speed","th_sparc":"EE&nbsp;SPARC",
          "diff_trials":"次试验",
          "sec2":"难度与构成","sec2d":"难度分布 · 子任务数 · 时长预算",
          "sec3":"三条能力轴","sec3d":"属性标签 → 能力轴 · 含榜首策略逐轴 SR",
          "sec4":"语言具体度的三个档位","sec4d":"同一目标，三种措辞 — vague / default / specific",
          "sec5":"排行榜 · RoboLab-120","sec5d":"1,200 次评估 · SR% / Score / 末端运动质量",
          "sec6":"指令词表","sec6d":"自 120 条 default 指令分词",
          "diff_lbl":"难度分布 · 每档任务数","subs_lbl":"子任务数分布 · 长程程度","dur_lbl":"单回合时长预算 · 秒",
          "lb_overall":"总榜 · 全部难度合计","lb_bydiff":"按难度 · SR% 随难度衰减",
          "ee_lbl":"末端执行器运动质量 · 越平滑越接近示教",
          "axis_topnote":"榜首策略 Cosmos3-Nano-Policy 的逐轴成绩 — relational 反而最高，visual 最低（轴最宽）",
          "tier_v":"vague · 含糊","tier_d":"default · 默认","tier_s":"specific · 具体",
          "tier_vd":"口语化、欠指代——考验先验与脚本化常识。",
          "tier_dd":"任务的规范措辞——多数论文报告的设定。",
          "tier_sd":"逐步、显式——指代消歧后只剩控制难度。",
          "footer":('来源 · 任务目录由本仓库 <code>RoboLab/tasks.md</code>（RoboLab 任务元数据 CSV 自动导出，'
                    '"Last updated: 2026-05-07"）解析为 <code>robolab_tasks.csv</code>。排行榜、评估协议、'
                    '难度/能力轴拆分与指标定义（SR% / Score / EE Speed / EE SPARC，1,200 次评估，'
                    'WAM 与 VLA 策略类型，与 RoboArena Elo 的相关性）取自 RoboLab 项目排行榜页 '
                    '<a href="https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html">'
                    'research.nvidia.com/labs/srl/projects/robolab</a>（NVIDIA Seattle Robotics Lab）。'
                    '场景缩略图引用仓库外的 RoboLab 资产路径，故此处以 <code>.usda</code> 场景名替代图像。'),
        }
    else:
        T = {
          "title":"RoboLab · Task / Instruction / Leaderboard Atlas",
          "stamp":"RoboLab-120 · 1,200 evals",
          "kick":"RoboLab · NVIDIA Seattle Robotics Lab · Task-Generalist Policy Analysis",
          "h1a":"RoboLab","h1b":"Analysis Atlas",
          "lede":('RoboLab is NVIDIA SRL\'s high-fidelity Isaac-Sim manipulation benchmark built for the '
                  '<b>analysis</b> of task-generalist policies. Rather than report one success number, it '
                  'unfolds <b>RoboLab-120</b>\'s 120 tabletop tasks along three axes: every task ships three '
                  '<b>language-specificity tiers</b> (vague / default / specific), three <b>difficulty labels</b> '
                  '(simple / moderate / complex), and per-task attribute tags rolled up into three '
                  '<b>competency axes</b> — visual / procedural / relational. The leaderboard scores '
                  '<b>120 tasks × 10 episodes = 1,200 evaluations</b> on <b>SR%</b>, a subtask-progress '
                  '<b>Score</b>, and end-effector motion quality (EE Speed / EE SPARC) — and its policy '
                  'ranking correlates strongly with real-world <b>RoboArena</b> Elo.'),
          "s_tasks":"tasks","s_modes":"instruction tiers","s_diff":"difficulty labels","s_axes":"competency axes","s_eval":"evaluations",
          "note":('<b>What this benchmark really answers.</b> RoboLab turns "one number" into a <b>diagnostic '
                  'grid</b>: the same task is evaluated under vague → default → specific phrasings, difficulty '
                  'is explicitly labeled, and attribute tags (color, spatial, counting, stacking…) roll up into '
                  'three competency axes. A failure is no longer just "failure" — it localizes to <b>not seeing</b> '
                  '(visual), <b>not acting</b> (procedural), or <b>not reasoning over multi-object relations</b> '
                  '(relational). The catalog below is parsed straight from the repo\'s <code>tasks.md</code>.'),
          "sec1":"The RoboLab-120 task catalog","sec1d":"120 tasks · 3 instruction tiers · click to expand · search/filter",
          "search_ph":"Search task, scene, attribute, or instruction text… (e.g. stack, pour, bin, spatial)",
          "all":"all",
          "cnt_pre":"Showing","cnt_post":"tasks",
          "m_scene":"scene","m_subtasks":"subtasks","m_budget":"budget",
          "attr_freq":"ATTRIBUTE-TAG FREQUENCY · ACROSS 120 TASKS",
          "ax_tasks":"RoboLab-120 tasks","ax_trials":"eval trials","ax_top":"top policy SR · score ",
          "tier_ex":"<b>__CLS__</b> &middot; one goal, three phrasings. The <b>vague</b> tier hides referents and counts; the <b>specific</b> tier spells them out. The gap between a policy's vague-tier and specific-tier success is a direct read on how much it depends on <b>language grounding</b> vs. scripted priors.",
          "th_rank":"#","th_policy":"Policy","th_sr":"SR%","th_score":"Score","th_speed":"EE&nbsp;Speed","th_sparc":"EE&nbsp;SPARC",
          "diff_trials":"trials",
          "sec2":"Difficulty & composition","sec2d":"difficulty mix · subtask depth · time budget",
          "sec3":"The three competency axes","sec3d":"attribute tags → axis · with the top policy's per-axis SR",
          "sec4":"Three tiers of language specificity","sec4d":"one goal, three phrasings — vague / default / specific",
          "sec5":"Leaderboard · RoboLab-120","sec5d":"1,200 evaluations · SR% / Score / motion quality",
          "sec6":"Instruction vocabulary","sec6d":"tokenized from the 120 default instructions",
          "diff_lbl":"DIFFICULTY MIX · TASKS PER LABEL","subs_lbl":"SUBTASK-COUNT DISTRIBUTION · LONG-HORIZON DEPTH","dur_lbl":"PER-EPISODE TIME BUDGET · SECONDS",
          "lb_overall":"OVERALL · ALL DIFFICULTIES COMBINED","lb_bydiff":"BY DIFFICULTY · SR% DECAYS AS TASKS GET HARDER",
          "ee_lbl":"END-EFFECTOR MOTION QUALITY · SMOOTHER ≈ CLOSER TO DEMONSTRATIONS",
          "axis_topnote":"Top policy Cosmos3-Nano-Policy per axis — relational is highest, visual lowest (the widest axis)",
          "tier_v":"vague","tier_d":"default","tier_s":"specific",
          "tier_vd":"Colloquial, under-referential — leans on priors and scripted common sense.",
          "tier_dd":"The task's canonical phrasing — the setting most papers report.",
          "tier_sd":"Step-by-step, explicit — once referents are disambiguated, only control difficulty remains.",
          "footer":('SOURCE · Task catalog parsed from this repo\'s <code>RoboLab/tasks.md</code> (auto-exported '
                    'from the RoboLab task-metadata CSV, "Last updated: 2026-05-07") into '
                    '<code>robolab_tasks.csv</code>. Leaderboard, evaluation protocol, difficulty/competency '
                    'breakdowns, and metric definitions (SR% / Score / EE Speed / EE SPARC, 1,200 evaluations, '
                    'WAM vs VLA policy types, and the RoboArena-Elo correlation) from the RoboLab project '
                    'leaderboard page <a href="https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html">'
                    'research.nvidia.com/labs/srl/projects/robolab</a> (NVIDIA Seattle Robotics Lab). Scene '
                    'thumbnails reference RoboLab asset paths outside this repo, so the <code>.usda</code> scene '
                    'name is shown in place of the image.'),
        }

    html = r'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,900&family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root{
    --paper:#0a0d0a; --paper2:#0f140f; --card:#121912; --ink:#e9f0e7; --dim:#869083; --line:#22301f;
    --green:#76b900; --lime:#a6e22e; --cyan:#46c4c0; --violet:#9a7bff; --amber:#e0a93b; --rust:#e0633a; --blue:#5b8def;
  }
  *{box-sizing:border-box}
  html,body{margin:0;background:var(--paper);color:var(--ink);font-family:'IBM Plex Sans',sans-serif;-webkit-font-smoothing:antialiased}
  body{background-image:radial-gradient(900px 480px at 84% -8%, rgba(118,185,0,.12), transparent 60%),radial-gradient(880px 470px at 4% 3%, rgba(70,196,192,.07), transparent 58%)}
  .shell{max-width:1240px;margin:0 auto;padding:clamp(20px,4vw,56px)}
  header.top{border:1.5px solid var(--line);background:var(--card);padding:26px 28px;position:relative;overflow:hidden;border-radius:14px}
  .top:before,.top:after{content:"";position:absolute;top:50%;width:130px;height:130px;border-radius:50%;transform:translateY(-50%);filter:blur(2px);opacity:.42}
  .top:before{right:120px;border:1.5px solid var(--green)}
  .top:after{right:30px;border:1.5px solid var(--cyan)}
  .stamp{position:absolute;top:18px;right:22px;font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.18em;color:var(--green);border:1px solid var(--green);padding:5px 10px;border-radius:20px;background:var(--card);z-index:2}
  .kick{font-family:'Space Mono',monospace;font-size:11.5px;letter-spacing:.3em;text-transform:uppercase;color:var(--amber)}
  h1{font-family:'Fraunces',serif;font-weight:900;font-size:clamp(34px,6vw,68px);line-height:.95;margin:.16em 0 .12em;letter-spacing:-.015em;position:relative;z-index:2}
  h1 em{font-style:italic;background:linear-gradient(90deg,var(--green),var(--cyan));-webkit-background-clip:text;background-clip:text;color:transparent}
  .lede{color:var(--dim);max-width:80ch;font-size:15px;line-height:1.62;position:relative;z-index:2}
  .lede b{color:var(--ink);font-weight:600}
  .byline{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);line-height:1.7;margin:2px 0 14px;position:relative;z-index:2}
  .byline a,.byline b{color:var(--ink)} .byline a{text-decoration:underline}
  .statbar{display:grid;grid-template-columns:repeat(2,1fr);gap:0;margin-top:22px;border:1.5px solid var(--line);border-radius:12px;overflow:hidden}
  @media(min-width:720px){.statbar{grid-template-columns:repeat(5,1fr)}}
  .stat{padding:16px 18px;border-right:1px solid var(--line);background:var(--paper2)}
  .stat:last-child{border-right:none}
  .stat .num{font-family:'Fraunces',serif;font-weight:900;font-size:28px;line-height:1}
  .stat .num.g{color:var(--green)} .stat .num.c{color:var(--cyan)} .stat .num.a{color:var(--amber)} .stat .num.v{color:var(--violet)}
  .stat .lab{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin-top:6px}
  .note{border-left:3px solid var(--green);background:var(--card);padding:14px 18px;font-size:13.5px;line-height:1.62;color:var(--dim);margin-top:18px;border-radius:0 10px 10px 0}
  .note b{color:var(--ink)} .note code{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan);background:var(--paper2);padding:1px 5px;border-radius:3px}
  section{margin-top:34px}
  .sec-h{display:flex;align-items:baseline;gap:14px;margin-bottom:14px}
  .sec-h h2{font-family:'Fraunces',serif;font-weight:600;font-size:25px;margin:0;letter-spacing:-.01em}
  .sec-h .idx{font-family:'Space Mono',monospace;font-size:12px;color:var(--cyan)}
  .sec-h .desc{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-left:auto;text-align:right}
  .panel{border:1.5px solid var(--line);background:var(--card);padding:22px;border-radius:14px}
  .lbl{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:14px;letter-spacing:.06em}
  .twocol{display:grid;gap:18px}
  @media(min-width:880px){.twocol{grid-template-columns:1fr 1fr}}
  /* catalog */
  .controls{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;align-items:center}
  .controls input{font-family:'IBM Plex Sans';font-size:13px;padding:9px 12px;border:1.5px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:8px;flex:1;min-width:240px}
  .controls input:focus{outline:none;border-color:var(--green)}
  .chiprow{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}
  .chip{font-family:'Space Mono',monospace;font-size:10.5px;padding:7px 11px;border:1.5px solid var(--line);background:var(--paper2);color:var(--dim);cursor:pointer;border-radius:8px;letter-spacing:.03em}
  .chip.on{border-color:var(--green);color:var(--green)}
  .chip.dx.on{border-color:var(--cyan);color:var(--cyan)}
  .count-line{font-family:'Space Mono',monospace;font-size:11px;color:var(--dim);margin-bottom:10px}
  .tasklist{display:flex;flex-direction:column;gap:10px}
  .tcard{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);overflow:hidden}
  .tcard>summary{cursor:pointer;list-style:none;padding:13px 18px;display:flex;align-items:center;gap:11px;flex-wrap:wrap}
  .tcard>summary::-webkit-details-marker{display:none}
  .tcard>summary:after{content:"\25B8";margin-left:auto;color:var(--green);transition:transform .2s}
  .tcard[open]>summary:after{transform:rotate(90deg)}
  .tcard .tname{font-family:'Space Mono',monospace;font-weight:700;font-size:13px;color:var(--ink)}
  .tcard .tinstr{font-size:13px;color:var(--dim);flex-basis:100%;line-height:1.4;margin-top:-2px}
  .dot{width:9px;height:9px;border-radius:50%;display:inline-block;flex:none}
  .pill{font-family:'Space Mono',monospace;font-size:9.5px;padding:3px 9px;border-radius:11px;border:1px solid var(--line);color:var(--dim);letter-spacing:.02em;white-space:nowrap}
  .tcard .body{padding:4px 18px 16px;border-top:1px solid var(--line);margin-top:2px}
  .tiers{display:grid;gap:8px;margin:14px 0 6px}
  @media(min-width:680px){.tiers{grid-template-columns:1fr 1fr 1fr}}
  .tier{border:1px solid var(--line);border-radius:9px;background:var(--paper);padding:10px 12px}
  .tier .tk{font-family:'Space Mono',monospace;font-size:9px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:5px}
  .tier.v .tk{color:var(--rust)} .tier.d .tk{color:var(--green)} .tier.s .tk{color:var(--cyan)}
  .tier .tt{font-size:12.5px;color:var(--ink);line-height:1.45}
  .meta-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;align-items:center}
  .meta-row .m{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim)}
  .meta-row .m b{color:var(--ink)}
  mark{background:rgba(118,185,0,.28);color:inherit;padding:0 1px}
  /* bars */
  .bar-wrap{display:flex;flex-direction:column;gap:9px}
  .brow{display:grid;grid-template-columns:120px 1fr 66px;align-items:center;gap:12px}
  .brow .name{font-family:'Space Mono',monospace;font-size:12px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .track{height:18px;background:var(--paper);border:1px solid var(--line);border-radius:3px;overflow:hidden;position:relative}
  .fill{height:100%;transition:width .6s cubic-bezier(.2,.8,.2,1)}
  .brow .v{font-family:'Space Mono',monospace;font-size:11px;font-weight:700;text-align:right}
  .histo{display:flex;align-items:flex-end;gap:5px;height:120px;margin-top:6px}
  .hbar{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px}
  .hbar .bb{width:100%;background:var(--cyan);border-radius:3px 3px 0 0;min-height:2px}
  .hbar .hl{font-family:'Space Mono',monospace;font-size:9px;color:var(--dim)}
  .hbar .hn{font-family:'Space Mono',monospace;font-size:9px;color:var(--ink)}
  /* axes */
  .axgrid{display:grid;gap:14px;grid-template-columns:1fr}
  @media(min-width:760px){.axgrid{grid-template-columns:1fr 1fr 1fr}}
  .axcard{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);padding:16px 18px;position:relative;overflow:hidden}
  .axcard .ah{font-family:'Fraunces',serif;font-weight:600;font-size:19px;margin-bottom:2px}
  .axcard .atag{font-family:'Space Mono',monospace;font-size:9.5px;color:var(--dim);margin-bottom:10px}
  .axcard .abig{font-family:'Fraunces',serif;font-weight:900;font-size:38px;line-height:1}
  .axcard .asub{font-family:'Space Mono',monospace;font-size:10px;color:var(--dim);margin-top:2px}
  .axcard .ad{font-size:12px;color:var(--dim);line-height:1.5;margin-top:10px;border-top:1px solid var(--line);padding-top:10px}
  .axcard .attrs{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
  /* leaderboard table */
  .lbtable{width:100%;border-collapse:collapse;font-size:13px}
  .lbtable th{font-family:'Space Mono',monospace;font-size:9.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);text-align:right;padding:8px 10px;border-bottom:1.5px solid var(--line)}
  .lbtable th:nth-child(1),.lbtable th:nth-child(2){text-align:left}
  .lbtable td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right;font-family:'Space Mono',monospace;font-size:12.5px}
  .lbtable td:nth-child(2){text-align:left;font-weight:700;color:var(--ink)}
  .lbtable td:nth-child(1){text-align:left;color:var(--dim)}
  .lbtable tr:hover td{background:var(--paper2)}
  .typetag{font-family:'Space Mono',monospace;font-size:8.5px;padding:2px 6px;border-radius:9px;border:1px solid var(--line);margin-left:7px;vertical-align:middle}
  .typetag.wam{color:var(--green);border-color:var(--green)} .typetag.vla{color:var(--violet);border-color:var(--violet)}
  .srcell{color:var(--green);font-weight:700}
  .diffgrp{margin-bottom:18px}
  .diffgrp .gh{font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);margin-bottom:8px;letter-spacing:.05em}
  /* tiers explainer */
  .tierx{display:grid;gap:14px;grid-template-columns:1fr}
  @media(min-width:760px){.tierx{grid-template-columns:1fr 1fr 1fr}}
  .txcard{border:1.5px solid var(--line);border-radius:12px;background:var(--paper2);padding:16px 18px}
  .txcard .txk{font-family:'Space Mono',monospace;font-size:11px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}
  .txcard.v .txk{color:var(--rust)} .txcard.d .txk{color:var(--green)} .txcard.s .txk{color:var(--cyan)}
  .txcard .txd{font-size:12.5px;color:var(--dim);line-height:1.5;margin-bottom:12px}
  .txcard .txe{font-size:12.5px;color:var(--ink);line-height:1.5;font-style:italic;border-left:2px solid var(--line);padding-left:10px}
  #cloud{width:100%;height:280px;display:block}
  footer{margin-top:36px;border-top:1.5px solid var(--line);padding-top:16px;font-family:'Space Mono',monospace;font-size:10.5px;color:var(--dim);line-height:1.7}
  footer a{color:var(--green)} footer code{color:var(--cyan)}
  .langtoggle{position:fixed;top:14px;right:14px;z-index:9999;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#e9f0e7;background:rgba(18,25,18,.82);border:1.5px solid #76b900;border-radius:9px;padding:7px 13px;text-decoration:none;backdrop-filter:blur(6px);transition:background .15s,color .15s,transform .15s}
  .langtoggle:hover{background:#76b900;color:#0a0d0a;transform:translateY(-1px)}
</style>
<a class="langtoggle" href="__OTHER__" title="__TOGGLE_TITLE__">__TOGGLE_LABEL__</a>
<div class="shell">
  <header class="top">
    <div class="stamp">__STAMP__</div>
    <div class="kick">__KICK__</div>
    <h1>__H1A__<br><em>__H1B__</em></h1>
    <div class="byline"><b>Jie Wang</b> &middot; <a href="https://everloom-129.github.io/" target="_blank" rel="noopener">everloom-129.github.io</a> &middot; GRASP Lab, UPenn &nbsp;&middot;&nbsp; Co-authored with <a href="https://claude.ai/" target="_blank" rel="noopener">Claude Code</a> &nbsp;&middot;&nbsp; <span style="color:var(--ink)">2026.6.1</span></div>
    <p class="lede">__LEDE__</p>
    <div class="statbar">
      <div class="stat"><div class="num g">120</div><div class="lab">__S_TASKS__</div></div>
      <div class="stat"><div class="num c">3</div><div class="lab">__S_MODES__</div></div>
      <div class="stat"><div class="num a">3</div><div class="lab">__S_DIFF__</div></div>
      <div class="stat"><div class="num v">3</div><div class="lab">__S_AXES__</div></div>
      <div class="stat"><div class="num">1,200</div><div class="lab">__S_EVAL__</div></div>
    </div>
  </header>

  <div class="note">__NOTE__</div>

  <!-- 01 CATALOG -->
  <section>
    <div class="sec-h"><span class="idx">01</span><h2>__SEC1__</h2><span class="desc">__SEC1D__</span></div>
    <div class="panel">
      <div class="controls"><input id="search" placeholder="__SEARCH_PH__"></div>
      <div class="chiprow" id="diffChips"></div>
      <div class="chiprow" id="axisChips"></div>
      <div class="count-line" id="countLine"></div>
      <div class="tasklist" id="tasklist"></div>
    </div>
  </section>

  <!-- 02 DIFFICULTY & COMPOSITION -->
  <section>
    <div class="sec-h"><span class="idx">02</span><h2>__SEC2__</h2><span class="desc">__SEC2D__</span></div>
    <div class="twocol">
      <div class="panel">
        <div class="lbl">__DIFF_LBL__</div>
        <div class="bar-wrap" id="diffBars"></div>
        <div class="lbl" style="margin-top:20px">__SUBS_LBL__</div>
        <div class="histo" id="subsHisto"></div>
      </div>
      <div class="panel">
        <div class="lbl">__DUR_LBL__</div>
        <div class="histo" id="durHisto"></div>
        <div class="bar-wrap" id="attrBars" style="margin-top:20px"></div>
      </div>
    </div>
  </section>

  <!-- 03 COMPETENCY AXES -->
  <section>
    <div class="sec-h"><span class="idx">03</span><h2>__SEC3__</h2><span class="desc">__SEC3D__</span></div>
    <div class="panel">
      <div class="lbl">__AXIS_TOPNOTE__</div>
      <div class="axgrid" id="axGrid"></div>
    </div>
  </section>

  <!-- 04 LANGUAGE TIERS -->
  <section>
    <div class="sec-h"><span class="idx">04</span><h2>__SEC4__</h2><span class="desc">__SEC4D__</span></div>
    <div class="panel">
      <div class="tierx" id="tierx"></div>
      <div class="note" style="margin-top:16px;border-left-color:var(--cyan)" id="tierExample"></div>
    </div>
  </section>

  <!-- 05 LEADERBOARD -->
  <section>
    <div class="sec-h"><span class="idx">05</span><h2>__SEC5__</h2><span class="desc">__SEC5D__</span></div>
    <div class="twocol">
      <div class="panel">
        <div class="lbl">__LB_OVERALL__</div>
        <table class="lbtable" id="lbTable"></table>
        <div class="lbl" style="margin-top:20px">__EE_LBL__</div>
        <div class="bar-wrap" id="eeBars"></div>
      </div>
      <div class="panel">
        <div class="lbl">__LB_BYDIFF__</div>
        <div id="diffBreak"></div>
      </div>
    </div>
  </section>

  <!-- 06 VOCAB -->
  <section>
    <div class="sec-h"><span class="idx">06</span><h2>__SEC6__</h2><span class="desc">__SEC6D__</span></div>
    <div class="panel"><canvas id="cloud"></canvas></div>
  </section>

  <footer>__FOOTER__</footer>
</div>
<script>
const DATA = __DATA__;
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const DIFFCOL={simple:'--green',moderate:'--amber',complex:'--rust'};
const AXISCOL={visual:'--cyan',procedural:'--violet',relational:'--amber',uncategorized:'--line'};
function dc(d){return css(DIFFCOL[d]||'--blue');}
function ac(a){return css(AXISCOL[a]||'--blue');}
const TXT=__TXT__;

// ---------- 01 catalog ----------
const TK=DATA.tasks;
let diffFilter='all',axisFilter='all';
(function buildChips(){
  const dEl=document.getElementById('diffChips');
  let h='<span class="chip dx on" data-d="all">'+TXT.all+'</span>';
  ['simple','moderate','complex'].forEach(function(d){
    h+='<span class="chip dx" data-d="'+d+'" style="">'+d+' &middot; '+(DATA.diffCounts[d]||0)+'</span>';
  });
  dEl.innerHTML=h;
  const aEl=document.getElementById('axisChips');
  let a='<span class="chip on" data-a="all">'+TXT.all+'</span>';
  ['visual','procedural','relational'].forEach(function(x){
    a+='<span class="chip" data-a="'+x+'" style="">'+x+' &middot; '+(DATA.axisCounts[x]||0)+'</span>';
  });
  aEl.innerHTML=a;
  Array.prototype.forEach.call(dEl.querySelectorAll('.chip'),function(c){c.onclick=function(){Array.prototype.forEach.call(dEl.querySelectorAll('.chip'),function(x){x.classList.remove('on');});c.classList.add('on');diffFilter=c.dataset.d;render();};});
  Array.prototype.forEach.call(aEl.querySelectorAll('.chip'),function(c){c.onclick=function(){Array.prototype.forEach.call(aEl.querySelectorAll('.chip'),function(x){x.classList.remove('on');});c.classList.add('on');axisFilter=c.dataset.a;render();};});
})();
function esc(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}
function render(){
  const q=document.getElementById('search').value.toLowerCase().trim();
  function hl(s){if(!s)return '';return q?s.replace(new RegExp('('+esc(q)+')','ig'),'<mark>$1</mark>'):s;}
  const rows=TK.filter(function(t){
    if(diffFilter!=='all'&&t.diff!==diffFilter)return false;
    if(axisFilter!=='all'&&t.axes.indexOf(axisFilter)<0)return false;
    if(!q)return true;
    const blob=(t.cls+' '+t.scene+' '+t.attrs.join(' ')+' '+t.default+' '+t.vague+' '+t.specific).toLowerCase();
    return blob.indexOf(q)>=0;
  });
  document.getElementById('countLine').textContent=TXT.cnt_pre+' '+rows.length+' / '+TK.length+' '+TXT.cnt_post;
  document.getElementById('tasklist').innerHTML=rows.map(function(t){
    const col=dc(t.diff);
    const axpills=t.axes.filter(function(x){return x!=='uncategorized';}).map(function(x){return '<span class="pill" style="border-color:'+ac(x)+';color:'+ac(x)+'">'+x+'</span>';}).join('');
    const attrpills=t.attrs.map(function(a){return '<span class="pill">'+a+'</span>';}).join('');
    return '<details class="tcard"><summary>'
      +'<span class="dot" style="background:'+col+'"></span>'
      +'<span class="tname">'+hl(t.cls)+'</span>'
      +'<span class="pill" style="border-color:'+col+';color:'+col+'">'+t.diff+'</span>'
      +axpills
      +'<span class="tinstr">'+hl(t.default)+'</span>'
      +'</summary><div class="body">'
      +'<div class="tiers">'
      +'<div class="tier v"><div class="tk">'+TXT.tier_v+'</div><div class="tt">'+hl(t.vague||'&mdash;')+'</div></div>'
      +'<div class="tier d"><div class="tk">'+TXT.tier_d+'</div><div class="tt">'+hl(t.default||'&mdash;')+'</div></div>'
      +'<div class="tier s"><div class="tk">'+TXT.tier_s+'</div><div class="tt">'+hl(t.specific||'&mdash;')+'</div></div>'
      +'</div>'
      +'<div class="meta-row">'
      +'<span class="m">'+TXT.m_scene+' <b>'+(t.scene||'&mdash;')+'</b></span>'
      +'<span class="m">'+TXT.m_subtasks+' <b>'+t.subs+'</b></span>'
      +'<span class="m">'+TXT.m_budget+' <b>'+t.ep+'s</b></span>'
      +'<span class="m">'+attrpills+'</span>'
      +'</div></div></details>';
  }).join('');
}
document.getElementById('search').addEventListener('input',render);
render();

// ---------- 02 difficulty + composition ----------
(function(){
  const order=['simple','moderate','complex'];
  const mx=Math.max.apply(null,order.map(function(d){return DATA.diffCounts[d]||0;}));
  document.getElementById('diffBars').innerHTML=order.map(function(d){
    const n=DATA.diffCounts[d]||0,col=dc(d);
    return '<div class="brow"><div class="name">'+d+'</div><div class="track"><div class="fill" style="width:'+(n/mx*100)+'%;background:'+col+'"></div></div><div class="v" style="color:'+col+'">'+n+'</div></div>';
  }).join('');
  // subtask histogram
  function histo(elId,vals,col,unit){
    const buckets={};vals.forEach(function(v){buckets[v]=(buckets[v]||0)+1;});
    const keys=Object.keys(buckets).map(Number).sort(function(a,b){return a-b;});
    const mxc=Math.max.apply(null,keys.map(function(k){return buckets[k];}));
    document.getElementById(elId).innerHTML=keys.map(function(k){
      return '<div class="hbar"><div class="hn">'+buckets[k]+'</div><div class="bb" style="height:'+(buckets[k]/mxc*92)+'px;background:'+col+'"></div><div class="hl">'+k+(unit||'')+'</div></div>';
    }).join('');
  }
  histo('subsHisto',TK.map(function(t){return t.subs;}),css('--cyan'),'');
  // duration buckets
  const durBk={};TK.forEach(function(t){var b=t.ep;durBk[b]=(durBk[b]||0)+1;});
  const dk=Object.keys(durBk).map(Number).sort(function(a,b){return a-b;});
  const dmx=Math.max.apply(null,dk.map(function(k){return durBk[k];}));
  document.getElementById('durHisto').innerHTML=dk.map(function(k){
    return '<div class="hbar"><div class="hn">'+durBk[k]+'</div><div class="bb" style="height:'+(durBk[k]/dmx*92)+'px;background:'+css('--green')+'"></div><div class="hl">'+k+'s</div></div>';
  }).join('');
  // attribute bars (top tags)
  const A=DATA.attrCounts.slice(0,11);
  const amx=A[0][1];
  document.getElementById('attrBars').innerHTML='<div class="lbl" style="margin-bottom:8px">'+TXT.attr_freq+'</div>'+A.map(function(p){
    var col=ac(({color:'visual',semantics:'visual',size:'visual',affordance:'procedural',reorientation:'procedural',stacking:'procedural',conjunction:'relational',counting:'relational',spatial:'relational'})[p[0]]||'uncategorized');
    return '<div class="brow"><div class="name">'+p[0]+'</div><div class="track"><div class="fill" style="width:'+(p[1]/amx*100)+'%;background:'+col+'"></div></div><div class="v" style="color:'+col+'">'+p[1]+'</div></div>';
  }).join('');
})();

// ---------- 03 competency axes ----------
(function(){
  document.getElementById('axGrid').innerHTML=DATA.axisBreak.map(function(a){
    const col=ac(a.axis);
    const tcount=DATA.axisCounts[a.axis]||0;
    return '<div class="axcard" style="border-color:'+col+'">'
      +'<div class="ah" style="color:'+col+'">'+a.axis+'</div>'
      +'<div class="atag">'+tcount+' '+TXT.ax_tasks+' &middot; '+a.trials+' '+TXT.ax_trials+'</div>'
      +'<div class="abig" style="color:'+col+'">'+a.sr.toFixed(1)+'%</div>'
      +'<div class="asub">'+TXT.ax_top+a.score.toFixed(1)+'</div>'
      +'<div class="attrs">'+a.attrs.map(function(x){return '<span class="pill" style="border-color:'+col+';color:'+col+'">'+x+'</span>';}).join('')+'</div>'
      +'<div class="ad">'+a.note+'</div></div>';
  }).join('');
})();

// ---------- 04 language tiers ----------
(function(){
  // find a vivid example task with all three tiers (prefer a sorting/complex one)
  let ex=TK.filter(function(t){return t.vague&&t.specific&&t.default;});
  let pick=ex.filter(function(t){return t.cls==='CleanUpToysTask';})[0]||ex[0];
  const tiers=[['v',TXT.tier_v,TXT.tier_vd],['d',TXT.tier_d,TXT.tier_dd],['s',TXT.tier_s,TXT.tier_sd]];
  document.getElementById('tierx').innerHTML=tiers.map(function(t){
    return '<div class="txcard '+t[0]+'"><div class="txk">'+t[1]+'</div><div class="txd">'+t[2]+'</div>'
      +'<div class="txe">&ldquo;'+(pick[{v:'vague',d:'default',s:'specific'}[t[0]]])+'&rdquo;</div></div>';
  }).join('');
  document.getElementById('tierExample').innerHTML=TXT.tier_ex.replace('__CLS__',pick.cls);
})();

// ---------- 05 leaderboard ----------
(function(){
  const L=DATA.leader;
  let h='<tr><th>'+TXT.th_rank+'</th><th>'+TXT.th_policy+'</th><th>'+TXT.th_sr+'</th><th>'+TXT.th_score+'</th><th>'+TXT.th_speed+'</th><th>'+TXT.th_sparc+'</th></tr>';
  h+=L.map(function(r){
    const tt='<span class="typetag '+r.type.toLowerCase()+'">'+r.type+'</span>';
    return '<tr><td>'+r.rank+'</td><td>'+r.model+tt+'</td>'
      +'<td class="srcell">'+r.sr.toFixed(1)+'</td><td>'+r.score.toFixed(1)+'</td>'
      +'<td>'+r.speed.toFixed(2)+'</td><td>'+r.sparc.toFixed(2)+'</td></tr>';
  }).join('');
  document.getElementById('lbTable').innerHTML=h;
  // EE motion-quality bars (SPARC: less negative = smoother). Map sparc into [0,1] for bar.
  const sp=L.map(function(r){return r.sparc;});
  const lo=Math.min.apply(null,sp),hi=Math.max.apply(null,sp);
  document.getElementById('eeBars').innerHTML=L.slice().sort(function(a,b){return b.sparc-a.sparc;}).map(function(r){
    const frac=(r.sparc-lo)/(hi-lo);const col=r.type==='WAM'?css('--green'):css('--violet');
    return '<div class="brow"><div class="name">'+r.model+'</div><div class="track"><div class="fill" style="width:'+(20+frac*80)+'%;background:'+col+'"></div></div><div class="v" style="color:'+col+'">'+r.sparc.toFixed(1)+'</div></div>';
  }).join('');
  // by difficulty
  const order=['simple','moderate','complex'];
  document.getElementById('diffBreak').innerHTML=order.map(function(d){
    const grp=DATA.diffBreak[d];const col=dc(d);
    // fixed 0-100% scale: the fill width IS the actual SR% so the decay across difficulty reads true
    const bars=grp.rows.slice().sort(function(a,b){return b[1]-a[1];}).map(function(x){
      return '<div class="brow"><div class="name" title="'+x[0]+'">'+x[0]+'</div><div class="track"><div class="fill" style="width:'+x[1]+'%;background:'+col+'"></div></div><div class="v" style="color:'+col+'">'+x[1].toFixed(1)+'%</div></div>';
    }).join('');
    return '<div class="diffgrp"><div class="gh"><span style="color:'+col+'">&#9632;</span> '+d+' &middot; '+grp.trials+' '+TXT.diff_trials+'</div><div class="bar-wrap">'+bars+'</div></div>';
  }).join('');
})();

// ---------- 06 word cloud (spiral packing) ----------
(function(){
  const cv=document.getElementById('cloud');const ctx=cv.getContext('2d');
  function draw(){
    const dpr=window.devicePixelRatio||1;const W=cv.clientWidth,H=280;
    cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,W,H);
    const words=DATA.words;if(!words.length)return;
    const mx=words[0][1],mn=words[words.length-1][1];
    const pal=[css('--green'),css('--cyan'),css('--violet'),css('--amber'),css('--lime'),css('--ink')];
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

    # JS-side text bundle — every string the client-side JS injects
    txt_js = json.dumps({k: T[k] for k in (
      "all","tier_v","tier_d","tier_s","tier_vd","tier_dd","tier_sd",
      "cnt_pre","cnt_post","m_scene","m_subtasks","m_budget","attr_freq",
      "ax_tasks","ax_trials","ax_top","tier_ex",
      "th_rank","th_policy","th_sr","th_score","th_speed","th_sparc","diff_trials",
    )}, ensure_ascii=False)

    repl = {
      "__TITLE__":T["title"],"__OTHER__":other,"__TOGGLE_LABEL__":toggle_label,"__TOGGLE_TITLE__":toggle_title,
      "__STAMP__":T["stamp"],"__KICK__":T["kick"],"__H1A__":T["h1a"],"__H1B__":T["h1b"],"__LEDE__":T["lede"],
      "__S_TASKS__":T["s_tasks"],"__S_MODES__":T["s_modes"],"__S_DIFF__":T["s_diff"],"__S_AXES__":T["s_axes"],"__S_EVAL__":T["s_eval"],
      "__NOTE__":T["note"],
      "__SEC1__":T["sec1"],"__SEC1D__":T["sec1d"],"__SEARCH_PH__":T["search_ph"],
      "__SEC2__":T["sec2"],"__SEC2D__":T["sec2d"],"__DIFF_LBL__":T["diff_lbl"],"__SUBS_LBL__":T["subs_lbl"],"__DUR_LBL__":T["dur_lbl"],
      "__SEC3__":T["sec3"],"__SEC3D__":T["sec3d"],"__AXIS_TOPNOTE__":T["axis_topnote"],
      "__SEC4__":T["sec4"],"__SEC4D__":T["sec4d"],
      "__SEC5__":T["sec5"],"__SEC5D__":T["sec5d"],"__LB_OVERALL__":T["lb_overall"],"__LB_BYDIFF__":T["lb_bydiff"],"__EE_LBL__":T["ee_lbl"],
      "__SEC6__":T["sec6"],"__SEC6D__":T["sec6d"],
      "__FOOTER__":T["footer"],
      "__DATA__":build_data_json(cn),"__TXT__":txt_js,
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html

for lang, fn in [('en', 'robolab_dashboard.html'), ('cn', 'robolab_dashboard_cn.html')]:
    out = render(lang)
    open(os.path.join(HERE, fn), 'w').write(out)
    print(f"wrote {fn} ({len(out)} bytes)")
