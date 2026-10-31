"""Shared paths, constants and helpers for the who-was-big-when study.

Raw inputs (read in place, never copied into the repository):
  OPENF   openfootball/england (https://github.com/openfootball/england, public domain), 2022-23 match files, because
          2022-23 is missing from engsoccerdata.
  ESD     jalapic/engsoccerdata (https://github.com/jalapic/engsoccerdata, James P. Curley), R data files:
          data/england.rda (every English league match, tiers 1 to 4, 1888-89 to 2024-25),
          data/england_club_data.rda (club latitude and longitude), data/teamnames.rda (other names),
          data/deductions.rda (points deductions to 2014-15).
  GATES   gates.json: per-season attendance tables read from englishfootballleaguetables.co.uk
          ('Average League Gate': Div, Club, home position, home average, away position, away average),
          keyed by season '1888-89' to '2025-26' (war years missing; 2025-26 is part of a season and is not used).
          Only derived per-club-season home averages are published, with credit.
  GEO     /home/claude/newdata/raw/geo: counties_uk.geojson (England ceremonial counties, Welsh preserved
          counties), uk_topo.json (ONS regions), ne_10m_populated_places_simple.geojson (town names).
Intermediate files go to WORK, outside the repository.
"""
import json
import math
import os
import re
import unicodedata

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW2 = "/home/claude/newdata/raw2"
ESD = os.path.join(RAW2, "engsoccerdata", "data")
GATES = os.path.join(RAW2, "gates.json")
GEO = "/home/claude/newdata/raw/geo"
WORK = os.environ.get("BIGWORK", "/home/claude/newdata/work/who-was-big-when")
DATA = os.path.join(ROOT, "data")
FONT_DIR = os.environ.get("FONT_DIR", "/home/claude/ref/fonts")
for d in (WORK, DATA):
    os.makedirs(d, exist_ok=True)

SLUG = "who-was-big-when"
TITLE = "Who was big when? 126 seasons of English league football"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
BLOG_URL = f"https://blog.tristanhotham.com/2026/10/31/{SLUG}/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# palette: programme paper, floodlight ink, claret, sky, mustard
BG = "#F7F3EA"
FG = "#1F1D1A"
MUTED = "#6E675C"
RULE = "#E3DACA"
LAND = "#ECE5D6"
SEA = "#F7F3EA"
HOT = "#9B1B30"      # claret
COOL = "#2F5D8A"     # sky blue, darker
GOLD = "#D69A12"
TIER = {1: ("Top flight", "#9B1B30"), 2: ("Second tier", "#D9752B"), 3: ("Third tier", "#2F7F86"), 4: ("Fourth tier", "#6A5A9C")}
TIER_DARK = {1: "#E06A7B", 2: "#F0A060", 3: "#62BAC0", 4: "#A897DB"}

# areas for the North/South balance: ONS regions grouped
NORTH = ["North East", "North West", "Yorkshire and The Humber"]
MIDLANDS = ["East Midlands", "West Midlands"]
SOUTH = ["East of England", "London", "South East", "South West"]
BANDS = ["North", "Midlands", "London", "South (outside London)", "Wales"]


def band(region):
    if region in NORTH:
        return "North"
    if region in MIDLANDS:
        return "Midlands"
    if region == "London":
        return "London"
    if region in SOUTH:
        return "South (outside London)"
    return region


def season_label(y):
    return f"{y}-{str(y + 1)[-2:]}"


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower().replace("&", " and ")
    return re.sub(r"[\W_]+", " ", s).strip()


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if math.isnan(float(o)) else float(o)
    return o


def jsave(obj, path, indent=None):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(clean(obj), f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
