"""Step 5. Build ../index.html from code/page_template.html: numbers from data/results.json (see fill.py),
a subset of results embedded as `const R = ...`, the shared full-screen map snippet pasted before </body>.
The page loads data/site.json, data/england_wales.geojson and data/towns.json itself. Claims made in words
are checked here."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
C, B, CH, LO = R["crowds"], R["balance"], R["champions"], R["lost"]
# claims in words
assert R["founders"]["north_west"] == 6 and R["founders"]["midlands"] == 6
assert R["london"]["first_season"] == "1893-94" and CH["first_london"] == "1930-31"
assert B["london_n_top_last"] == 7
assert C["first_games"] == 132 and C["peak_season"] == "1948-49" and C["low_season"] == "1985-86"
assert C["first_rise_after_low"] == "1986-87" and C["top_avg_growth_pl"] > 1.85
assert R["clubs_1923"] == 88
assert CH["north_to_1914"] + CH["midlands_to_1914"] == CH["n_to_1914"]
cs = pd.read_csv(os.path.join(DATA, "club_seasons.csv"))
ch = cs[(cs.tier == 1) & (cs.position == 1) & (cs.season >= 2000) & (cs.region == "North West")]
assert len(ch) == CH["north_since_2000"] and set(ch.town) == {"Manchester", "Liverpool"}
k = {r["team"]: r for r in R["crowd_kings"]["runs"]}
runs = R["crowd_kings"]["runs"]
assert runs[0]["name"] == "Everton" and runs[0]["to"] == 1897 and runs[1]["name"] == "Aston Villa"
assert [r["name"] for r in runs[2:7]] == ["Newcastle United", "Chelsea", "Manchester United", "Chelsea", "Manchester City"]
assert any(r["name"] == "Arsenal" and r["from"] == 1929 and r["to"] == 1938 for r in runs)
post = [r["name"] for r in runs if 1946 <= r["from"] < 1993]
assert set(post) == {"Newcastle United", "Tottenham Hotspur", "Arsenal", "Chelsea", "Everton", "Manchester United", "Liverpool"}, set(post)
assert R["crowd_kings"]["man_utd_since"] == "1993-94" and runs[-1]["name"] == "Manchester United" and runs[-1]["to"] == 2024
lost = {x["town"]: x for x in jload(os.path.join(DATA, "results.json"))["lost"]["recent"]}
LT = pd.read_csv(os.path.join(DATA, "lost_towns.csv")).set_index("town")
for t in ("Darwen", "Bootle", "Northwich", "Loughborough", "Gainsborough", "Glossop"):
    assert LT.loc[t, "last"] < 1915, t
for t in ("Merthyr Tydfil", "Aberdare", "Ashington", "Durham", "Nelson", "Stalybridge"):
    assert 1919 <= LT.loc[t, "last"] < 1940, t
for t in ("Barnet", "Oldham"):
    assert t not in LT.index, t
assert LT.loc["Carlisle", "last_label"] == "2024-25" and LT.loc["Morecambe", "last_label"] == "2024-25"
assert R["lost"]["membership_change"] == {"in": ["Barnet", "Oldham Athletic"], "out": ["Carlisle United", "Morecambe"]}
for t in ("Bury", "Rochdale", "Hartlepool", "Southend-on-Sea", "Scunthorpe", "Carlisle", "Morecambe"):
    assert LT.loc[t, "last"] >= 2000, t
assert LT.loc["Bury", "last"] == 2018 and LO["most_seasons"]["town"] == "Bury"
cb = {x["name"] for x in R["comebacks"]}
assert cb == {"Barrow", "Newport County", "Aldershot", "Wrexham", "Stockport County"}, cb
assert R["comebacks"][0]["name"] == "Barrow" and R["comebacks"][0]["out"] == "1971-72" and R["comebacks"][0]["back"] == "2020-21"
pk = R["peaks"]
assert pk["Preston North End"]["best_season"] == "1888-89" and pk["Huddersfield Town"]["titles"] == 3 and pk["Portsmouth"]["titles"] == 2
assert R["forest"] == {"t_1976": 2, "pos_1976": 3, "pos_1977": 1, "t_1977": 1}
for club, dec in (("Wolverhampton Wanderers", 1950), ("Burnley", 1950), ("Ipswich Town", 1960), ("Derby County", 1970)):
    assert any((cs.engsoccerdata_name == club) & (cs.tier == 1) & (cs.position == 1) & (cs.season // 10 * 10 == dec))
assert R["eras"][0]["centre_near"] == "Chapel-en-le-Frith" and R["eras"][5]["centre_near"] == "Market Bosworth"
assert R["data"]["n_unmatched"] == 5

EMB = {k: R[k] for k in ("eras", "peaks", "crowds", "data")}
EMB["peaks"] = {"by_decade": R["peaks"]["by_decade"]}
t = fill(open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read())
t = t.replace("/*DATA*/", "const R = " + json.dumps(clean(EMB), ensure_ascii=False, separators=(",", ":")) + ";")
t = t.replace("/*LAST*/0", str(int(R["data"]["last"][:4])))
t = t.replace("/*FULLSCREEN*/", open(os.path.join(HERE, "fullscreen_snippet.html"), encoding="utf-8").read())
check_visible(t, "index.html")
for scr in re.findall(r"<script>(.*?)</script>", t, flags=re.S):
    assert "—" not in scr and "–" not in scr
rest = re.findall(r"\{\{.*?\}\}", t)
assert set(rest) <= {"{{DOI}}", "https://blog.tristanhotham.com/2026/10/31/who-was-big-when/"}, rest[:5]
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t.encode()) // 1024, "KB")
