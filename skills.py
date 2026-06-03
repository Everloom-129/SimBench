#!/usr/bin/env python3
"""Shared verb->object skill ontology for the benchmark atlases.

This is the single source of truth for the *language analysis* that closes every
atlas page: the wordcloud's token categories (verb / object / spatial / color)
and the verb->skill taxonomy that sits right after it. Builders import from here
instead of redefining the maps, so skill labels stay comparable benchmark-to-
benchmark (see CLAUDE.md). Stdlib-only — no dependencies.

Usage:
    import skills
    skills.tokenize("Put the red block in the drawer")  -> ['put','red','block','drawer']
    skills.cat("drawer")                                -> 'object'
    skills.skill_of("Put the red block in the drawer")  -> 'Place'
"""
import re
from collections import OrderedDict

# ---- glue words dropped before any analysis (NOT verbs/objects/colors) ----
STOP = set((
    "the a an and or in on of to up at is be with for from down over under as by into onto off "
    "front back near it its this that these those all each any some make sure so then next while "
    "which what when where there here their them they he she his her are was were has have had will "
    "would can could should do does did not no yes every both one two three four five until after "
    "before again about your you i we us me my our out around along across toward towards if than "
    "but also still already correct use using place-holder per via etc go-to"
).split())

# ---- verb -> canonical skill family.  Order matters: families are scanned in
#      this order and the FIRST trigger verb found in an instruction wins, so the
#      primary action of a chained instruction is what gets counted. Each family
#      carries an accent color reused verbatim by the client-side renderers. -----
SKILLS = OrderedDict([
    ("Pick",        {"c": "#ff5436", "verbs": "pick grasp grab lift take retrieve raise pluck pickup hold collect get".split()}),
    ("Place",       {"c": "#f5b840", "verbs": "place put set insert stack drop deposit position load arrange hang lay sort replace store pack stow".split()}),
    ("Push/Pull",   {"c": "#46c4c0", "verbs": "push pull slide shove drag nudge collapse".split()}),
    ("Rotate",      {"c": "#9a7bff", "verbs": "rotate turn twist flip spin swivel screw unscrew".split()}),
    ("Open",        {"c": "#74c476", "verbs": "open unfasten unlock uncover".split()}),
    ("Close",       {"c": "#d98cff", "verbs": "close shut cover seal lock".split()}),
    ("Press/Toggle",{"c": "#5ad1ff", "verbs": "press toggle switch activate click hit beat tap".split()}),
    ("Pour/Fill",   {"c": "#ffa94d", "verbs": "pour fill empty spill scoop serve dump".split()}),
    ("Move/Reach",  {"c": "#8b9bb4", "verbs": "move reach navigate approach bring transport carry deliver align adjust operate".split()}),
    ("Wipe/Clean",  {"c": "#c9b458", "verbs": "wipe clean sweep wash scrub dust mop".split()}),
    ("Shape",       {"c": "#b07a5a", "verbs": "fold unfold roll wrap cut slice chop peel plug connect attach assemble fasten".split()}),
])
OTHER = "Other"
OTHER_COLOR = "#4a5161"

# reverse index verb -> family (built once, respects SKILLS order)
VERB2SKILL = {}
for _fam, _d in SKILLS.items():
    for _v in _d["verbs"]:
        VERB2SKILL.setdefault(_v, _fam)

# every trigger verb is a "verb" token for the wordcloud's coloring
VERB = set(VERB2SKILL) | set("go reach close open turn".split())
SPAT = set("top middle near left right front side between back bottom inside center upper lower behind above below corner edge".split())
COLOR = set("green yellow blue red pink black white orange purple brown gray grey".split())

_PLACEHOLDER = re.compile(r"\{[^}]*\}|<[^>]*>")  # {obj_lang}, {self.behavior}, <grab the hammer>
_WORD = re.compile(r"[a-z]+")


def clean(text):
    """Drop template placeholders / markup tags so they don't leak fake tokens."""
    return _PLACEHOLDER.sub(" ", text or "")


def tokenize(text):
    """Lowercase content tokens: stopwords removed, length >= 2."""
    return [w for w in _WORD.findall(clean(text).lower()) if w not in STOP and len(w) >= 2]


def cat(token):
    """Wordcloud color bucket for a single token."""
    if token in VERB:  return "verb"
    if token in COLOR: return "color"
    if token in SPAT:  return "spatial"
    return "object"


def skill_of(instruction):
    """Map an instruction to its primary manipulation skill family, or 'Other'.

    'turn on/off' and 'switch on/off' are toggles, not rotations — handled as a
    bigram before the plain verb lookup."""
    words = _WORD.findall(clean(instruction).lower())
    for i, w in enumerate(words):
        nxt = words[i + 1] if i + 1 < len(words) else ""
        if w in ("turn", "switch", "flip") and nxt in ("on", "off"):
            return "Press/Toggle"
        fam = VERB2SKILL.get(w)
        if fam:
            return fam
    return OTHER


def skill_color(family):
    return OTHER_COLOR if family == OTHER else SKILLS[family]["c"]
