# -*- coding: utf-8 -*-
"""Recorre los 21 productos: monta el 3D, activa cada punto y saca una foto."""
from playwright.sync_api import sync_playwright
import pathlib, os, json, re

ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
SHOT = ROOT / "_shots3d"; SHOT.mkdir(exist_ok=True)
BASE = os.environ.get("QA_BASE", "http://localhost:8899")

js = (ROOT / "js" / "productos.js").read_text(encoding="utf-8")
orden = json.loads(re.search(r"window\.ORDEN = (\[.*?\]);", js, re.S).group(1))

fallos = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    for slug in orden:
        del errs[:]
        pg.goto(BASE + "/producto.html?p=" + slug, wait_until="load")
        pg.wait_for_timeout(3800)
        hay = pg.evaluate("!!document.querySelector('#stage3d canvas')")
        n = pg.evaluate("document.querySelectorAll('.hs-item').length")
        nombre = pg.evaluate("document.getElementById('h-nombre').textContent")
        modelo = pg.evaluate("(window.PRODUCTOS||{})['%s'] ? window.PRODUCTOS['%s'].modelo3d : '?'" % (slug, slug))
        estado = "OK " if (hay and n) else "FALLA"
        if not (hay and n) or errs:
            fallos.append((slug, hay, n, errs[:1]))
        print("%-5s %-26s %-8s puntos=%s %s" % (estado, slug, modelo, n, (errs[:1] or "")))
        caja = pg.locator("#stage3d").bounding_box()
        clip = {"x": caja["x"], "y": caja["y"], "width": caja["width"], "height": caja["height"]}
        pg.screenshot(path=str(SHOT / ("p_%s_0.png" % slug)), clip=clip)
        if n:
            pg.click(".hs-item[data-i='1']"); pg.wait_for_timeout(1500)
            pg.screenshot(path=str(SHOT / ("p_%s_1.png" % slug)), clip=clip)
            pg.click(".hs-item[data-i='%d']" % (n - 1)); pg.wait_for_timeout(1500)
            pg.screenshot(path=str(SHOT / ("p_%s_2.png" % slug)), clip=clip)
    b.close()
print("\nFALLOS:", fallos if fallos else "ninguno")
