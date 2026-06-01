# SimBench — A Visual Survey of VLA Simulation Manipulation Benchmarks

> **What are the robots *actually* told to do?**
> A curated, side-by-side reference of the task suites and language instructions used across today's
> Vision-Language-Action (VLA) manipulation benchmarks.

🔗 **Live reference:** https://everloom-129.github.io/blog

This repository collects the task catalogs of the major simulated robot-manipulation benchmarks into a
single, comparable format. For each benchmark it provides the raw task list (CSV/JSON), the script used to
build it where applicable, and an interactive HTML "atlas" that visualizes the tasks, skills, and
instructions. A top-level dashboard surveys all of them together.

It exists as a public, browsable reference — for picking an evaluation suite, comparing task coverage and
difficulty, or just understanding what each benchmark measures.

---

## Cross-benchmark dashboard

[`vla_benchmark_dashboard.html`](vla_benchmark_dashboard.html) — *VLA Simulation Benchmarks · Visual Survey.*
A single page that compares all benchmarks: task-instruction word cloud, capability-vs-robustness
correlation, benchmark × model success heatmap, difficulty spread, simulator backbones, and per-benchmark
deep dives.

---

## Benchmarks

| Benchmark | Focus | Tasks | Data | Atlas |
|---|---|---|---|---|
| **Meta-World** | MT/ML multi-task & meta-RL manipulation | 50 | [`metaworld_tasks.csv`](metaworld/metaworld_tasks.csv) | [atlas](metaworld/metaworld_dashboard.html) |
| **RLBench** | Vision-guided tasks & multi-task leaderboard | 106 | [`rlbench_tasks.csv`](rlbench/rlbench_tasks.csv) | [atlas](rlbench/rlbench_dashboard.html) |
| **CALVIN** | Language-conditioned, long-horizon chaining | 34 | [`calvin_tasks.csv`](calvin/calvin_tasks.csv) · [`.json`](calvin/calvin_tasks.json) | [atlas](calvin/calvin_dashboard.html) |
| **RoboCasa365** | Kitchen atomic skills + composite activities | 67 atomic / 301 composite | [atomic](robocasa365/robocasa_atomic_tasks.csv) · [composite](robocasa365/robocasa_composite_tasks.csv) | [atomic](robocasa365/robocasa365_atomic_skills.html) · [composite](robocasa365/robocasa365_composite_tasks.html) |
| **BEHAVIOR-1K** | Long-horizon household activities (Challenge 2025) | 50 | [`behavior_challenge_50_tasks.csv`](Behavior1K/behavior_challenge_50_tasks.csv) | [atlas](Behavior1K/behavior_challenge_2025.html) |
| **RoboTwin** | Dual-arm manipulation tasks & instructions | — | — | [atlas](RoboTwin/robotwin_tasks.html) |
| **SimplerEnv** | Real-to-sim VLA evaluation setups | 7 | [`simplerenv_tasks.csv`](simplerenv/simplerenv_tasks.csv) | [atlas](simplerenv/simplerenv_dashboard.html) |
| **LW-BenchHub** | Lightwheel task hub (multi-suite) | 275 | [`lw_benchhub_tasks.csv`](lightwheel/lw_benchhub_tasks.csv) | [atlas](lightwheel/lw_benchhub_tasks.html) |

*Task counts reflect the rows in this repository's catalogs and may differ from a benchmark's full upstream
set. RoboTwin is currently published as an atlas only.*

---

## Repository layout

```
.
├── vla_benchmark_dashboard.html   # cross-benchmark visual survey
├── metaworld/                     # Meta-World MT/ML
│   ├── build_metaworld.py         #   builder script
│   ├── metaworld_tasks.csv        #   task catalog
│   └── metaworld_dashboard.html   #   interactive atlas
├── rlbench/                       # RLBench
├── calvin/                        # CALVIN (language + long-horizon)
├── robocasa365/                   # RoboCasa365 (atomic + composite)
├── Behavior1K/                    # BEHAVIOR-1K Challenge 2025
├── RoboTwin/                      # RoboTwin dual-arm
├── simplerenv/                    # SimplerEnv real-to-sim
└── lightwheel/                    # LW-BenchHub
```

Each benchmark folder follows the same convention:

- **`*_tasks.csv` / `.json`** — the task catalog: task names, categories/skills, and language instructions.
- **`build_*.py`** — the script that generates the catalog (where the source benchmark is installable).
- **`*_dashboard.html` / `*_tasks.html`** — a self-contained interactive atlas for that benchmark.

The HTML pages are static and self-contained — open any of them directly in a browser, or browse them all
via the [live site](https://everloom-129.github.io/blog).

---

## Notes

- All visualizations are single-file HTML with no build step or dependencies.
- Catalogs are normalized toward a shared shape (task / category / instruction) but keep
  benchmark-specific columns (e.g. block color in CALVIN, appliance in RoboCasa365, eval setups in
  SimplerEnv) where they matter.
- This is a reference compilation; each underlying benchmark is the work of its respective authors —
  please cite the original benchmark when using its tasks.
