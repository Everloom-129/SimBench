# SimBench — A Visual Survey of VLA Simulation Manipulation Benchmarks

> **What are the robots *actually* told to do?**
> A curated, side-by-side reference of the task suites and language instructions used across today's
> Vision-Language-Action (VLA) manipulation benchmarks.

🔗 **Live reference:** https://everloom-129.github.io/SimBench/

This repository collects the task catalogs of the major simulated robot-manipulation benchmarks into a
single, comparable format. For each benchmark it provides the raw data (CSV/JSON), the script used to build
it where applicable, and an interactive HTML "atlas" that visualizes the tasks, skills, and instructions.
Alongside the task catalogs it also tracks the **robustness, generalization, and sim-to-real** axes —
perturbation suites and benchmark surveys that measure how well policies actually hold up. A top-level
index and dashboard survey all of them together.

It exists as a public, browsable reference — for picking an evaluation suite, comparing task coverage and
difficulty, or just understanding what each benchmark measures.

---

## Start here

- [`index.html`](index.html) — *VLA Sim-Benchmark Atlas · Index.* The landing page that links out to every
  per-benchmark atlas below. This is the front door of the [live site](https://everloom-129.github.io/SimBench/).
- [`vla_benchmark_dashboard.html`](vla_benchmark_dashboard.html) — *VLA Simulation Benchmarks · Visual
  Survey.* A single page that compares all benchmarks: task-instruction word cloud,
  capability-vs-robustness correlation, benchmark × model success heatmap, difficulty spread, simulator
  backbones, and per-benchmark deep dives.

---

## Task catalogs

Benchmarks whose tasks and language instructions are catalogued here.

| Benchmark | Focus | Tasks | Data | Atlas |
|---|---|---|---|---|
| **Meta-World** | MT/ML multi-task & meta-RL manipulation | 50 | [`metaworld_tasks.csv`](metaworld/metaworld_tasks.csv) | [atlas](metaworld/metaworld_dashboard.html) |
| **RLBench** | Vision-guided tasks & multi-task leaderboard | 106 | [`rlbench_tasks.csv`](rlbench/rlbench_tasks.csv) | [atlas](rlbench/rlbench_dashboard.html) |
| **CALVIN** | Language-conditioned, long-horizon chaining | 34 | [`calvin_tasks.csv`](calvin/calvin_tasks.csv) · [`.json`](calvin/calvin_tasks.json) | [atlas](calvin/calvin_dashboard.html) |
| **LIBERO** | 4-suite lifelong manipulation | 131 | [`libero_tasks.csv`](libero/libero_tasks.csv) | [atlas](libero/libero_dashboard.html) |
| **RoboCasa365** | Kitchen atomic skills + composite activities | 67 atomic / 301 composite | [atomic](robocasa365/robocasa_atomic_tasks.csv) · [composite](robocasa365/robocasa_composite_tasks.csv) | [atomic](robocasa365/robocasa365_atomic_skills.html) · [composite](robocasa365/robocasa365_composite_tasks.html) |
| **BEHAVIOR-1K** | Long-horizon household activities (Challenge 2025) | 50 | [`behavior_challenge_50_tasks.csv`](Behavior1K/behavior_challenge_50_tasks.csv) | [atlas](Behavior1K/behavior_challenge_2025.html) |
| **RoboTwin** | Dual-arm manipulation tasks & instructions | — | — | [atlas](RoboTwin/robotwin_tasks.html) |
| **SimplerEnv** | Real-to-sim VLA evaluation setups | 7 | [`simplerenv_tasks.csv`](simplerenv/simplerenv_tasks.csv) | [atlas](simplerenv/simplerenv_dashboard.html) |
| **PolaRiS** | Real-to-sim correlation via Gaussian-splat scene scans (r≈0.9) | 6 | [`polaris_tasks.csv`](PolaRiS/polaris_tasks.csv) | [atlas](PolaRiS/polaris_tasks.html) |
| **MolmoSpaces** | Ai2 open ecosystem (scenes/objects/grasps) + 8-task bench | 8 bench / 10 templates | [`molmospaces_templates.csv`](molmospaces/molmospaces_templates.csv) | [atlas](molmospaces/molmospaces_dashboard.html) |
| **RoboVerse** | Aggregator: MetaSim unifies 6 simulators + 18 source benchmarks | 276 cats / 18 sources | [`roboverse_sources.csv`](roboverse/roboverse_sources.csv) | [atlas](roboverse/roboverse_dashboard.html) |
| **LW-BenchHub** | Lightwheel task hub (multi-suite) | 275 | [`lw_benchhub_tasks.csv`](lightwheel/lw_benchhub_tasks.csv) | [atlas](lightwheel/lw_benchhub_tasks.html) |

*Task counts reflect the rows in this repository's catalogs and may differ from a benchmark's full upstream
set. RoboTwin is currently published as an atlas only.*

---

## Robustness, generalization & survey atlases

These cover how well policies hold up under perturbation, and how the benchmark landscape itself is
evolving. Their data files are evaluation/leaderboard tables rather than task lists.

| Atlas | Focus | Data | Page |
|---|---|---|---|
| **THE COLOSSEUM** | Generalization under 14 systematic perturbation factors | [`colosseum.csv`](colosseum/colosseum.csv) | [atlas](colosseum/colosseum_dashboard.html) |
| **LIBERO-Plus** | VLA robustness across 7 perturbation axes | [`libero_plus.csv`](libero-plus/libero_plus.csv) | [atlas](libero-plus/libero_plus_dashboard.html) |
| **LIBERO-Pro** | Anti-memorization perturbation evaluation | [`libero_pro.csv`](libero-pro/libero_pro.csv) | [atlas](libero-pro/libero_pro_dashboard.html) |
| **Memory & Long-Horizon** | Survey of emerging robot-memory benchmarks | [`memory_benchmarks.csv`](memory/memory_benchmarks.csv) | [atlas](memory/memory_dashboard.html) |
| **Sim ↔ Real Bridge** | Real-robot evaluation & the reality gap | [`sim2real.csv`](sim2real/sim2real.csv) | [atlas](sim2real/sim2real_dashboard.html) |

---

## Repository layout

```
.
├── index.html                     # landing page → links to every atlas
├── build_index.py                 # generates index.html
├── vla_benchmark_dashboard.html   # cross-benchmark visual survey
│
│   # ── task catalogs ──
├── metaworld/                     # Meta-World MT/ML
│   ├── build_metaworld.py         #   builder script
│   ├── metaworld_tasks.csv        #   task catalog
│   └── metaworld_dashboard.html   #   interactive atlas
├── rlbench/                       # RLBench
├── calvin/                        # CALVIN (language + long-horizon)
├── libero/                        # LIBERO (4-suite lifelong)
├── robocasa365/                   # RoboCasa365 (atomic + composite)
├── Behavior1K/                    # BEHAVIOR-1K Challenge 2025
├── RoboTwin/                      # RoboTwin dual-arm
├── simplerenv/                    # SimplerEnv real-to-sim
├── PolaRiS/                       # PolaRiS real-to-sim correlation (Gaussian splat)
├── molmospaces/                   # MolmoSpaces ecosystem + 8-task bench
├── roboverse/                     # RoboVerse (aggregator · MetaSim)
├── lightwheel/                    # LW-BenchHub
│
│   # ── robustness / generalization / survey ──
├── colosseum/                     # THE COLOSSEUM (perturbation)
├── libero-plus/                   # LIBERO-Plus (robustness)
├── libero-pro/                    # LIBERO-Pro (anti-memorization)
├── memory/                        # robot-memory benchmark survey
└── sim2real/                      # sim ↔ real bridge
```

Each folder follows the same convention:

- **`*.csv` / `*_tasks.csv` / `.json`** — the data: a task catalog (task names, categories/skills, language
  instructions) for the catalogs above, or an evaluation/leaderboard table for the robustness atlases.
- **`build_*.py`** — the script that generates the data/page (where the source benchmark is installable).
- **`*_dashboard.html` / `*_tasks.html`** — a self-contained interactive atlas for that benchmark.

The HTML pages are static and self-contained — open any of them directly in a browser, or browse them all
via the [live site](https://everloom-129.github.io/SimBench/).

---

## Notes

- All visualizations are single-file HTML with no build step or dependencies.
- Catalogs are normalized toward a shared shape (task / category / instruction) but keep
  benchmark-specific columns (e.g. block color in CALVIN, appliance in RoboCasa365, eval setups in
  SimplerEnv) where they matter.
- This is a reference compilation; each underlying benchmark is the work of its respective authors —
  please cite the original benchmark when using its tasks.
