"""Step 8. Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_Who_Was_Big_When.tex and .pdf (figures f_*.png from 06_figures.py)."""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa
import pandas as pd

OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Who_Was_Big_When"
# claims in words
assert R["champions"]["by_band"]["Wales"] == 0 and len(R["comebacks"]) == 5 and R["n_88"] == 88
assert {x["name"] for x in R["peaks"]["recent_best"]} >= {"Brighton & Hove Albion", "AFC Bournemouth"}
assert [x["town"] for x in R["lost"]["top_flight"]] == ["Bury", "Darwen", "Carlisle", "Glossop"]
SS = pd.read_csv(os.path.join(DATA, "seasons.csv")).set_index("season")
rows = ""
for y, what in ((1888, "First season"), (1913, "Last before the First World War"), (1937, "Inter-war peak"), (1948, "All-time peak"),
                (1966, "England's World Cup season"), (1985, "Low point"), (1992, "First Premier League season"), (2024, "Latest complete season")):
    r = SS.loc[y]
    rows += f"{r.season_label} & {what} & {int(r.clubs)} & {r.total_league_crowd / 1e6:.1f} & {int(r.avg_league_crowd):,} & {int(r.top_flight_avg_gate):,}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Crowd milestones. Total: millions at league matches; averages per match.}\\label{tab:crowds}"
      "\\begin{tabular}{llrrrr}\\toprule Season & & Clubs & Total (m) & Average & Top flight\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for e in R["eras"]:
    t = e["top"]; c = e["crowd"]; ch = e["champs"]
    f = lambda d, b: f"{d[b] * 100:.0f}"
    rows += f"{e['label']} & " + " & ".join(f(t, b) for b in BANDS) + " & " + " & ".join(f(c, b) for b in BANDS[:4]) + f" & {ch['North']}/{ch['Midlands']}/{ch['London']}/{ch['South (outside London)']}\\\\\n"
TE = ("\\begin{table}[tbp]\\centering\\footnotesize\\setlength{\\tabcolsep}{3.5pt}\\caption{Area shares by era, per cent: top-flight places (N North, M Midlands, L London, S rest of the South, W Wales), all league crowds, and titles (North/Midlands/London/South).}\\label{tab:eras}"
      "\\begin{tabular}{lrrrrrrrrrr}\\toprule & \\multicolumn{5}{c}{Top-flight places} & \\multicolumn{4}{c}{Crowds} & Titles\\\\ Era & N & M & L & S & W & N & M & L & S & N/M/L/S\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
LT = pd.read_csv(os.path.join(DATA, "lost_towns.csv"))
TN = {1: "top", 2: "2nd", 3: "3rd", 4: "4th"}
rows = ""
for r in LT.itertuples():
    rows += f"{r.town} & {r.clubs.replace('&', chr(92) + '&')} & {r.seasons} & {r.last_label} & {r.best_pos}, {TN[r.best_tier]} tier ({r.best_season})\\\\\n"
TL = ("\\begin{table}[tbp]\\centering\\scriptsize\\caption{The " + str(len(LT)) + " towns that had a league club and have none in " + R["lost"]["today"] + ", most recent first. Best: highest finish.}\\label{tab:lost}"
      "\\begin{tabular}{llrll}\\toprule Town & Club(s) & Seasons & Last & Best\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("{{TABLE_CROWDS}}", TC).replace("{{TABLE_ERAS}}", TE).replace("{{TABLE_LOST}}", TL)
t = re.sub(r"\\url\{\{\{(meta\.\w+)\|raw\}\}\}", lambda m: "\\url{" + get(m.group(1)) + "}", t)
t = fill(t, tex=True)
assert "[[" not in t and "\u2014" not in t and "\u2013" not in t and "--" not in t.replace("{{DOI}}", "")
assert re.findall(r"\{\{(?!DOI)", t) == [], re.findall(r"\{\{.{0,30}", t)[:5]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013"))
