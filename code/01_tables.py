"""Step 1. Final league tables for every season and division, 1888-89 to 2024-25, from every match in
engsoccerdata's england.rda.

Rules: 2 points for a win before 1981-82 and 3 from 1981-82; ties broken by goal average (goals for divided
by goals against) to 1975-76 (1975-76 top flight already on goal difference, as in engsoccerdata's
maketable_eng), by goal difference from 1976-77, then goals scored. Points deductions from engsoccerdata's
deductions table (to 2014-15) plus later ones listed in LATER_DEDUCTIONS below. 2019-20 tiers 3 and 4 were
ended early and decided on points per game, as the league did. Output: WORK/tables.csv, one row per club and
season, with tier, division, position, played, won, drawn, lost, goals, points and pyramid rank (number of clubs
in higher tiers plus position; the two regional third divisions of 1921-22 to 1957-58 share the same offset).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import pandas as pd
import pyreadr

E = pyreadr.read_r(os.path.join(ESD, "england.rda"))["england"]
E["Season"] = E["Season"].astype(int); E["tier"] = E["tier"].astype(int)
# records expunged when a club left mid-season: Wigan Borough 1931-32, Accrington Stanley 1961-62.
# Leeds City were expelled in October 1919 and Port Vale took over their fixtures and record.
for yr, club in ((1931, "Wigan Borough"), (1961, "Accrington Stanley")):
    E = E[~((E.Season == yr) & ((E.home == club) | (E.visitor == club)))]
for col in ("home", "visitor"):
    E.loc[(E.Season == 1919) & (E[col] == "Leeds City"), col] = "Port Vale"
E.loc[(E.Season == 1931) & (E.division == "3"), "division"] = "3N"


def openfootball_2022():
    """2022-23 is missing from engsoccerdata's england.rda; read it from openfootball/england (public domain),
    files 2022-23/1-premierleague.txt to 4-league2.txt, regular season only (play-offs left out)."""
    out = []
    for tier, fn in enumerate(["1-premierleague", "2-championship", "3-league1", "4-league2"], start=1):
        for ln in open(os.path.join(OPENF, fn + ".txt"), encoding="utf-8"):
            if re.match(r"^\W*Play-?offs?", ln.strip()):
                break
            m = re.match(r"^\s+(?:\d\d:\d\d\s+)?(\S.*?)\s+(\d+)-(\d+)(?:\s+\(\d+-\d+\))?\s+(\S.*?)\s*$", ln)
            if m:
                out.append({"Season": 2022, "home": m.group(1), "visitor": m.group(4), "hgoal": int(m.group(2)), "vgoal": int(m.group(3)),
                            "division": str(tier), "tier": tier})
    df = pd.DataFrame(out)
    known = set(E.home) | set(E.visitor)

    def fix(n):
        n0 = n
        n = re.sub(r"\s+(A\.?F\.?C\.?|F\.?C\.?)$", "", n)
        n = {"Stevenage": "Stevenage Borough", "Harrogate Town": "Harrogate Town A.F.C.", "Accrington Stanley": "Accrington",
             "Cheltenham Town": "Cheltenham", "Yeovil Town": "Yeovil", "Dagenham & Redbridge": "Dagenham and Redbridge",
             "Bournemouth": "AFC Bournemouth", "Wimbledon": "AFC Wimbledon", "MK Dons": "Milton Keynes Dons"}.get(n, n)
        if n in known:
            return n
        raise ValueError(n0)
    df["home"] = df.home.map(fix); df["visitor"] = df.visitor.map(fix)
    assert df.groupby("tier").size().to_dict() == {1: 380, 2: 552, 3: 552, 4: 552}, df.groupby("tier").size()
    return df


OPENF = os.path.join(RAW2, "openfootball_2022-23")
E = pd.concat([E, openfootball_2022()], ignore_index=True)
N_MATCHES = len(E)
DED = pyreadr.read_r(os.path.join(ESD, "deductions.rda"))["deductions"]
DED = {(int(r.Season), r.team): int(r.deduction) for r in DED.itertuples()}
# deductions after engsoccerdata's table ends (2015-16 onwards), from the published final tables
LATER_DEDUCTIONS = {
    (2018, "Birmingham City"): 9,
    (2019, "Wigan Athletic"): 12, (2019, "Bolton Wanderers"): 12, (2019, "Macclesfield Town"): 17,
    (2020, "Sheffield Wednesday"): 6,
    (2021, "Derby County"): 21, (2021, "Reading"): 6,
    (2022, "Reading"): 6, (2022, "Wigan Athletic"): 3,
    (2023, "Everton"): 8, (2023, "Nottingham Forest"): 4, (2023, "Reading"): 4, (2023, "Wigan Athletic"): 8,
}
DED.update(LATER_DEDUCTIONS)

rows = []
for (season, div), g in E.groupby(["Season", "division"]):
    tier = int(g["tier"].iloc[0])
    h = pd.DataFrame({"team": g["home"], "gf": g["hgoal"], "ga": g["vgoal"]})
    a = pd.DataFrame({"team": g["visitor"], "gf": g["vgoal"], "ga": g["hgoal"]})
    t = pd.concat([h, a])
    t["w"] = (t.gf > t.ga).astype(int); t["d"] = (t.gf == t.ga).astype(int); t["l"] = (t.gf < t.ga).astype(int)
    hp = g.groupby("home").size()
    T = t.groupby("team").agg(p=("gf", "size"), w=("w", "sum"), d=("d", "sum"), l=("l", "sum"), gf=("gf", "sum"), ga=("ga", "sum")).reset_index()
    T["hp"] = T.team.map(hp).fillna(0).astype(int)
    win = 3 if season >= 1981 else 2
    T["ded"] = [DED.get((season, tm), 0) for tm in T.team]
    T["pts"] = T.w * win + T.d - T.ded
    T["gd"] = T.gf - T.ga
    T["gav"] = T.gf / T.ga.replace(0, 0.5)
    tiebreak = "gav" if (season <= 1974 or (season == 1975 and tier > 1)) else "gd"
    if season == 2019 and tier in (3, 4):
        T["ppg"] = T.pts / T.p
        T = T.sort_values(["ppg", tiebreak, "gf"], ascending=False)
    else:
        T = T.sort_values(["pts", tiebreak, "gf"], ascending=False)
    T["pos"] = range(1, len(T) + 1)
    T["season"] = season; T["tier"] = tier; T["division"] = div; T["n_div"] = len(T)
    rows.append(T)
tab = pd.concat(rows, ignore_index=True)

# pyramid rank: clubs in higher tiers plus position (3N and 3S share the third-tier offset)
tier_size = tab.groupby(["season", "tier"]).team.size().unstack()
div_max = tab.groupby(["season", "tier"]).n_div.max().unstack()


def offset(r):
    above = 0
    for k in range(1, r.tier):
        above += div_max.loc[r.season, k]
    return above


tab["rank"] = [offset(r) + r.pos for r in tab.itertuples()]
tab["n_league"] = tab.season.map(tab.groupby("season").team.size())

# odd numbers of games: report (Leeds City 1919-20, Accrington Stanley 1961-62, Bury 2019-20 and so on)
odd = tab[tab.p != tab.groupby(["season", "division"]).p.transform("max")]
print("clubs with fewer games than their division:\n", odd[["season", "division", "team", "p"]].to_string())

# famous champions, checked
champ = tab[(tab.tier == 1) & (tab.pos == 1)].set_index("season").team
CHECK = {1888: "Preston North End", 1889: "Preston North End", 1890: "Everton", 1891: "Sunderland", 1893: "Aston Villa", 1894: "Sunderland",
         1904: "Newcastle United", 1907: "Manchester United", 1914: "Everton", 1919: "West Bromwich Albion", 1922: "Liverpool",
         1923: "Huddersfield Town", 1924: "Huddersfield Town", 1925: "Huddersfield Town", 1930: "Arsenal", 1935: "Sunderland", 1936: "Manchester City",
         1938: "Everton", 1946: "Liverpool", 1948: "Portsmouth", 1949: "Portsmouth", 1950: "Tottenham Hotspur",
         1953: "Wolverhampton Wanderers", 1954: "Chelsea", 1955: "Manchester United", 1959: "Burnley", 1960: "Tottenham Hotspur",
         1961: "Ipswich Town", 1964: "Manchester United", 1967: "Manchester City", 1968: "Leeds United", 1970: "Arsenal",
         1971: "Derby County", 1974: "Derby County", 1977: "Nottingham Forest", 1979: "Liverpool", 1980: "Aston Villa",
         1984: "Everton", 1988: "Arsenal", 1989: "Liverpool", 1991: "Leeds United", 1992: "Manchester United",
         1994: "Blackburn Rovers", 1997: "Arsenal", 2003: "Arsenal", 2004: "Chelsea", 2011: "Manchester City",
         2015: "Leicester City", 2019: "Liverpool", 2022: "Manchester City", 2023: "Manchester City", 2024: "Liverpool"}
bad = {s: (c, champ.get(s)) for s, c in CHECK.items() if champ.get(s) != c}
assert not bad, bad
# goal average decided 1923-24 (Huddersfield over Cardiff); goal difference 1988-89 (Arsenal over Liverpool, equal on points and GD, Arsenal more goals)
assert tab[(tab.season == 1923) & (tab.tier == 1) & (tab.pos == 2)].team.iloc[0] == "Cardiff City"
assert tab[(tab.season == 2011) & (tab.tier == 1) & (tab.pos == 2)].team.iloc[0] == "Manchester United"
for tr, club in ((2, "Burnley"), (3, "Plymouth Argyle"), (4, "Leyton Orient")):
    assert tab[(tab.season == 2022) & (tab.tier == tr) & (tab.pos == 1)].team.iloc[0] == club
assert tab[(tab.season == 2023) & (tab.tier == 1) & (tab.team == "Everton")].pos.iloc[0] == 15
assert tab[(tab.season == 2021) & (tab.tier == 2) & (tab.team == "Derby County")].pos.iloc[0] == 23
print("seasons", tab.season.nunique(), tab.season.min(), tab.season.max(), "club-seasons", len(tab), "clubs", tab.team.nunique())
jsave({"n_matches": N_MATCHES, "n_matches_raw": 208028, "n_matches_2022_openfootball": 2036}, os.path.join(WORK, "matches.json"))
tab.drop(columns=["gav"]).to_csv(os.path.join(WORK, "tables.csv"), index=False)
