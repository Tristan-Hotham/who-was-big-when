"""Step 2. Average home league gates per club and season from gates.json (tables read from
englishfootballleaguetables.co.uk), matched to the engsoccerdata club names of the same season.

Only the first table of each season ('Average League Gate') is used: Div, Club, home rank, home average,
away rank, away average. 2025-26 is part of a season and is left out; 1939-40 (abandoned after three games)
is not in the match data and is left out. Matching is within a season: exact name, then normalised name,
then the alias list below, then a unique match on the first word. Anything left over is reported and saved to
WORK/gates_unmatched.json. Output: WORK/gates.csv (season, team, home_avg, away_avg, gate_div).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import pandas as pd

G = jload(GATES)
T = pd.read_csv(os.path.join(WORK, "tables.csv"))
ALIAS = {  # gates name -> engsoccerdata name (any season)
    "Accrington": "Accrington F.C.", "Arsenal": "Arsenal", "Woolwich Arsenal": "Arsenal", "Royal Arsenal": "Arsenal",
    "The Arsenal": "Arsenal", "Small Heath": "Birmingham City", "Birmingham": "Birmingham City",
    "Newton Heath": "Manchester United", "Ardwick": "Manchester City", "Thames Association": "Thames",
    "Bournemouth & Boscombe Athletic": "AFC Bournemouth", "Bournemouth": "AFC Bournemouth", "AFC Bournemouth": "AFC Bournemouth",
    "Leicester Fosse": "Leicester City", "Orient": "Leyton Orient", "Clapton Orient": "Leyton Orient", "Leyton Orient": "Leyton Orient",
    "Swansea Town": "Swansea City", "Hull City": "Hull City", "Stoke": "Stoke City", "Coventry City": "Coventry City",
    "Wimbledon": "Wimbledon", "MK Dons": "Milton Keynes Dons", "Milton Keynes Dons": "Milton Keynes Dons",
    "Stevenage": "Stevenage Borough", "Harrogate Town": "Harrogate Town A.F.C.", "Cheltenham Town": "Cheltenham",
    "Yeovil Town": "Yeovil", "Macclesfield Town": "Macclesfield", "Hartlepools United": "Hartlepool United", "Hartlepool": "Hartlepool United",
    "Hartlepool United": "Hartlepool United", "Dagenham & Redbridge": "Dagenham and Redbridge", "Sheffield Wednesday": "Sheffield Wednesday",
    "The Wednesday": "Sheffield Wednesday", "Wednesday": "Sheffield Wednesday", "Chester City": "Chester", "Rotherham County": "Rotherham County",
    "Accrington Stanley": "Accrington Stanley", "Gateshead": "Gateshead", "South Shields": "South Shields",
    "Glossop": "Glossop North End", "Burslem Port Vale": "Port Vale", "Bradford": "Bradford Park Avenue", "Bradford Park Avenue": "Bradford Park Avenue",
    "Brighton & Hove Albion": "Brighton & Hove Albion", "Rushden & Diamonds": "Rushden & Diamonds", "Middlesbrough Ironopolis": "Middlesbrough Ironopolis",
    "New Brighton Tower": "New Brighton Tower", "Manchester Central": None,
}
DIVMAP = {}
rows, unmatched = [], {}
# a season whose table is a copy of another season's (the scrape of 2021-22 returned 2022-23's table): left out
first_rows = {}
for s, tabs in G.items():
    if tabs:
        first_rows.setdefault(tuple(tabs[0].split("\n")[2:12]), []).append(s)
DUP = {}
for ss in first_rows.values():
    if len(ss) > 1:
        for s in ss:
            y = int(s[:4]); names = set(T[T.season == y].team)
            DUP[s] = sum(ln.split("\t")[1].strip() in names for ln in G[s][0].split("\n")[2:] if "\t" in ln)
        best = max(ss, key=lambda s: DUP[s])
        for s in ss:
            if s != best:
                print("gate table for", s, "is a copy of", best, "(left out)")
                G[s] = []; DUP[s] = best
DUP = {k: v for k, v in DUP.items() if isinstance(v, str)}
for s, tabs in G.items():
    y = int(s[:4])
    if s == "2025-26":
        continue
    cl = T[T.season == y]
    if cl.empty:
        print("no match data for", s, "(left out)")
        continue
    names = set(cl.team)
    if not tabs:
        print("no gate table for", s, "(copy of " + DUP[s] + ")" if s in DUP else "(matches played behind closed doors)")
        continue
    lines = tabs[0].strip().split("\n")
    assert lines[0].startswith("Div\tClub") and "Home" in lines[1], lines[:2]
    seen, todo = {}, []
    to_n = lambda v: int(v.replace(",", "")) if v.strip().replace(",", "").isdigit() else None
    nn = {norm(n): n for n in names}
    for ln in lines[2:]:
        f = ln.split("\t")
        if len(f) < 4 or not f[1].strip():
            continue
        div, club, havg = f[0].strip(), f[1].strip(), f[3]
        if div == "FA":      # Football Alliance (1889-92), not the Football League
            continue
        rec = {"season": y, "gate_name": club, "gate_div": div, "home_avg": to_n(havg), "away_avg": to_n(f[5]) if len(f) > 5 else None}
        team = club if club in names else nn.get(norm(club)) or (ALIAS.get(club) if ALIAS.get(club) in names else None)
        if team:
            assert team not in seen, (s, club, team, seen.get(team))
            seen[team] = club; rec["team"] = team; rows.append(rec)
        else:
            todo.append(rec)
    for rec in todo:     # second pass: a unique unclaimed club with the same first word
        club = rec["gate_name"]
        w = norm(club).split()[0]
        cand = [n for n in names - set(seen) if norm(n).split()[0] == w]
        if len(cand) == 1:
            seen[cand[0]] = club; rec["team"] = cand[0]; rows.append(rec)
        else:
            unmatched.setdefault(s, []).append(club)
gt = pd.DataFrame(rows)
# matches that changed the name, for the record
renamed = gt[gt.team != gt.gate_name][["gate_name", "team"]].drop_duplicates().sort_values("team")
print(renamed.to_string())
print("unmatched gate names:", unmatched)
# coverage: club-seasons in the tables with a gate
m = T.merge(gt, on=["season", "team"], how="left")
cov = m.groupby("season").home_avg.apply(lambda v: v.notna().mean())
print("seasons with incomplete gates:\n", cov[cov < 1].to_string())
gt.to_csv(os.path.join(WORK, "gates.csv"), index=False)
jsave({"duplicate_left_out": DUP, "unmatched": unmatched, "renamed": renamed.values.tolist(), "n_rows": len(gt),
       "coverage": {int(k): float(v) for k, v in cov.items()}}, os.path.join(WORK, "gates_match.json"), indent=1)
