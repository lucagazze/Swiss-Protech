# -*- coding: utf-8 -*-
"""Prueba a fondo el visor 3D: cada punto debe cambiar la camara y resaltar su parte."""
from playwright.sync_api import sync_playwright
import pathlib, os
ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
SHOT = ROOT / "_shots3d"; SHOT.mkdir(exist_ok=True)
BASE = os.environ.get("QA_BASE", "http://localhost:8899")

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:150]))
    pg.goto(BASE + "/producto.html?p=mobilelink-dual-mobility", wait_until="load")
    pg.wait_for_timeout(4000)

    caja = pg.locator("#stage3d").bounding_box()
    print("canvas:", pg.evaluate("!!document.querySelector('#stage3d canvas')"), "| puntos:", pg.evaluate("document.querySelectorAll('.hs').length"))

    def foto(nombre):
        pg.screenshot(path=str(SHOT / (nombre + ".png")),
                      clip={"x": caja["x"], "y": caja["y"], "width": caja["width"], "height": caja["height"]})

    foto("00_inicial")
    prev = None
    for i in range(6):
        pg.click(".hs-item[data-i='%d']" % i)
        pg.wait_for_timeout(1600)
        titulo = pg.evaluate("document.getElementById('v-titulo').textContent")
        estado = pg.evaluate("document.getElementById('v-estado').textContent")
        visibles = pg.evaluate("[...document.querySelectorAll('.hs')].filter(h=>h.style.opacity!=='0').length")
        marcado = pg.evaluate("document.querySelectorAll('.hs.on').length + '/' + document.querySelectorAll('.hs-item.on').length")
        print("punto %d | %-42s | estado=%-28s | marcadores visibles=%s | on=%s" % (i + 1, titulo[:42], estado, visibles, marcado))
        foto("%02d_punto%d" % (i + 1, i + 1))
    # ---- hero del inicio
    pg.goto(BASE + "/index.html", wait_until="load"); pg.wait_for_timeout(4500)
    print("HERO canvas:", pg.evaluate("!!document.querySelector('#hero3d canvas')"),
          "| slots ocultos:", pg.evaluate("[...document.querySelectorAll('.slot')].every(s=>s.style.display==='none')"),
          "| botones:", pg.evaluate("!!document.getElementById('h3-explotar') && !!document.getElementById('h3-auto')"),
          "| rotulo:", pg.evaluate("document.getElementById('heroNombre').textContent"))
    pg.screenshot(path=str(SHOT / "hero_00.png"), clip={"x":700,"y":120,"width":740,"height":700})
    pg.click("#h3-explotar"); pg.wait_for_timeout(1400)
    pg.screenshot(path=str(SHOT / "hero_01_explotado.png"), clip={"x":700,"y":120,"width":740,"height":700})
    print("errores:", errs[:3])
    b.close()
