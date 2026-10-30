"""Render the link-preview image (1200x630) from share.html.
Usage: python3 make_share.py <repo>   → writes <repo>/assets/share.png"""
import sys, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]).resolve() / "assets" / "share.png"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__("os").environ.get("CAPMAP_CHROME"), channel="chromium")
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    pg.goto((HERE / "share.html").as_uri()); pg.wait_for_timeout(400)
    pg.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
    b.close()
print("wrote", OUT)
