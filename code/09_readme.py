"""Step 9. README.md and LICENSE, numbers from data/results.json."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

C, B, CH, LO, D = R["crowds"], R["balance"], R["champions"], R["lost"], R["data"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
readme = f"""# Who was big when?

Every Football League and Premier League club's league position and average home crowd, season by season from {D['first']} to {D['last']}, on a map of England and Wales that moves through time: {D['n_seasons']} seasons, {D['n_clubs']} clubs, {D['n_matches']:,} matches.

Interactive page: {PAGE}
Paper: https://doi.org/{{{{DOI}}}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/who-was-big-when/}}

## Headline results

- Total league crowds peaked at {X['x_peak_m']} million in {C['peak_season']} ({C['peak_avg']:,.0f} a match across four divisions), fell in {C['n_decline_seasons']} of the next {C['n_decline_span']} seasons to {X['x_low_m']} million in {C['low_season']} ({X['x_fall_pct']} down), and recovered to {X['x_last_m']} million in {C['last_season']} ({X['x_last_vs_peak']} of the peak). The recovery began in {C['first_rise_after_low']}.
- The top-flight average rose from {C['pl1_top_avg']:,.0f} in 1992-93 to {C['last_top_avg']:,.0f} in {C['last_season']}, but the top flight's share of all league spectators ({C['t1_share_last'] * 100:.0f}%) is close to {C['peak_season']} ({C['t1_share_peak'] * 100:.0f}%).
- The twelve founders of 1888 were six from Lancashire and six from the Midlands. Before 1915 the North held {B['north_top_first'] * 100:.0f}% of top-flight places and London and the South {B['south_top_first'] * 100:.0f}%; since 2010, {B['north_top_last'] * 100:.0f}% and {B['south_top_last'] * 100:.0f}%. In {C['last_season']} the Premier League had {B['london_n_top_last']} London clubs and {B['north_n_top_last']} from the North. The crowd-weighted centre of the top flight moved about {X['x_centre_km']} km south.
- Titles stayed northern: {CH['by_band']['North']} of {CH['n']} champions; since 2000-01, {CH['north_since_2000']} of {CH['n_since_2000']}, all from Manchester or Liverpool. First London champion: Arsenal, {CH['first_london']}.
- Manchester United have had the biggest average home crowd in {X['x_mu_kings']} seasons, every recorded season since {R['crowd_kings']['man_utd_since']}; the biggest in the data is {R['crowd_kings']['biggest']['avg']:,.0f} ({R['crowd_kings']['biggest']['season']}).
- {LO['n']} of the {LO['n_towns_ever']} towns that have had a league club have none in {LO['today']} (the {C['last_season']} clubs with that summer's promotions and relegations between League Two and the National League applied: in, {' and '.join(LO['membership_change']['in'])}; out, {' and '.join(LO['membership_change']['out'])}); {LO['since_2000']} lost it since 2000, among them Bury (expelled 2019 after {LO['most_seasons']['seasons']} seasons).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; loads `data/site.json`, `data/england_wales.geojson`, `data/towns.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/club_seasons.csv` | One row per club and season ({D['n_club_seasons']:,} rows): tier, division, position, pyramid rank, record, points, deductions, home games and average home league gate ({size('club_seasons.csv')}). |
| `data/seasons.csv` | One row per season: clubs, matches, total and average league crowd, top-flight average, crowds by tier, area shares of top-flight places and crowds. |
| `data/club_peaks.csv` | One row per club: first and last season, titles, top-flight seasons, best finish, best decade, biggest crowd. |
| `data/lost_towns.csv` | The {LO['n']} towns that lost league football: clubs, seasons, last season, best finish, biggest crowd. |
| `data/clubs.csv` | Clubs with display name, engsoccerdata name, town, county, region, nation and ground point. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/england_wales.geojson`, `data/towns.json` | Page data: compact seasons, county outlines (ONS), town names (OS Open Names). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source, blog post, figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Tables rebuilt from every match: 2 points for a win until 1980-81, 3 from 1981-82; goal average until 1975-76, goal difference after; points deductions applied (engsoccerdata to 2014-15, published tables after); 2019-20 tiers 3 and 4 on points per game; expunged records (Wigan Borough 1931-32, Accrington Stanley 1961-62) removed; Leeds City 1919-20 credited to Port Vale. Champions and places checked against the record in more than fifty seasons.
- 2022-23 is missing from engsoccerdata and was filled from openfootball ({D['n_matches_2022']:,} matches).
- Pyramid rank: clubs in higher tiers plus position (1 = champions).
- Crowds: average home league gate per club and season from englishfootballleaguetables.co.uk, matched to engsoccerdata names season by season. {D['n_unmatched']} names unmatched, all expunged clubs: {'; '.join(f"{k}: {', '.join(v)}" for k, v in D['unmatched'].items())}. No crowds for 2020-21 (closed doors) or 2021-22 (the saved source page was a copy of 2022-23). Season total = average times home league matches.
- Places: present or last ground (engsoccerdata club table, Coventry City and Harrogate Town corrected); ONS regions grouped into North, Midlands, London, rest of the South and Wales; town assigned by hand.
- Caveats: early crowds are estimates; clubs drawn at one ground for all seasons; position and crowd are only two measures of size.

## Sources and licences

- Match results: James P. Curley, engsoccerdata, https://github.com/jalapic/engsoccerdata (https://doi.org/10.5281/zenodo.13158). Package code GPL-3; results are facts, credited as the author asks.
- 2022-23 results: openfootball/england, https://github.com/openfootball/england. Public domain (CC0).
- Average league gates: englishfootballleaguetables.co.uk. Only per-club, per-season averages derived from its tables are published here, with credit; its pages are not redistributed.
- Boundaries: Office for National Statistics (Open Government Licence v3.0). Town names: OS Open Names (Open Government Licence v3.0), via https://github.com/Tristan-Hotham/dark-skies.
- Base map tiles on the page: © Esri.

## How to rerun

Needs Python 3 with pandas, geopandas, pyreadr, matplotlib, fontTools and Playwright, xelatex and pdftotext. Raw inputs are read in place (paths in `code/common.py`): engsoccerdata's `data/*.rda`, `gates.json` (the attendance tables), and the openfootball 2022-23 match files. Intermediate files go to `/home/claude/newdata/work/who-was-big-when` (set `BIGWORK` to change).

```
python3 code/01_tables.py      # final tables from every match
python3 code/02_gates.py       # average league gates, matched to clubs
python3 code/03_clubs_geo.py   # clubs, towns, regions, outlines
python3 code/04_results.py     # results.json and data files
python3 code/05_build_site.py  # index.html
python3 code/06_figures.py     # paper and blog figures
python3 code/07_header.py      # header.png
python3 code/08_paper.py       # paper PDF
python3 code/09_readme.py      # README and LICENSE
python3 code/10_release.py     # blog post, Zenodo files
python3 reddit/collage.py      # collage
python3 code/12_qa.py          # screenshots and console check
```

## Citation

Hotham, T. (2026) Who was big when? League position and crowds of every English league club, {D['first']} to {D['last']}. Zenodo. https://doi.org/{{{{DOI}}}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--"):
    assert bad not in readme.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/ and reddit/collage.py and the page
scripts. The text of the page, the figures and the derived data files in data/
are released under CC BY 4.0. Match results are from engsoccerdata (James P.
Curley) and openfootball (public domain). Average league gates are derived
from englishfootballleaguetables.co.uk and must be credited to it when reused.
Boundaries: Office for National Statistics, Open Government Licence v3.0.
Town names: OS Open Names, Open Government Licence v3.0.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
