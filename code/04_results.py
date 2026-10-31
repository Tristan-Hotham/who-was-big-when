"""Step 4. Join tables, gates and clubs; compute every number used anywhere; write the clean data files
and the page data.

Outputs:
  data/club_seasons.csv   one row per club and season: tier, division, position, pyramid rank, record, points,
                          average home league gate (from englishfootballleaguetables.co.uk) and region
  data/seasons.csv        one row per season: clubs, matches, total and average league crowd, top-flight average,
                          shares of top-flight places and of all league crowds by area
  data/club_peaks.csv     one row per club: best season, best decade, biggest crowd season, first and last season
  data/lost_towns.csv     towns that once had a league club and have none in the league today (2025-26 membership)
  data/results.json       every number quoted in the page, paper, blog, collage and post
  data/site.json          compact page data (loaded by index.html)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import pandas as pd

T = pd.read_csv(os.path.join(WORK, "tables.csv"))
G = pd.read_csv(os.path.join(WORK, "gates.csv"))
CL = jload(os.path.join(WORK, "clubs.json"))
GM = jload(os.path.join(WORK, "gates_match.json"))
MT = jload(os.path.join(WORK, "matches.json"))
CK = {c["key"]: c for c in CL}
M = T.merge(G[["season", "team", "home_avg", "away_avg"]], on=["season", "team"], how="left")
for k in ("name", "town", "region", "band", "county", "nation", "lat", "lon"):
    M[k] = M.team.map(lambda t: CK[t][k])
M["crowd"] = M.home_avg * M.hp
M["decade"] = (M.season // 10) * 10
LAST = int(M.season.max()); FIRST = int(M.season.min())
NO_GATES = sorted(int(s) for s in M.groupby("season").home_avg.count().pipe(lambda x: x[x == 0]).index)
assert NO_GATES == [2020, 2021], NO_GATES
R = {"meta": {"page": PAGE, "repo": REPO, "slug": SLUG}}

# ---- coverage ----
seasons = sorted(M.season.unique())
R["data"] = {"n_seasons": len(seasons), "first": season_label(FIRST), "last": season_label(LAST), "n_clubs": int(M.team.nunique()),
             "n_club_seasons": len(M), "n_matches": MT["n_matches"], "n_matches_2022": MT["n_matches_2022_openfootball"],
             "n_gate_rows": int(M.home_avg.notna().sum()), "n_gate_seasons": int(M[M.home_avg.notna()].season.nunique()),
             "unmatched": GM["unmatched"], "n_unmatched": sum(len(v) for v in GM["unmatched"].values()),
             "years_span": LAST + 1 - FIRST, "n_towns": len(set(c["town"] for c in CL))}

# ---- crowds by season ----
S = M.groupby("season").agg(clubs=("team", "size"), games=("hp", "sum"), total=("crowd", "sum"), n_gate=("home_avg", "count")).reset_index()
S.loc[S.n_gate == 0, "total"] = np.nan
S["avg"] = S.total / S.games
S["top_avg"] = S.season.map(M[M.tier == 1].groupby("season").home_avg.mean())
for tr in (1, 2, 3, 4):
    S[f"total_t{tr}"] = S.season.map(M[M.tier == tr].groupby("season").crowd.sum()).where(S.n_gate > 0)
for b in BANDS:
    S["top_share_" + b] = S.season.map(M[M.tier == 1].groupby("season").band.apply(lambda v: (v == b).mean()))
    S["crowd_share_" + b] = S.season.map(M.groupby("season").apply(lambda d: d.loc[d.band == b, "crowd"].sum() / d.crowd.sum() if d.crowd.sum() else np.nan, include_groups=False))
peak = S.loc[S.total.idxmax()]; low_post = S[(S.season > 1948)].loc[S[(S.season > 1948)].total.idxmin()]
assert int(peak.season) == 1948 and int(low_post.season) == 1985, (peak.season, low_post.season)
pre1 = S[S.season < 1915].loc[S[S.season < 1915].total.idxmax()]
inter = S[(S.season > 1918) & (S.season < 1939)]
last = S[S.season == LAST].iloc[0]
pl1 = S[S.season == 1992].iloc[0]
R["crowds"] = {
    "first_total": S.iloc[0].total, "first_avg": S.iloc[0].avg,
    "peak_season": season_label(int(peak.season)), "peak_total": peak.total, "peak_avg": peak.avg, "peak_top_avg": peak.top_avg,
    "pre1915_peak_season": season_label(int(pre1.season)), "pre1915_peak_total": pre1.total,
    "inter_peak_season": season_label(int(inter.loc[inter.total.idxmax()].season)), "inter_peak_total": inter.total.max(),
    "low_season": season_label(int(low_post.season)), "low_total": low_post.total, "low_avg": low_post.avg, "low_top_avg": low_post.top_avg,
    "fall_pct": 1 - low_post.total / peak.total,
    "last_season": season_label(LAST), "last_total": last.total, "last_avg": last.avg, "last_top_avg": last.top_avg,
    "last_vs_peak": last.total / peak.total, "last_vs_low": last.total / low_post.total,
    "pl1_season": "1992-93", "pl1_total": pl1.total, "pl1_top_avg": pl1.top_avg,
    "top_avg_growth_pl": last.top_avg / pl1.top_avg,
    "t1_share_last": last.total_t1 / last.total, "t1_share_peak": peak.total_t1 / peak.total,
    "lower_last": last.total - last.total_t1, "lower_peak": peak.total - peak.total_t1,
    "post_war_above_40m": [season_label(int(s)) for s in S[S.total >= 40e6].season],
    "years_above_last_total": [season_label(int(s)) for s in S[S.total > last.total].season],
}
R["crowds"]["first_games"] = int(S.iloc[0].games)
dec = S[(S.season >= 1948) & (S.season <= 1985)].set_index("season").total
R["crowds"]["n_decline_seasons"] = int((dec.diff() < 0).sum()); R["crowds"]["n_decline_span"] = int(len(dec) - 1)
R["crowds"]["first_rise_after_low"] = season_label(int(S[(S.season > 1985) & (S.total > low_post.total)].season.min()))
h48 = M[(M.season == 1948)]
hull = float(h48[h48.team == "Hull City"].home_avg.iloc[0])
R["crowds"]["hull_1948"] = hull
R["crowds"]["hull_1948_beat_top"] = int((h48[h48.tier == 1].home_avg < hull).sum())
R["crowds"]["n_top_1948"] = int((h48.tier == 1).sum())
R["crowds"]["first_season_beating_last"] = R["crowds"]["years_above_last_total"][0]
R["crowds"]["last_season_beating_last"] = R["crowds"]["years_above_last_total"][-1]
R["crowds"]["n_seasons_beating_last"] = len(R["crowds"]["years_above_last_total"])

# ---- biggest crowds: the best-supported club each season ----
top = M[M.home_avg.notna()].sort_values("home_avg", ascending=False).groupby("season").head(1).sort_values("season")
runs = []
for r in top.itertuples():
    gated = sorted(top.season)   # consecutive among seasons that have gates (wars and 2020-22 skipped)
    if runs and runs[-1]["team"] == r.team and gated.index(runs[-1]["to"]) == gated.index(r.season) - 1:
        runs[-1]["to"] = int(r.season); runs[-1]["n"] += 1
    else:
        runs.append({"team": r.team, "name": r.name, "from": int(r.season), "to": int(r.season), "n": 1})
crowd_kings = top.team.value_counts()
R["crowd_kings"] = {"runs": runs, "counts": [{"name": CK[t]["name"], "n": int(n)} for t, n in crowd_kings.items()],
                    "n_clubs": int(top.team.nunique())}
mu = int(crowd_kings.get("Manchester United", 0))
R["crowd_kings"]["man_utd"] = mu
R["crowd_kings"]["man_utd_since"] = season_label(min(r["from"] for r in runs if r["team"] == "Manchester United" and r["to"] >= LAST))
R["crowd_kings"]["biggest"] = {"name": top.loc[top.home_avg.idxmax()]["name"], "season": season_label(int(top.loc[top.home_avg.idxmax()].season)), "avg": top.home_avg.max()}
first_king = top.iloc[0]
R["crowd_kings"]["first"] = {"name": first_king["name"], "avg": first_king.home_avg}

# ---- champions and their regions ----
ch = M[(M.tier == 1) & (M.pos == 1)].sort_values("season")
R["champions"] = {"n": len(ch), "n_clubs": int(ch.team.nunique()),
                  "by_band": {b: int((ch.band == b).sum()) for b in BANDS},
                  "first_london": season_label(int(ch[ch.band == "London"].season.min())),
                  "first_london_club": ch[ch.band == "London"].iloc[0]["name"],
                  "first_south": season_label(int(ch[ch.band == "South (outside London)"].season.min())),
                  "first_south_club": ch[ch.band == "South (outside London)"].iloc[0]["name"],
                  "north_to_1914": int(((ch.band == "North") & (ch.season < 1915)).sum()), "n_to_1914": int((ch.season < 1915).sum()),
                  "midlands_to_1914": int(((ch.band == "Midlands") & (ch.season < 1915)).sum()),
                  "london_since_2000": int(((ch.band == "London") & (ch.season >= 2000)).sum()), "n_since_2000": int((ch.season >= 2000).sum()),
                  "north_since_2000": int(((ch.band == "North") & (ch.season >= 2000)).sum())}
assert ch.iloc[0]["name"] == "Preston North End" and R["champions"]["first_london_club"] == "Arsenal"

# ---- founders, first London club, London ----
f = M[M.season == FIRST]
R["founders"] = {"n": len(f), "north_west": int((f.region == "North West").sum()), "midlands": int((f.band == "Midlands").sum()),
                 "names": sorted(f.name.tolist()), "still_top": int(M[(M.season == LAST) & (M.tier == 1) & M.team.isin(f.team)].shape[0]),
                 "still_league": int(M[(M.season == LAST) & M.team.isin(f.team)].shape[0]),
                 "still_top_names": sorted(M[(M.season == LAST) & (M.tier == 1) & M.team.isin(f.team)].name.tolist())}
assert R["founders"]["north_west"] == 6 and R["founders"]["midlands"] == 6
lon = M[M.band == "London"]
lon_top = M[(M.tier == 1)].groupby("season").apply(lambda d: int((d.band == "London").sum()), include_groups=False)
R["london"] = {"first_season": season_label(int(lon.season.min())), "first_club": lon[lon.season == lon.season.min()].iloc[0]["name"],
               "first_top": season_label(int(M[(M.tier == 1) & (M.band == "London")].season.min())),
               "n_clubs_ever": int(lon.team.nunique()), "n_clubs_last": int((M[M.season == LAST].band == "London").sum()),
               "top_last": int(lon_top.loc[LAST]), "top_max": int(lon_top.max()),
               "top_max_seasons": [season_label(int(s)) for s in lon_top[lon_top == lon_top.max()].index],
               "top_1900": int(lon_top.loc[1900]), "top_1930": int(lon_top.loc[1930]),
               "crowd_share_1900": S.set_index("season").loc[1900, "crowd_share_London"],
               "crowd_share_1948": S.set_index("season").loc[1948, "crowd_share_London"],
               "crowd_share_last": S.set_index("season").loc[LAST, "crowd_share_London"]}

# ---- North/South by era ----
ERAS = [(1888, 1914, "1888 to 1915"), (1919, 1939, "1919 to 1939"), (1946, 1966, "1946 to 1967"), (1967, 1991, "1967 to 1992"),
        (1992, 2009, "1992 to 2010"), (2010, LAST, f"2010 to {LAST + 1}")]
eras = []
for a, b, lab in ERAS:
    d = M[(M.season >= a) & (M.season <= b)]
    t1 = d[d.tier == 1]
    e = {"label": lab, "from": a, "to": b, "top": {x: (t1.band == x).mean() for x in BANDS},
         "crowd": {x: d.loc[d.band == x, "crowd"].sum() / d.crowd.sum() for x in BANDS},
         "champs": {x: int(((ch.season >= a) & (ch.season <= b) & (ch.band == x)).sum()) for x in BANDS},
         "n_champs": int(((ch.season >= a) & (ch.season <= b)).sum())}
    # crowd-weighted centre of the top flight
    w = t1.home_avg.fillna(0)
    e["centre_lat"] = float((t1.lat * w).sum() / w.sum()) if w.sum() else None
    e["centre_lon"] = float((t1.lon * w).sum() / w.sum()) if w.sum() else None
    eras.append(e)
R["eras"] = eras
nb = lambda e: e["top"]["North"]
TW = jload(os.path.join(WORK, "towns.json"))
def nearest(lat, lon):
    return min(TW, key=lambda t: (t["lat"] - lat) ** 2 + ((t["lon"] - lon) * math.cos(math.radians(lat))) ** 2)["n"]
for e in eras:
    e["centre_near"] = nearest(e["centre_lat"], e["centre_lon"])
R["balance"] = {"north_top_first": eras[0]["top"]["North"], "north_top_last": eras[-1]["top"]["North"],
                "south_top_first": eras[0]["top"]["London"] + eras[0]["top"]["South (outside London)"],
                "south_top_last": eras[-1]["top"]["London"] + eras[-1]["top"]["South (outside London)"],
                "midlands_top_first": eras[0]["top"]["Midlands"], "midlands_top_last": eras[-1]["top"]["Midlands"],
                "north_crowd_first": eras[0]["crowd"]["North"], "north_crowd_last": eras[-1]["crowd"]["North"],
                "south_crowd_first": eras[0]["crowd"]["London"] + eras[0]["crowd"]["South (outside London)"],
                "south_crowd_last": eras[-1]["crowd"]["London"] + eras[-1]["crowd"]["South (outside London)"],
                "centre_shift_km": (eras[0]["centre_lat"] - eras[-1]["centre_lat"]) * 111.2}
# north share of top-flight places each season, smoothed for charts
R["balance"]["north_top_1888"] = S.set_index("season").loc[FIRST, "top_share_North"]
R["balance"]["north_top_last_season"] = S.set_index("season").loc[LAST, "top_share_North"]
R["balance"]["south_top_last_season"] = S.set_index("season").loc[LAST, "top_share_London"] + S.set_index("season").loc[LAST, "top_share_South (outside London)"]
R["balance"]["north_n_top_last"] = int((M[(M.season == LAST) & (M.tier == 1)].band == "North").sum())
R["balance"]["london_n_top_last"] = int((M[(M.season == LAST) & (M.tier == 1)].band == "London").sum())
R["balance"]["south_n_top_last"] = int((M[(M.season == LAST) & (M.tier == 1)].band == "South (outside London)").sum())
R["balance"]["mid_n_top_last"] = int((M[(M.season == LAST) & (M.tier == 1)].band == "Midlands").sum())

# ---- towns that lost league football ----
# "Today" is the 2025-26 league membership. The match data end with 2024-25, so the change from the 2024-25
# membership is applied explicitly: the two clubs promoted from the National League into League Two for
# 2025-26 and the two relegated from League Two at the end of 2024-25.
TODAY = "2025-26"
MEMBERSHIP_CHANGE = {
    "in": ["Barnet", "Oldham Athletic"],        # National League champions and play-off winners, 2024-25
    "out": ["Carlisle United", "Morecambe"],    # bottom two of League Two, 2024-25
}
clubs_last = set(M[M.season == LAST].team)
assert not (set(MEMBERSHIP_CHANGE["in"]) & clubs_last) and set(MEMBERSHIP_CHANGE["out"]) <= clubs_last
clubs_today = (clubs_last - set(MEMBERSHIP_CHANGE["out"])) | set(MEMBERSHIP_CHANGE["in"])
assert len(clubs_today) == 92
now_towns = {CK[t]["town"] for t in clubs_today}
lost = []
for town, d in M.groupby("town"):
    if town in now_towns:
        continue
    best = d.sort_values(["rank", "season"]).iloc[0]
    big = d.loc[d.home_avg.idxmax()] if d.home_avg.notna().any() else None
    lost.append({"town": town, "clubs": sorted(d.name.unique().tolist()), "first": int(d.season.min()), "last": int(d.season.max()),
                 "last_label": season_label(int(d.season.max())), "seasons": int(d.season.nunique()),
                 "best_rank": int(best["rank"]), "best_tier": int(best.tier), "best_pos": int(best.pos), "best_season": season_label(int(best.season)),
                 "top_seasons": int((d.tier == 1).sum()),
                 "peak_avg": None if big is None else float(big.home_avg), "peak_avg_season": None if big is None else season_label(int(big.season)),
                 "region": d.region.iloc[0], "lat": float(d.lat.mean()), "lon": float(d.lon.mean())})
lost.sort(key=lambda x: (-x["last"], x["town"]))
LT = pd.DataFrame(lost)
ever_top = LT[LT.top_seasons > 0].sort_values("top_seasons", ascending=False)
R["lost"] = {"n": len(lost), "n_towns_ever": R["data"]["n_towns"], "n_towns_last": len(now_towns), "today": TODAY,
             "membership_change": {k: [CK[t]["name"] for t in v] for k, v in MEMBERSHIP_CHANGE.items()},
             "n_top_flight": int((LT.top_seasons > 0).sum()), "top_flight": ever_top[["town", "top_seasons", "best_season", "best_pos"]].to_dict("records"),
             "before_1940": int((LT["last"] < 1939).sum()), "since_1960": int((LT["last"] >= 1960).sum()), "since_2000": int((LT["last"] >= 2000).sum()),
             "biggest_crowd": LT.sort_values("peak_avg", ascending=False).iloc[0][["town", "peak_avg", "peak_avg_season"]].to_dict(),
             "most_seasons": LT.sort_values("seasons", ascending=False).iloc[0][["town", "seasons", "last_label"]].to_dict(),
             "recent": LT[LT["last"] >= 2000][["town", "last_label"]].to_dict("records")}
LT.assign(clubs=LT.clubs.map(" / ".join)).to_csv(os.path.join(DATA, "lost_towns.csv"), index=False)
# Glossop: the smallest town ever in the top flight (one season, 1899-1900), checked here
assert "Glossop" in [x["town"] for x in R["lost"]["top_flight"]]
R["lost"]["glossop"] = next(x for x in lost if x["town"] == "Glossop")
# towns that came back: Barrow (1972 out, 2020 back), Chesterfield, Wrexham, Carlisle, Doncaster? computed: gaps of 10+ seasons
back = []
for t, d in M.groupby("team"):
    ss = sorted(d.season.unique())
    gaps = [(a, b) for a, b in zip(ss, ss[1:]) if b - a > 1 and not (a <= 1914 and b >= 1919) and not (a <= 1938 and b >= 1946)]
    for a, b in gaps:
        missed = (b - a - 1) - sum(1 for y in range(a + 1, b) if 1915 <= y <= 1918 or 1939 <= y <= 1945)
        if missed >= 10:
            back.append({"name": CK[t]["name"], "out": season_label(a), "back": season_label(b), "missed": missed})
R["comebacks"] = sorted(back, key=lambda x: -x["missed"])
assert any(x["name"] == "Barrow" for x in back)

# ---- each club's peak ----
peaks = []
for t, d in M.groupby("team"):
    d = d.sort_values("season")
    best = d.sort_values(["rank", "season"]).iloc[0]
    dec = d.groupby("decade").agg(n=("season", "size"), r=("rank", "mean"))
    dec = dec[dec.n >= 3] if (dec.n >= 3).any() else dec
    bd = int(dec.r.idxmin())
    big = d.loc[d.home_avg.idxmax()] if d.home_avg.notna().any() else None
    peaks.append({"key": t, "name": CK[t]["name"], "town": CK[t]["town"], "region": CK[t]["region"], "first": int(d.season.min()), "last": int(d.season.max()),
                  "seasons": int(d.season.nunique()), "top_seasons": int((d.tier == 1).sum()), "titles": int(((d.tier == 1) & (d.pos == 1)).sum()),
                  "best_rank": int(best["rank"]), "best_season": season_label(int(best.season)), "best_tier": int(best.tier), "best_pos": int(best.pos),
                  "best_decade": f"{bd}s", "best_decade_rank": float(dec.r.min()),
                  "peak_avg": None if big is None else float(big.home_avg), "peak_avg_season": None if big is None else season_label(int(big.season)),
                  "in_league_last": bool(d.season.max() == LAST), "tier_last": int(d[d.season == LAST].tier.iloc[0]) if d.season.max() == LAST else None})
P = pd.DataFrame(peaks)
P.drop(columns=["key"]).to_csv(os.path.join(DATA, "club_peaks.csv"), index=False)
pk = P[P.seasons >= 20].copy()
pk["dec"] = pk.best_decade.str[:4].astype(int)
R["peaks"] = {"by_decade": {f"{d}s": int(n) for d, n in pk.dec.value_counts().sort_index().items()}, "n_clubs_20": len(pk)}
for c in ("Huddersfield Town", "Preston North End", "Blackburn Rovers", "Sunderland", "Portsmouth", "Burnley", "Wolverhampton Wanderers", "Derby County",
          "Nottingham Forest", "Bolton Wanderers", "Notts County", "Sheffield Wednesday", "Manchester City", "Brighton & Hove Albion", "Brentford",
          "Bournemouth", "AFC Bournemouth", "Wigan Athletic", "Bury", "Newcastle United", "Aston Villa", "Arsenal", "Everton"):
    r = P[P.key == c]
    if len(r):
        R["peaks"][c] = r.iloc[0].drop("key").to_dict()
# the Bournemouth and Brighton kind of rise: best season in the last decade, at least 50 seasons in the league
recent_peak = P[(P.best_season.str[:4].astype(int) >= LAST - 9) & (P.seasons >= 50)].sort_values("best_rank")
R["peaks"]["recent_best"] = recent_peak[["name", "best_season", "best_pos", "best_tier", "seasons"]].to_dict("records")
early = P[(P.best_season.str[:4].astype(int) < 1939) & (P.seasons >= 50) & P.in_league_last].sort_values("best_rank")
R["peaks"]["early_best_still_league"] = early[["name", "best_season", "best_pos", "best_tier", "tier_last"]].to_dict("records")

# ---- biggest towns by top-flight seasons ----
tt = M[M.tier == 1].groupby("town").season.size().sort_values(ascending=False)
R["towns_top"] = [{"town": t, "n": int(n)} for t, n in tt.head(12).items()]
R["ever_present_top"] = sorted(CK[t]["name"] for t, d in M.groupby("team") if d.season.nunique() == len(seasons))
R["n_ever_present_league"] = len(R["ever_present_top"])

# ---- spotlight seasons for the page buttons ----
def season_brief(y):
    d = M[M.season == y]
    t1 = d[d.tier == 1].sort_values("pos")
    big = d.sort_values("home_avg", ascending=False).head(3)
    return {"season": season_label(y), "champion": t1.iloc[0]["name"], "clubs": len(d),
            "total": float(S.set_index("season").loc[y, "total"]) if y not in NO_GATES else None,
            "biggest": [{"name": r["name"], "avg": float(r.home_avg)} for _, r in big.iterrows()] if y not in NO_GATES else [],
            "north_top": int((t1.band == "North").sum()), "london_top": int((t1.band == "London").sum()), "n_top": len(t1)}
R["spot"] = {str(y): season_brief(y) for y in (1888, 1913, 1930, 1948, 1966, 1985, 1992, LAST)}

R["clubs_1923"] = int(S.set_index("season").loc[1923, "clubs"])
fo = M[M.team == "Nottingham Forest"].set_index("season")
R["forest"] = {"t_1976": int(fo.loc[1976, "tier"]), "pos_1976": int(fo.loc[1976, "pos"]), "pos_1977": int(fo.loc[1977, "pos"]), "t_1977": int(fo.loc[1977, "tier"])}
R["n_92_from"] = season_label(int(S[S.clubs >= 92].season.min()))
R["n_88"] = int(S.set_index("season").loc[1946, "clubs"])

# ---- write data files ----
cs = M[["season", "team", "name", "town", "county", "region", "nation", "tier", "division", "pos", "n_div", "rank", "n_league", "p", "w", "d", "l", "gf", "ga", "ded", "pts", "hp", "home_avg"]].copy()
cs.insert(1, "season_label", cs.season.map(season_label))
cs = cs.rename(columns={"team": "engsoccerdata_name", "pos": "position", "rank": "pyramid_rank", "n_league": "league_clubs", "p": "played", "w": "won",
                        "d": "drawn", "l": "lost", "gf": "goals_for", "ga": "goals_against", "ded": "points_deducted", "pts": "points",
                        "hp": "home_games", "home_avg": "avg_home_league_gate"})
cs["avg_home_league_gate"] = cs.avg_home_league_gate.round().astype("Int64")
cs.sort_values(["season", "pyramid_rank"]).to_csv(os.path.join(DATA, "club_seasons.csv"), index=False)
so = S.copy(); so.insert(1, "season_label", so.season.map(season_label))
so = so.rename(columns={"games": "matches", "total": "total_league_crowd", "avg": "avg_league_crowd", "top_avg": "top_flight_avg_gate"})
for c in so.columns:
    if c.startswith(("total", "avg", "top_flight")):
        so[c] = so[c].round()
    if "share" in c:
        so[c] = so[c].round(4)
so.drop(columns=["n_gate"]).to_csv(os.path.join(DATA, "seasons.csv"), index=False)

# page data: clubs list, per-season rows [club index, tier, pos, rank, avg or -1]
order = sorted(CL, key=lambda c: c["name"])
idx = {c["key"]: i for i, c in enumerate(order)}
site = {"clubs": [[c["name"], c["town"], c["lat"], c["lon"], c["region"], c["county"]] for c in order],
        "seasons": {}, "tot": [], "first": FIRST, "last": LAST, "no_gates": NO_GATES,
        "peaks": {idx[p["key"]]: [p["best_season"], p["best_tier"], p["best_pos"], p["best_decade"], p["peak_avg"], p["peak_avg_season"], p["titles"], p["top_seasons"], p["seasons"]] for p in peaks},
        "champ": {}}
for y, d in M.groupby("season"):
    d = d.sort_values("rank")
    site["seasons"][int(y)] = [[idx[r.team], int(r.tier), int(r.pos), int(r.rank), -1 if pd.isna(r.home_avg) else int(r.home_avg), r.division] for r in d.itertuples()]
for r in S.to_dict("records"):
    ok = not pd.isna(r["total"])
    site["tot"].append([int(r["season"]), int(r["total"]) if ok else None, int(r["avg"]) if ok else None,
                        int(r["top_avg"]) if ok else None, [round(r["top_share_" + b], 3) for b in BANDS],
                        [int(r[f"total_t{k}"]) if ok and not pd.isna(r[f"total_t{k}"]) else 0 for k in (1, 2, 3, 4)]])
site["peakList"] = [[p["name"], p["best_decade"]] for p in sorted(peaks, key=lambda p: p["name"]) if p["seasons"] >= 20]
site["bands"] = BANDS
site["lost"] = [[x["town"], x["lat"], x["lon"], x["last_label"], x["seasons"], x["best_tier"], x["best_pos"], x["best_season"], " / ".join(x["clubs"])] for x in lost]
jsave(site, os.path.join(DATA, "site.json"))
jsave(TW, os.path.join(DATA, "towns.json"))
jsave(R, os.path.join(DATA, "results.json"), indent=1)
print(json.dumps({k: R[k] for k in ("data", "crowds", "champions", "founders", "london", "balance")}, indent=1, default=str)[:6000])
print("lost towns", R["lost"]["n"], [x["town"] for x in lost][:60])
print("comebacks", R["comebacks"])
print("kings", runs)
print("recent best", R["peaks"]["recent_best"]); print("early best", R["peaks"]["early_best_still_league"][:12])
print("site.json", os.path.getsize(os.path.join(DATA, "site.json")) // 1024, "KB")
