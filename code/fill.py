"""Placeholder filling shared by the page, README, paper, blog and collage.

{{path.to.value|fmt}} reads data/results.json; names in X are derived values computed here from the same file.
Formats: int, pct0, pct1, f0, f1, m1 (millions, one decimal), raw. Tokens written [[DOI]], [[DOI_URL]] and
[[BLOG_URL]] become {{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/who-was-big-when/ for the publisher to fill.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa

R = jload(os.path.join(DATA, "results.json"))
C = R["crowds"]
X = {
    "x_peak_m": f"{C['peak_total'] / 1e6:.1f}", "x_low_m": f"{C['low_total'] / 1e6:.1f}", "x_last_m": f"{C['last_total'] / 1e6:.1f}",
    "x_first_k": f"{C['first_total'] / 1e3:,.0f}", "x_pl1_m": f"{C['pl1_total'] / 1e6:.1f}",
    "x_fall_pct": f"{C['fall_pct'] * 100:.0f}%", "x_last_vs_peak": f"{C['last_vs_peak'] * 100:.0f}%",
    "x_prewar_m": f"{C['pre1915_peak_total'] / 1e6:.1f}", "x_inter_m": f"{C['inter_peak_total'] / 1e6:.1f}",
    "x_top_growth": f"{C['top_avg_growth_pl']:.1f}",
    "x_lower_last_m": f"{C['lower_last'] / 1e6:.1f}", "x_lower_peak_m": f"{C['lower_peak'] / 1e6:.1f}",
    "x_centre_km": f"{R['balance']['centre_shift_km']:.0f}",
    "x_mu_kings": str(R["crowd_kings"]["man_utd"]),
}


def get(path):
    if path in X:
        return X[path]
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f, tex=False):
    if isinstance(v, str) and f in ("", "raw"):
        s = v
    elif f == "int": s = f"{int(round(float(v))):,}"
    elif f == "pct0": s = f"{v * 100:.0f}%"
    elif f == "pct1": s = f"{v * 100:.1f}%"
    elif f == "f0": s = f"{v:.0f}"
    elif f == "f1": s = f"{v:.1f}"
    elif f == "m1": s = f"{v / 1e6:.1f} million"
    else: s = str(v)
    if tex:
        s = s.replace("%", "\\%").replace("&", "\\&").replace("<", "$<$")
    return s


def fill(t, tex=False):
    def sub(m):
        path, _, f = m.group(1).partition("|")
        if path.strip() in ("DOI", "BLOG_URL", "DOI_URL") or path.startswith("IMG"):
            return m.group(0)
        return fmt(get(path.strip()), f.strip(), tex)
    t = re.sub(r"\{\{(.+?)\}\}", sub, t)
    return t.replace("[[DOI]]", "{{DOI}}").replace("[[BLOG_URL]]", "https://blog.tristanhotham.com/2026/10/31/who-was-big-when/").replace("[[DOI_URL]]", "{{DOI_URL}}")


def check_visible(text, where):
    vis = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", text, flags=re.S)
    vis = re.sub(r'style="[^"]*"', "", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, (where, bad, vis[max(0, vis.find(bad) - 80): vis.find(bad) + 80])
