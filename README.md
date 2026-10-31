# Who was big when?

Every Football League and Premier League club's league position and average home crowd, season by season from 1888-89 to 2024-25, on a map of England and Wales that moves through time: 126 seasons, 147 clubs, 210,019 matches.

Interactive page: https://maps.tristanhotham.com/who-was-big-when/
Paper: https://doi.org/10.5281/zenodo.23844507
Blog post: https://blog.tristanhotham.com/2026/10/31/who-was-big-when/

## Headline results

- Total league crowds peaked at 41.2 million in 1948-49 (22,318 a match across four divisions), fell in 27 of the next 37 seasons to 16.5 million in 1985-86 (60% down), and recovered to 36.4 million in 2024-25 (88% of the peak). The recovery began in 1986-87.
- The top-flight average rose from 21,136 in 1992-93 to 40,430 in 2024-25, but the top flight's share of all league spectators (42%) is close to 1948-49 (43%).
- The twelve founders of 1888 were six from Lancashire and six from the Midlands. Before 1915 the North held 62% of top-flight places and London and the South 6%; since 2010, 36% and 43%. In 2024-25 the Premier League had 7 London clubs and 5 from the North. The crowd-weighted centre of the top flight moved about 78 km south.
- Titles stayed northern: 87 of 126 champions; since 2000-01, 17 of 25, all from Manchester or Liverpool. First London champion: Arsenal, 1930-31.
- Manchester United have had the biggest average home crowd in 56 seasons, every recorded season since 1993-94; the biggest in the data is 75,826 (2006-07).
- 39 of the 113 towns that have had a league club have none in 2025-26 (the 2024-25 clubs with that summer's promotions and relegations between League Two and the National League applied: in, Barnet and Oldham Athletic; out, Carlisle United and Morecambe); 20 lost it since 2000, among them Bury (expelled 2019 after 114 seasons).

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; loads `data/site.json`, `data/england_wales.geojson`, `data/towns.json`). |
| `header.png` | Social card, 1200 x 630. |
| `data/club_seasons.csv` | One row per club and season (9,828 rows): tier, division, position, pyramid rank, record, points, deductions, home games and average home league gate (1.3 MB). |
| `data/seasons.csv` | One row per season: clubs, matches, total and average league crowd, top-flight average, crowds by tier, area shares of top-flight places and crowds. |
| `data/club_peaks.csv` | One row per club: first and last season, titles, top-flight seasons, best finish, best decade, biggest crowd. |
| `data/lost_towns.csv` | The 39 towns that lost league football: clubs, seasons, last season, best finish, biggest crowd. |
| `data/clubs.csv` | Clubs with display name, engsoccerdata name, town, county, region, nation and ground point. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/site.json`, `data/england_wales.geojson`, `data/towns.json` | Page data: compact seasons, county outlines (ONS), town names (OS Open Names). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source, blog post, figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Tables rebuilt from every match: 2 points for a win until 1980-81, 3 from 1981-82; goal average until 1975-76, goal difference after; points deductions applied (engsoccerdata to 2014-15, published tables after); 2019-20 tiers 3 and 4 on points per game; expunged records (Wigan Borough 1931-32, Accrington Stanley 1961-62) removed; Leeds City 1919-20 credited to Port Vale. Champions and places checked against the record in more than fifty seasons.
- 2022-23 is missing from engsoccerdata and was filled from openfootball (2,036 matches).
- Pyramid rank: clubs in higher tiers plus position (1 = champions).
- Crowds: average home league gate per club and season from englishfootballleaguetables.co.uk, matched to engsoccerdata names season by season. 5 names unmatched, all expunged clubs: 1919-20: Leeds City; 1931-32: Wigan Borough; 1961-62: Accrington Stanley; 1991-92: Aldershot; 1992-93: Maidstone United. No crowds for 2020-21 (closed doors) or 2021-22 (the saved source page was a copy of 2022-23). Season total = average times home league matches.
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

Hotham, T. (2026) Who was big when? League position and crowds of every English league club, 1888-89 to 2024-25. Zenodo. https://doi.org/10.5281/zenodo.23844507

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
