# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A curated, published reference (https://everloom-129.github.io/blog) surveying VLA (Vision-Language-Action)
simulation manipulation benchmarks. It is **not a software library** — there are no tests, no lint config,
no package manager, and no dependencies beyond the Python 3 standard library. The deliverables are static
data files (CSV/JSON) and self-contained HTML "atlas" pages. See `README.md` for the user-facing catalog.

## Build commands

Every benchmark folder has one builder script that regenerates that benchmark's data + page:

```bash
python3 metaworld/build_metaworld.py      # → metaworld_tasks.csv + metaworld_dashboard.html
python3 build_index.py                    # → index.html (the landing gallery)
```

Scripts are stdlib-only (`json`, `csv`, `re`, `html`, `collections`, `os`) — no `pip install` needed.
There is no top-level "build everything" command; run each script individually. The generated `.csv`,
`.json`, and `.html` files are committed artifacts — regenerate and commit them when changing a builder.

## Architecture

**One folder per benchmark**, each self-contained with the same trio:
- `build_*.py` — generator script
- `*.csv` / `*_tasks.csv` / `.json` — the data (a task catalog, or an eval/leaderboard table)
- `*_dashboard.html` / `*_tasks.html` — a self-contained interactive atlas

**How a builder works:** the HTML is a raw Python string (`HTML = r'''...'''`) with the data injected as a
JSON blob (`json.dumps(...)`) that client-side JS renders. Pages pull only Google Fonts from a CDN —
otherwise fully standalone, openable directly in a browser. All pages share one "blueprint style" visual
identity (dark theme; Fraunces / Space Mono / IBM Plex Sans). When editing or adding a page, match that
aesthetic and the inject-JSON-into-template pattern rather than introducing a framework or build step.

**Each atlas closes with two analysis sections — wordcloud, then skill taxonomy.** The page's final
content (last numbered `<section>`s before the `<footer>`) is the *language analysis* of the task
instructions, in this fixed order:
1. **Wordcloud** — token frequency over the instructions. Python builds it with a `STOP`-word set + a
   `Counter` (see `metaworld/build_metaworld.py`: `wc.most_common(...)` → `DATA['words']`), and a
   `<canvas id="cloud">` renders it client-side, sized by frequency. Keep this.
2. **Verb–object skill taxonomy** (appended *after* the wordcloud) — parse each instruction into
   `(verb, object)` pairs, map each verb onto a shared skill ontology (pick / place / push / rotate /
   pour / open / …), and render the per-skill coverage. This is the deeper, comparable signal the
   wordcloud lacks; the wordcloud stays for visual identity, the taxonomy carries the analysis.

Both are computed in the builder (new `DATA['taxonomy']` key, same inject-JSON pattern) and live in the
builder template so they survive regeneration — and, like everything else, must be mirrored into the
`_cn.html` counterpart. When adding the taxonomy to a benchmark, reuse one shared verb→skill ontology
across builders rather than redefining it per page, so the skill labels stay comparable benchmark-to-benchmark.

**Every page ships bilingual (EN + 中文).** Each atlas and the index must exist as a matched pair: the
English page (`*.html`) and a Chinese mirror (`*_cn.html`) in the same folder. Both carry a fixed-position
`.langtoggle` button (top-right) that links to the other language — EN → `*_cn.html`, CN → `*.html`. When
you **create or add any new page, produce both versions in the same change** (never an EN page alone); when
you edit content on one, update its counterpart too so the pair stays in sync. For pages with a builder,
put the `.langtoggle` markup in the builder template so it survives regeneration (see
`molmospaces`/`roboverse`). The `_cn.html` files are hand-translated, not generated.

**Three kinds of data source** — know which before editing a builder:
1. **`/tmp/*.json` dumps** (`metaworld`, `libero`, `rlbench`, `colosseum`) — task lists extracted from the
   actual benchmark package in a *separate* environment, then read from `/tmp`. These will **not**
   regenerate from a clean checkout; the extraction step lives outside this repo.
2. **Local file** (`calvin` reads its own `calvin_tasks.json`) — self-contained, regenerates anywhere.
3. **Inline hardcoded** (`sim2real`, `memory`, `libero-plus`, `libero-pro`, and the leaderboard tables in
   most scripts) — numbers are typed into the script directly, each **annotated with an inline citation
   comment** (paper title + arXiv ID + table reference). Preserve and add these citations; the sourcing is
   the point — never invent or alter benchmark numbers without a cited source.

**`build_index.py`** generates the landing `index.html` from a hardcoded `SECTIONS` list of cards (title,
blurb, path, headline stat, accent color). Adding a new benchmark requires **manually adding a card** to
the relevant section here — the index does not auto-discover dashboards (it only checks that each listed
path exists).
