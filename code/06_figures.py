"""Step 6. Static figures for the paper (release/paper/f_*.png), the blog (release/blog/b_*.png) and the
header map (WORK/header_map.png). All values from data/club_seasons.csv, data/seasons.csv, data/lost_towns.csv,
data/club_peaks.csv and data/results.json."""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import *  # noqa
import pandas as pd

R = jload(os.path.join(DATA, "results.json"))
CS = pd.read_csv(os.path.join(DATA, "club_seasons.csv"))
SS = pd.read_csv(os.path.join(DATA, "seasons.csv"))
LT = pd.read_csv(os.path.join(DATA, "lost_towns.csv"))
PK = pd.read_csv(os.path.join(DATA, "club_peaks.csv"))
CL = pd.read_csv(os.path.join(DATA, "clubs.csv")).set_index("engsoccerdata_name")
CS["lat"] = CS.engsoccerdata_name.map(CL.lat); CS["lon"] = CS.engsoccerdata_name.map(CL.lon)
PAP = os.path.join(ROOT, "release", "paper"); BLG = os.path.join(ROOT, "release", "blog")
os.makedirs(PAP, exist_ok=True); os.makedirs(BLG, exist_ok=True)
SHORT = {"Manchester United": "Man Utd", "Manchester City": "Man City", "Tottenham Hotspur": "Spurs", "Wolverhampton Wanderers": "Wolves",
         "West Bromwich Albion": "West Brom", "Newcastle United": "Newcastle", "Aston Villa": "Villa", "Preston North End": "Preston",
         "Blackburn Rovers": "Blackburn", "Bolton Wanderers": "Bolton", "Sheffield Wednesday": "Sheff Wed", "West Ham United": "West Ham",
         "Sunderland": "Sunderland", "Everton": "Everton", "Arsenal": "Arsenal", "Liverpool": "Liverpool", "Chelsea": "Chelsea"}


def season_map(ax, y, k=1.0, labels=0, title=True, fs=11):
    outline(ax)
    d = CS[CS.season == y].sort_values("avg_home_league_gate", ascending=False, na_position="last")
    x, yy = proj(d.lon.values, d.lat.values)
    ax.scatter(x, yy, s=rad(d.avg_home_league_gate.fillna(-1).values, k), c=[TC[t] for t in d.tier], alpha=.85, edgecolors="white", linewidths=.5, zorder=3)
    if title:
        lab = f"{y}-{str(y + 1)[-2:]}"
        tot = SS.set_index("season").loc[y, "total_league_crowd"]
        ax.text(0.02, 0.98, lab, transform=ax.transAxes, fontproperties=DISP, fontsize=fs * 2.0, va="top", color=FG)
        ax.text(0.02, 0.86, f"{len(d)} clubs\n{tot / 1e6:.1f}m crowds" if tot == tot else f"{len(d)} clubs", transform=ax.transAxes, fontsize=fs * .8, va="top", color=MUTED)
    return d


def fig_maps(path, years=(1888, 1913, 1948, 1985, 2024), w=15, h=5.4, dpi=200):
    fig, axs = plt.subplots(1, len(years), figsize=(w, h), facecolor=BG)
    fig.subplots_adjust(left=.01, right=.99, top=.98, bottom=.12, wspace=.02)
    for ax, y in zip(axs, years):
        season_map(ax, y, k=.55)
    hs = [plt.scatter([], [], s=60, c=TC[t], label=TIER[t][0]) for t in (1, 2, 3, 4)]
    hs += [plt.scatter([], [], s=rad([v], .55)[0], facecolors="none", edgecolors=MUTED, label=f"{v:,} crowd") for v in (5000, 20000, 50000)]
    fig.legend(handles=hs, loc="lower center", ncol=7, frameon=False, fontsize=10.5)
    save(fig, path, dpi)


fig_maps(f"{PAP}/f_maps.png"); shutil.copy(f"{PAP}/f_maps.png", f"{BLG}/b_maps.png")

# total crowds stacked by tier
def fig_crowds(path, w=10, h=4.6):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG); ax.set_facecolor(BG)
    s = SS.set_index("season")
    yrs = np.arange(1888, 2025)
    for a, b in ((1915, 1918), (1939, 1945)):
        ax.axvspan(a, b + 1, color=RULE, lw=0, zorder=0)
    seg = []
    for y in yrs:
        if y in s.index and s.loc[y, "total_league_crowd"] == s.loc[y, "total_league_crowd"]:
            seg.append(y)
        elif seg:
            draw_seg(ax, s, seg); seg = []
    if seg:
        draw_seg(ax, s, seg)
    c = R["crowds"]
    for yy, v, t, dy, ha in ((1948, c["peak_total"], f"{c['peak_total'] / 1e6:.1f}m, {c['peak_season']}", 1.6e6, "center"), (1985, c["low_total"], f"{c['low_total'] / 1e6:.1f}m, {c['low_season']}", -4.2e6, "center"),
                             (2024, c["last_total"], f"{c['last_total'] / 1e6:.1f}m", 1.6e6, "right")):
        ax.plot(yy + .5, v, "o", color=FG, ms=4.5, zorder=5)
        ax.text(yy + .5, v + dy, t, ha=ha, fontsize=10.5, color=FG, fontweight="medium", zorder=5)
    ax.set_xlim(1886, 2027); ax.set_ylim(0, 46e6)
    ax.set_yticks(np.arange(0, 46e6, 10e6)); ax.set_yticklabels([f"{v // 1000000:.0f}m" for v in np.arange(0, 46e6, 10e6)])
    ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
    hs = [plt.Rectangle((0, 0), 1, 1, fc=TC[t]) for t in (1, 2, 3, 4)] + [plt.Rectangle((0, 0), 1, 1, fc=RULE)]
    ax.legend(hs, [TIER[t][0] for t in (1, 2, 3, 4)] + ["War"], loc="upper left", frameon=False, fontsize=10, ncol=5)
    fig.tight_layout(); save(fig, path)


def draw_seg(ax, s, seg):
    x = np.array(seg) + .5; low = np.zeros(len(seg))
    for t in (1, 2, 3, 4):
        v = s.loc[seg, f"total_t{t}"].fillna(0).values
        ax.fill_between(x, low, low + v, color=TC[t], alpha=.85, lw=0, step=None); low = low + v
    ax.plot(x, s.loc[seg, "total_league_crowd"].values, color=FG, lw=1.2)


fig_crowds(f"{PAP}/f_crowds.png"); shutil.copy(f"{PAP}/f_crowds.png", f"{BLG}/b_crowds.png")

# top-flight places by area
def fig_balance(path, w=10, h=4.4):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG); ax.set_facecolor(BG)
    s = SS.set_index("season")
    for a, b in ((1888, 1914), (1919, 1938), (1946, 2024)):
        idx = [y for y in range(a, b + 1) if y in s.index]
        x = np.array(idx + [idx[-1] + 1]); low = np.zeros(len(x))
        for band in BANDS:
            v = s.loc[idx, "top_share_" + band].values; v = np.append(v, v[-1])
            ax.fill_between(x, low, low + v, step="post", color=BANDC[band], lw=0); low = low + v
    for a, b in ((1915, 1918), (1939, 1945)):
        ax.axvspan(a, b + 1, color=RULE, lw=0)
    ax.set_xlim(1888, 2025); ax.set_ylim(0, 1)
    ax.set_yticks([0, .25, .5, .75, 1]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    hs = [plt.Rectangle((0, 0), 1, 1, fc=BANDC[b]) for b in BANDS]
    ax.legend(hs, [BANDL[b] for b in BANDS], loc="upper center", bbox_to_anchor=(.5, -.08), frameon=False, fontsize=10, ncol=5)
    fig.tight_layout(); save(fig, path)


fig_balance(f"{PAP}/f_balance.png"); shutil.copy(f"{PAP}/f_balance.png", f"{BLG}/b_balance.png")

# best-supported club each season
KC = {"Manchester United": "#C8102E", "Arsenal": "#E5862B", "Everton": "#274488", "Chelsea": "#3A6FC4", "Newcastle United": "#222222",
      "Liverpool": "#3B8C4F", "Aston Villa": "#7A2650", "Tottenham Hotspur": "#8A8F99", "Manchester City": "#6CABDD"}


def fig_kings(path, w=10, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG); ax.set_facecolor(BG)
    top = CS[CS.avg_home_league_gate.notna()].sort_values("avg_home_league_gate", ascending=False).groupby("season").head(1)
    ax.bar(top.season + .5, top.avg_home_league_gate, width=.85, color=[KC.get(n, "#A8A196") for n in top.name])
    ax.set_xlim(1886, 2027); ax.set_ylim(0, 80000)
    ax.set_yticks(range(0, 80001, 20000)); ax.set_yticklabels([f"{v // 1000}k" for v in range(0, 80001, 20000)])
    ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
    used = [k for k in KC if k in set(top.name)]
    hs = [plt.Rectangle((0, 0), 1, 1, fc=KC[k]) for k in used] + [plt.Rectangle((0, 0), 1, 1, fc="#A8A196")]
    ax.legend(hs, used + ["Other"], loc="upper left", frameon=False, fontsize=9.5, ncol=3)
    fig.tight_layout(); save(fig, path)


fig_kings(f"{PAP}/f_kings.png"); shutil.copy(f"{PAP}/f_kings.png", f"{BLG}/b_kings.png")

# lost towns map
def fig_lost(path, w=8, h=9.2):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG)
    fig.subplots_adjust(0, 0, 1, 1)
    outline(ax)
    ch = R["lost"]["membership_change"]
    now = CS[(CS.season == CS.season.max()) & ~CS.name.isin(ch["out"])][["lat", "lon"]]
    now = pd.concat([now, CL[CL.name.isin(ch["in"])][["lat", "lon"]]])
    assert len(now) == 92
    x, y = proj(now.lon.values, now.lat.values)
    ax.scatter(x, y, s=10, c="#B9AE9C", zorder=2, lw=0)
    era = lambda l: "#9B1B30" if l < 1940 else ("#D9752B" if l < 2000 else "#2F5D8A")
    x, y = proj(LT.lon.values, LT.lat.values)
    ax.scatter(x, y, s=34, facecolors="none", edgecolors=[era(l) for l in LT["last"]], lw=1.8, zorder=4)
    placed = [(a - .03, b - .025, a + .03, b + .025) for a, b in zip(x, y)]
    for r in LT.sort_values("seasons", ascending=False).itertuples():
        px, py = proj(r.lon, r.lat)
        cw = .041
        cands = [(.06, 0, "left"), (-.06, 0, "right"), (0, .085, "center"), (0, -.085, "center"), (.07, .07, "left"), (-.07, -.07, "right"),
                 (.07, -.07, "left"), (-.07, .07, "right"), (.16, .12, "left"), (-.16, -.12, "right"), (.16, -.14, "left"), (-.16, .14, "right"), (0, .18, "center"), (0, -.18, "center"), (.25, .2, "left"), (-.25, .2, "right"), (.25, -.22, "left"), (-.25, -.22, "right")]
        for dx, dy, ha in cands:
            wd = cw * len(r.town)
            x0 = px + dx if ha == "left" else (px + dx - wd if ha == "right" else px + dx - wd / 2)
            box = (x0, py + dy - .035, x0 + wd, py + dy + .035)
            if not any(box[0] < b[2] and box[2] > b[0] and box[1] < b[3] and box[3] > b[1] for b in placed):
                placed.append(box)
                ax.text(px + dx, py + dy, r.town, ha=ha, va="center", fontsize=7.5, color=FG, zorder=5,
                        path_effects=[matplotlib.patheffects.withStroke(linewidth=2.2, foreground=BG)])
                break
        else:
            print("lost map: no room for", r.town)
    hs = [plt.scatter([], [], s=40, facecolors="none", edgecolors=c, lw=1.8, label=l) for c, l in
          (("#9B1B30", "Lost before 1940"), ("#D9752B", "Lost 1940 to 1999"), ("#2F5D8A", "Lost since 2000"))]
    hs.append(plt.scatter([], [], s=12, c="#B9AE9C", label=f"League club, {R['lost']['today']}"))
    ax.legend(handles=hs, loc="lower right", frameon=False, fontsize=9)
    save(fig, path)


import matplotlib.patheffects  # noqa
fig_lost(f"{PAP}/f_lost.png"); shutil.copy(f"{PAP}/f_lost.png", f"{BLG}/b_lost.png")

# best decades
def fig_peaks(path, w=10, h=3.8):
    fig, ax = plt.subplots(figsize=(w, h), facecolor=BG); ax.set_facecolor(BG)
    bd = R["peaks"]["by_decade"]
    ax.bar(range(len(bd)), list(bd.values()), color=HOT, width=.72)
    for i, v in enumerate(bd.values()):
        ax.text(i, v + .2, str(v), ha="center", fontsize=10)
    ax.set_xticks(range(len(bd))); ax.set_xticklabels(list(bd.keys()), fontsize=10)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    fig.tight_layout(); save(fig, path)


fig_peaks(f"{PAP}/f_peaks.png"); shutil.copy(f"{PAP}/f_peaks.png", f"{BLG}/b_peaks.png")

# header map: 1948-49, no title
fig, ax = plt.subplots(figsize=(5.2, 6.5), facecolor=BG); fig.subplots_adjust(0, 0, 1, 1)
season_map(ax, 1948, k=1.0, title=False)
save(fig, os.path.join(WORK, "header_map.png"), dpi=130)
print("figures done")
