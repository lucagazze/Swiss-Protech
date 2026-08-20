# -*- coding: utf-8 -*-
"""Control de calidad del sitio generado: desborde, imagenes, errores, interacciones."""
from playwright.sync_api import sync_playwright
import pathlib, os

SITE = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "site"
SHOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "_shots"
SHOT.mkdir(exist_ok=True)
PAGES = ["index.html", "productos.html", "proceso.html", "producto.html", "contacto.html"]

rep = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (768, 1024), (390, 844)]:
        c = b.new_context(viewport={"width": w, "height": h})
        pg = c.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:110]))
        for f in PAGES:
            del errs[:]
            pg.goto((SITE / f).as_uri(), wait_until="load")
            pg.wait_for_timeout(900)
            ov = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            broken = pg.evaluate("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src'))")
            holes = pg.evaluate("(document.body.innerText.match(/\\{\\{[^}]+\\}\\}/g)||[])")
            rep.append("%dx%d %-15s ovf=%-3s rotas=%-2d holes=%d err=%s"
                       % (w, h, f, ov, len(broken), len(holes), errs[:1]))
            if broken:
                rep.append("      ROTAS: " + ", ".join(broken[:4]))
            if w == 1440:
                pg.screenshot(path=str(SHOT / ("d_" + f.replace(".html", ".png"))), full_page=True)
            if w == 390:
                pg.screenshot(path=str(SHOT / ("m_" + f.replace(".html", ".png"))), full_page=True)
        c.close()

    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    pg.goto((SITE / "index.html").as_uri(), wait_until="load"); pg.wait_for_timeout(1200)
    rep.append("HERO: " + pg.evaluate("document.getElementById('heroNombre').textContent"))
    pg.click('[data-hero="3"]'); pg.wait_for_timeout(900)
    rep.append("HERO tras click: " + pg.evaluate("document.getElementById('heroNombre').textContent"))

    pg.goto((SITE / "productos.html").as_uri(), wait_until="load"); pg.wait_for_timeout(600)
    pg.click('[data-filter="rodilla"]'); pg.wait_for_timeout(400)
    rep.append("FILTRO: " + str(pg.evaluate("[...document.querySelectorAll('[data-grupo]')].filter(g=>g.style.display!=='none').map(g=>g.dataset.grupo)")))

    pg.goto((SITE / "producto.html").as_uri(), wait_until="load"); pg.wait_for_timeout(600)
    t0 = pg.evaluate("document.getElementById('obj').style.transform")
    pg.click("#rotR"); pg.wait_for_timeout(400)
    rep.append("VISOR: %s -> %s" % (t0, pg.evaluate("document.getElementById('obj').style.transform")))

    pg.goto((SITE / "contacto.html").as_uri(), wait_until="load"); pg.wait_for_timeout(600)
    pg.click('[data-quien="paciente"]'); pg.wait_for_timeout(300)
    pg.click('[data-pais="cl"]'); pg.wait_for_timeout(300)
    rep.append("CONTACTO: %s | %s" % (pg.evaluate("document.getElementById('quienTxt').textContent"),
                                      pg.evaluate("document.getElementById('sede1Dir').textContent")))
    b.close()
print("\n".join(rep))
