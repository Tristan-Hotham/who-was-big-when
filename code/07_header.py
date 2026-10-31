"""Step 7. Render ../header.png (1200 x 630 social card) with Playwright Chromium, using the 1948-49 map
from 06_figures.py."""
import sys, os, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill import *  # noqa
from playwright.sync_api import sync_playwright

img = base64.b64encode(open(os.path.join(WORK, "header_map.png"), "rb").read()).decode()
FD = FONT_DIR
ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
    ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
    ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")])
html = fill(f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:{BG};color:{FG};overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:64px;top:62px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:{MUTED};display:flex;gap:12px;align-items:center}}
.k b{{background:{HOT};color:#fff;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:104px;margin:0;font:900 104px/.9 Fraunces,Georgia,serif;letter-spacing:-.02em;width:700px}}
.a{{color:{HOT}}} .b{{color:#D9752B}}
p{{position:absolute;left:64px;top:330px;width:600px;margin:0;font-size:25px;line-height:1.36}}
.f{{position:absolute;left:64px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:{MUTED}}}
.lg{{position:absolute;left:64px;bottom:84px;font:400 15px/1 'IBM Plex Mono',monospace;color:{MUTED};display:flex;gap:16px}}
.lg i{{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:6px}}
.m{{position:absolute;left:700px;top:-6px;height:642px}} .y{{position:absolute;right:40px;bottom:36px;font:900 40px/1 Fraunces,serif;color:{FG};opacity:.85}}
</style></head><body>
<div class="k"><b>Data study</b><span>Football</span></div>
<h1>Who was <span class="a">big</span> <span class="b">when?</span></h1>
<p>Every Football League and Premier League club, {{{{data.first|raw}}}} to {{{{data.last|raw}}}}: where they played, how big their crowds were and where they finished.</p>
<div class="lg">{"".join(f'<span><i style="background:{TIER[t][1]}"></i>{TIER[t][0]}</span>' for t in (1, 2, 3))}</div>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<img class="m" src="data:image/png;base64,{img}"><div class="y">{{{{crowds.peak_season|raw}}}}</div>
</body></html>""")
tmp = os.path.join(WORK, "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + tmp); pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
print("header.png written")
