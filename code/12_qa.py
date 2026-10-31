"""QA: open index.html with Playwright at 1280 px and 390 px (light and dark), record console errors and take
screenshots into ../qa/. Tile and font requests fail in the build container (no internet), so those
network errors are ignored."""
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from playwright.sync_api import sync_playwright

LEAF = "/tmp/claude-0/-home-claude/9791f396-0812-550b-8fd1-2ad33918f115/scratchpad/node_modules/leaflet/dist"   # npm leaflet@1.9.4 (cdnjs is blocked here)
QA = os.path.join(ROOT, "qa"); os.makedirs(QA, exist_ok=True)
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8766", "--bind", "127.0.0.1"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
errs = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, vw, vh, scheme in (("desktop", 1280, 900, "light"), ("phone", 390, 844, "light"), ("phone_dark", 390, 844, "dark")):
            ctx = b.new_context(viewport={"width": vw, "height": vh}, color_scheme=scheme, device_scale_factor=1 if vw > 500 else 2)
            pg = ctx.new_page()
            pg.route("**/*arcgisonline*/**", lambda r: r.abort()); pg.route("**/fonts.g*/**", lambda r: r.abort())
            pg.route("**/leaflet.min.js", lambda r: r.fulfill(path=f"{LEAF}/leaflet.js"))
            pg.route("**/leaflet.min.css", lambda r: r.fulfill(path=f"{LEAF}/leaflet.css"))
            pg.on("console", lambda m, n=name: errs.append((n, m.type, m.text)) if m.type in ("error", "warning") and "Failed to load resource" not in m.text else None)
            pg.on("pageerror", lambda e, n=name: errs.append((n, "pageerror", str(e))))
            pg.goto("http://127.0.0.1:8766/index.html", wait_until="domcontentloaded")
            pg.wait_for_timeout(2500)
            pg.screenshot(path=f"{QA}/{name}_top.png")
            pg.locator("#atlas").scroll_into_view_if_needed(); pg.wait_for_timeout(500)
            pg.screenshot(path=f"{QA}/{name}_map_1888.png")
            pg.evaluate("setYear(1948)"); pg.wait_for_timeout(500)
            pg.screenshot(path=f"{QA}/{name}_map_1948.png")
            pg.evaluate("setYear(2024)"); pg.wait_for_timeout(500)
            pg.screenshot(path=f"{QA}/{name}_map_2024.png")
            if name == "desktop":
                pg.fill("#q", "Bury"); pg.wait_for_timeout(300); pg.screenshot(path=f"{QA}/{name}_search.png")
                pg.keyboard.press("Enter"); pg.wait_for_timeout(800); pg.screenshot(path=f"{QA}/{name}_club.png")
                pg.click(".lyrBtn"); pg.wait_for_timeout(300); pg.screenshot(path=f"{QA}/{name}_layers.png"); pg.click(".lyrBtn")
                pg.click("#colRow .btn[data-c=rank]"); pg.wait_for_timeout(300); pg.screenshot(path=f"{QA}/{name}_rank.png")
                pg.click("#play"); pg.wait_for_timeout(1500); pg.click("#play")
            # full screen button
            pg.locator("#atlas").scroll_into_view_if_needed()
            btn = pg.locator(".mfs-btn").first
            assert btn.count() == 1, "no fullscreen button"
            btn.click(); pg.wait_for_timeout(700); pg.screenshot(path=f"{QA}/{name}_fullscreen.png"); btn.click(); pg.wait_for_timeout(300)
            for sec in ("crowdChart", "balChart", "eraChart", "kingChart", "peakChart", "lostTable"):
                pg.locator("#" + sec).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
                pg.screenshot(path=f"{QA}/{name}_{sec}.png")
            sw = pg.evaluate("document.documentElement.scrollWidth")
            assert sw <= vw + 1, (name, "horizontal scroll", sw)
            ctx.close()
        b.close()
finally:
    srv.terminate()
print("console problems:", errs if errs else "none")
