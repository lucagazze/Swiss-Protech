# -*- coding: utf-8 -*-
"""Control de calidad del sitio: desborde, imagenes, errores, 3D e interacciones."""
from playwright.sync_api import sync_playwright
import pathlib, os, json

ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
SHOT = ROOT / "_shots"; SHOT.mkdir(exist_ok=True)
BASE = os.environ.get("QA_BASE", "http://localhost:8899")
url = lambda f: BASE + "/" + f
PAGES = ["index.html", "productos.html", "proceso.html", "contacto.html",
         "institucional.html", "representaciones.html", "educacion.html", "multimedia.html",
         "producto.html?p=mobilelink-dual-mobility", "producto.html?p=optetrak-logic",
         "producto.html?p=bimobile", "producto.html?p=palamix-gun"]

rep = []
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for w, h in [(1440, 900), (768, 1024), (390, 844)]:
        c = b.new_context(viewport={"width": w, "height": h})
        pg = c.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)[:110]))
        pg.on("console", lambda m: errs.append("console:" + m.text[:90]) if m.type == "error" else None)
        for f in PAGES:
            del errs[:]
            pg.goto(url(f), wait_until="load")
            pg.wait_for_timeout(1800 if "producto" in f else 900)
            ov = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            broken = pg.evaluate("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src'))")
            holes = pg.evaluate("(document.body.innerText.match(/\\{\\{[^}]+\\}\\}/g)||[])")
            rep.append("%dx%d %-42s ovf=%-3s rotas=%-2d holes=%d err=%s" % (w, h, f, ov, len(broken), len(holes), errs[:1]))
            if broken:
                rep.append("      ROTAS: " + ", ".join(str(x) for x in broken[:4]))
            if w == 1440:
                pg.screenshot(path=str(SHOT / ("d_" + f.replace("?p=", "_").replace(".html", "") + ".png")), full_page=True)
            if w == 390:
                pg.screenshot(path=str(SHOT / ("m_" + f.replace("?p=", "_").replace(".html", "") + ".png")), full_page=True)
        c.close()

    # ---- interacciones
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:140]))
    pg.goto(url("producto.html?p=mobilelink-dual-mobility"), wait_until="load")
    pg.wait_for_timeout(3500)
    rep.append("3D canvas: %s | cargando visible: %s | hotspots: %s | err=%s" % (
        pg.evaluate("!!document.querySelector('#stage3d canvas')"),
        pg.evaluate("!!document.getElementById('v-cargando')"),
        pg.evaluate("document.querySelectorAll('.hs').length"), errs[:2]))
    if pg.evaluate("document.querySelectorAll('.hs').length"):
        pg.click(".hs-item[data-i='3']"); pg.wait_for_timeout(1200)
        rep.append("punto 4 -> " + pg.evaluate("document.getElementById('v-titulo').textContent"))
        pg.click("#v-explotar"); pg.wait_for_timeout(1100)
        pg.screenshot(path=str(SHOT / "d_3d_explotado.png"), clip={"x": 100, "y": 300, "width": 800, "height": 760})
        pg.click("#v-explotar"); pg.click("#v-corte"); pg.wait_for_timeout(900)
        pg.screenshot(path=str(SHOT / "d_3d_corte.png"), clip={"x": 100, "y": 300, "width": 800, "height": 760})
        pg.click("#v-corte"); pg.wait_for_timeout(400)
    pg.click("[data-t='fotos']"); pg.wait_for_timeout(600)
    rep.append("fotos: miniaturas=%s" % pg.evaluate("document.querySelectorAll('.thumb').length"))
    pg.click("[data-t='video']"); pg.wait_for_timeout(900)
    rep.append("videos: %s | reproduciendo=%s" % (
        pg.evaluate("document.querySelectorAll('#vid-grid video').length"),
        pg.evaluate("[...document.querySelectorAll('#vid-grid video')].filter(v=>!v.paused).length")))
    pg.screenshot(path=str(SHOT / "d_producto_video.png"), full_page=True)

    pg.goto(url("productos.html"), wait_until="load"); pg.wait_for_timeout(700)
    pg.click('[data-filter="cementos"]'); pg.wait_for_timeout(400)
    rep.append("FILTRO: " + str(pg.evaluate("[...document.querySelectorAll('[data-grupo]')].filter(g=>g.style.display!=='none').map(g=>g.dataset.grupo)")))
    pg.click('[data-filter="todos"]'); pg.wait_for_timeout(300)
    pg.click(".pc"); pg.wait_for_load_state("load"); pg.wait_for_timeout(1500)
    rep.append("catalogo -> ficha: " + pg.url.split("/")[-1] + " | " + pg.evaluate("document.getElementById('h-nombre').textContent"))

    pg.goto(url("contacto.html"), wait_until="load"); pg.wait_for_timeout(600)
    pg.click('[data-quien="paciente"]'); pg.click('[data-pais="cl"]'); pg.wait_for_timeout(300)
    rep.append("CONTACTO: %s | %s" % (pg.evaluate("document.getElementById('quienTxt').textContent"),
                                      pg.evaluate("document.getElementById('sede1Dir').textContent")))
    b.close()
print("\n".join(rep))
