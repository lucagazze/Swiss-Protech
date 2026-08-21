# -*- coding: utf-8 -*-
"""El producto tiene que quedar centrado en los 3 contextos, y el zoom tiene que acercarlo."""
from playwright.sync_api import sync_playwright
import pathlib, os
ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
SHOT = ROOT / "_shots3d"; SHOT.mkdir(exist_ok=True)
BASE = os.environ.get("QA_BASE", "http://localhost:8899")
PRODS = ["mobilelink-dual-mobility", "lubinus-spii", "optetrak-logic"]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:150]))
    for prod in PRODS:
        pg.goto(BASE + "/producto.html?p=" + prod, wait_until="load")
        pg.wait_for_timeout(3800)
        st = pg.locator("#stage3d"); st.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
        def foto(n):
            st.screenshot(path=str(SHOT / ("ctx_%s_%s.png" % (prod, n))))
        for k, sel in (("solo", "#v-solo"), ("hueso", "#v-anatomia"), ("cuerpo", "#v-cuerpo")):
            if pg.locator(sel).count() == 0:
                print("%-28s %-7s sin boton" % (prod, k)); continue
            pg.click(sel); pg.wait_for_timeout(1500)
            foto(k)
            vis = pg.evaluate("[...document.querySelectorAll('.hs')].filter(h=>h.style.opacity!=='0').length")
            print("%-28s %-7s numeros visibles=%s" % (prod, k, vis))
        # zoom estando en el cuerpo
        if pg.locator("#v-cuerpo").count():
            for _ in range(3):
                pg.click("#v-zoomin"); pg.wait_for_timeout(500)
            pg.wait_for_timeout(700); foto("cuerpo_zoom")
    print("errores:", errs[:3])
    b.close()
