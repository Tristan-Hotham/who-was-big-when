"""Reddit collage (r/dataisbeautiful style, light background): five season maps, total crowds, top-flight places
by area and the lost towns count. Every number from data/results.json and the data files.
Run: python3 reddit/collage.py  ->  reddit/who_was_big_when.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
from figstyle import *  # noqa
import pandas as pd
import matplotlib.gridspec as gs
import matplotlib.patheffects  # noqa

R = jload(os.path.join(DATA, "results.json"))
CS = pd.read_csv(os.path.join(DATA, "club_seasons.csv"))
SS = pd.read_csv(os.path.join(DATA, "seasons.csv")).set_index("season")
CL = pd.read_csv(os.path.join(DATA, "clubs.csv")).set_index("engsoccerdata_name")
CS["lat"] = CS.engsoccerdata_name.map(CL.lat); CS["lon"] = CS.engsoccerdata_name.map(CL.lon)
C = R["crowds"]
YEARS = [1888, 1913, 1948, 1985, 2024]

fig = plt.figure(figsize=(16, 18), facecolor=BG)
G = gs.GridSpec(4, 5, figure=fig, height_ratios=[.07, .9, .62, .5], left=.04, right=.97, top=.865, bottom=.075, hspace=.3, wspace=.03)
fig.text(.04, .955, "Who was big when?", fontproperties=DISP, fontsize=64, color=FG, va="center")
fig.text(.04, .915, f"Every Football League and Premier League club, {R['data']['first']} to {R['data']['last']}, sized by its average home crowd.", fontproperties=SERP, fontsize=22, color=FG, va="center")
fig.text(.04, .888, f"League crowds peaked at {C['peak_total'] / 1e6:.1f} million in {C['peak_season']}, fell {C['fall_pct'] * 100:.0f}% by {C['low_season']} and are back to {C['last_total'] / 1e6:.1f} million.",
         fontproperties=SERP, fontsize=18, color=MUTED, va="center")

for i, y in enumerate(YEARS):
    ax = fig.add_subplot(G[1, i])
    outline(ax)
    d = CS[CS.season == y].sort_values("avg_home_league_gate", ascending=False)
    x, yy = proj(d.lon.values, d.lat.values)
    ax.scatter(x, yy, s=rad(d.avg_home_league_gate.fillna(-1).values, .6), c=[TIER[t][1] for t in d.tier], alpha=.85, edgecolors="white", linewidths=.5, zorder=3)
    tot = SS.loc[y, "total_league_crowd"]
    # labels above the map, on plain paper
    ax.set_title(f"{y}-{str(y + 1)[-2:]}", fontproperties=DISP, fontsize=27, color=FG, loc="left", pad=34)
    ax.text(0, 1.015, f"{len(d)} clubs · {tot / 1e6:.1f}m", transform=ax.transAxes, fontsize=13, color=MUTED, va="bottom")
lax = fig.add_subplot(G[0, :]); lax.axis("off")
hs = [plt.scatter([], [], s=150, c=TIER[t][1], label=TIER[t][0]) for t in (1, 2, 3, 4)]
hs += [plt.scatter([], [], s=rad([v], .6)[0], facecolors="none", edgecolors=MUTED, label=f"{v:,} home crowd") for v in (5000, 25000, 60000)] + [plt.scatter([], [], s=0, label="(circle area)")]
lax.legend(handles=hs, loc="center", ncol=4, frameon=False, fontsize=14, handletextpad=.3, columnspacing=2.2)

# total crowds
SUB = G[2, :].subgridspec(1, 3, width_ratios=[3, .55, 2], wspace=0)
ax = fig.add_subplot(SUB[0, 0]); ax.set_facecolor(BG)
for a, b in ((1915, 1918), (1939, 1945)):
    ax.axvspan(a, b + 1, color=RULE, lw=0)
segs, cur = [], []
for y in range(1888, 2025):
    ok = y in SS.index and SS.loc[y, "total_league_crowd"] == SS.loc[y, "total_league_crowd"]
    if ok: cur.append(y)
    elif cur: segs.append(cur); cur = []
segs.append(cur)
for sg in segs:
    xx = np.array(sg) + .5; low = np.zeros(len(sg))
    for t in (1, 2, 3, 4):
        v = SS.loc[sg, f"total_t{t}"].fillna(0).values
        ax.fill_between(xx, low, low + v, color=TIER[t][1], alpha=.85, lw=0); low = low + v
    ax.plot(xx, SS.loc[sg, "total_league_crowd"], color=FG, lw=1.4)
for y, v, t, dy, ha in ((1948, C["peak_total"], f"{C['peak_total'] / 1e6:.1f}m in {C['peak_season']}", 2.2e6, "center"), (1985, C["low_total"], f"{C['low_total'] / 1e6:.1f}m in {C['low_season']}", -5.2e6, "center"),
                        (2024, C["last_total"], f"{C['last_total'] / 1e6:.1f}m", 2.2e6, "right")):
    ax.plot(y + .5, v, "o", color=FG, ms=6, zorder=5)
    box = dict(boxstyle="round,pad=.25", fc=BG, ec="none", alpha=.92) if y == 1985 else None
    ax.text(y + .5, v + dy, t, ha=ha, fontsize=14, color=FG, fontweight="medium", zorder=6, bbox=box,
            path_effects=None if box else [matplotlib.patheffects.withStroke(linewidth=3, foreground=BG)])
ax.set_xlim(1886, 2027); ax.set_ylim(0, 48e6)
ax.set_yticks(np.arange(0, 46e6, 10e6)); ax.set_yticklabels([f"{v / 1e6:.0f}m" for v in np.arange(0, 46e6, 10e6)], fontsize=12)
ax.tick_params(axis="x", labelsize=12); ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
ax.set_title("Total league crowd each season, by division", loc="left", fontproperties=SEMI, fontsize=19, color=FG, pad=10)

# area shares of top-flight places by era
ax = fig.add_subplot(SUB[0, 2]); ax.set_facecolor(BG)
eras = R["eras"]
for i, e in enumerate(eras):
    left = 0
    for b in BANDS:
        v = e["top"][b]
        ax.barh(len(eras) - 1 - i, v, left=left, color=BANDC[b], height=.72)
        if v > .08:
            ax.text(left + v / 2, len(eras) - 1 - i, f"{v * 100:.0f}%", ha="center", va="center", color="white", fontsize=11.5, fontweight="medium")
        left += v
ax.set_yticks(range(len(eras))); ax.set_yticklabels([e["label"] for e in eras][::-1], fontsize=12.5)
ax.set_xlim(0, 1); ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.set_title("Who holds the top-flight places", loc="left", fontproperties=SEMI, fontsize=19, color=FG, pad=10)
hs = [plt.Rectangle((0, 0), 1, 1, fc=BANDC[b]) for b in BANDS]
ax.legend(hs, [BANDL[b] for b in BANDS], loc="upper center", bbox_to_anchor=(.45, -.02), ncol=3, frameon=False, fontsize=11.5)

# fact cards
B, CH, LO = R["balance"], R["champions"], R["lost"]
facts = [(f"{LO['n']}", "towns that once had a league\nclub and have none in 2025-26\n(Bury, Carlisle, Darwen,\nMerthyr Tydfil...)", HOT),
         (f"{B['london_n_top_last']} to {B['north_n_top_last']}", f"London clubs to Northern clubs\nin the {C['last_season']} Premier\nLeague. In 1888-89: 0 to {R['founders']['north_west']}.", COOL),
         (f"{CH['by_band']['North']} of {CH['n']}", f"titles won by Northern clubs;\nsince 2000-01, {CH['north_since_2000']} of {CH['n_since_2000']}, all\nManchester or Liverpool", TIER[1][1]),
         (f"{R['crowd_kings']['man_utd']}", f"seasons with Manchester United\nthe best-supported club, every\none since {R['crowd_kings']['man_utd_since']}", TIER[2][1])]
for i, (big, txt, col) in enumerate(facts):
    x0 = .04 + i * .238
    fig.text(x0, .195, big, fontproperties=DISP, fontsize=44, color=col, va="center")
    fig.text(x0, .158, txt, fontsize=13, color=FG, va="top", linespacing=1.45)
fig.add_artist(plt.Line2D([.04, .97], [.068, .068], color=FG, lw=1.2))
fig.text(.04, .052, "Data: match results, engsoccerdata (J. P. Curley) and openfootball; average home league gates, englishfootballleaguetables.co.uk; ONS boundaries.", fontsize=11.5, color=MUTED, va="center")
fig.text(.04, .036, "Circles at each club's present or last ground. Crowd = average home league gate x home league games; early figures are estimates; no crowd data 2020-22.", fontsize=11.5, color=MUTED, va="center")
fig.text(.04, .016, "Dr Tristan Hotham · Independent researcher", fontsize=12, color=MUTED, va="center")
fig.text(.97, .016, "maps.tristanhotham.com/who-was-big-when", fontsize=15, color=FG, ha="right", va="center", fontweight="medium")
import matplotlib.patheffects  # noqa
out = os.path.join(ROOT, "reddit", "who_was_big_when.png")
fig.savefig(out, dpi=150, facecolor=BG); plt.close(fig)
print(out)
