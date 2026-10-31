"""Step 10. Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo)."""
import sys, os, zipfile, json as _json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa

REL = os.path.join(ROOT, "release"); NAME = "Hotham_Who_Was_Big_When"
C = R["crowds"]
# claims in words in the blog (alt text included), checked
assert R["founders"]["still_top_names"] == ["Aston Villa", "Everton", "Wolverhampton Wanderers"]
assert sorted(R["founders"]["names"]) == sorted(["Preston North End", "Accrington", "Blackburn Rovers", "Bolton Wanderers", "Burnley", "Everton",
                                                 "Aston Villa", "Derby County", "Notts County", "Stoke City", "West Bromwich Albion", "Wolverhampton Wanderers"])
assert R["crowd_kings"]["first"]["name"] == "Everton"
assert round(C["pre1915_peak_total"] / 1e6, 1) == 12.4 and 27e6 < C["inter_peak_total"] < 29e6 and round(C["peak_total"] / 1e6, 1) == 41.2
assert round(C["low_total"] / 1e6, 1) == 16.5 and round(C["last_total"] / 1e6, 1) == 36.4 and round(R["crowd_kings"]["biggest"]["avg"] / 1000) == 76
assert R["lost"]["n"] == 39 and R["lost"]["today"] == "2025-26"
assert R["comebacks"][0]["name"] == "Barrow" and R["comebacks"][0]["missed"] == 48
bd = R["peaks"]["by_decade"]; mx = max(bd.values()); mn = min(bd.values())
assert {d for d, v in bd.items() if v == mx} == {"1890s", "1940s", "2020s"} and {d for d, v in bd.items() if v == mn} == {"1960s", "2010s"}
assert R["peaks"]["Huddersfield Town"]["best_decade"] == "1920s" and R["peaks"]["Portsmouth"]["best_decade"] == "1940s"
P = {p["name"]: p for p in R["peaks"]["recent_best"]}
assert int(P["Brighton & Hove Albion"]["best_season"][:4]) >= 2015 and int(P["AFC Bournemouth"]["best_season"][:4]) >= 2015
post = fill(open(os.path.join(HERE := os.path.dirname(os.path.abspath(__file__)), "blog_template.html"), encoding="utf-8").read())
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
check_visible(post, "post")
assert "{{" not in re.sub(r"\{\{(IMG\|[^}]*|DOI_URL)\}\}", "", post)
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
meta = {"title": "Who was big when? 126 seasons of English league football on one map",
        "slug": SLUG,
        "excerpt": f"Every English league club since 1888 on one map, sized by its crowd: {C['peak_total'] / 1e6:.1f} million at league matches in {C['peak_season']}, {C['low_total'] / 1e6:.1f} million in {C['low_season']}, a game that moved south, and {R['lost']['n']} towns that lost their league club.",
        "seo_description": f"Every English league club since 1888 mapped by league position and crowd: the {C['peak_season']} peak, the 1980s low, the move south and {R['lost']['n']} lost towns.",
        "tags": ["football", "Football League", "Premier League", "attendance", "history", "maps", "data visualisation", "England", "Wales"],
        "header_alt": "Title card reading 'Who was big when?' in black, claret and orange on cream, beside a map of England and Wales in 1948-49 with a circle for every league club sized by its home crowd and coloured by division, biggest in the North West, Newcastle, the Midlands and London."}
assert str(R["data"]["n_seasons"]) in meta["title"]
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst): os.remove(dst)
    os.link(src, dst)


link(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_code_and_data.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__": continue
            z.write(os.path.join(ROOT, d, fn), f"{SLUG}/{d}/{fn}")
    for fn in ("README.md", "LICENSE", "index.html", "header.png"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("``", "\u201c").replace("''", "\u201d").replace("$<$", "<").replace("\\&", "&")
zmeta = {"title": f"Who Was Big When? League Position and Crowds of Every English League Club, {R['data']['first']} to {R['data']['last']}",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: {PAGE}. Data and code: {REPO}. Match results from engsoccerdata (James P. Curley) and openfootball; average league gates derived from englishfootballleaguetables.co.uk and credited to it.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["football", "Football League", "Premier League", "attendance", "crowds", "sports history", "North and South", "England", "Wales", "maps"],
         "license": "cc-by-4.0", "access_right": "open", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://doi.org/10.5281/zenodo.13158", "relation": "isDerivedFrom", "resource_type": "software"},
                                 {"identifier": "https://github.com/openfootball/england", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.englishfootballleaguetables.co.uk/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", re.sub(r"<!--.*?-->", "", post, flags=re.S)).split())
print("blog words", words, "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
