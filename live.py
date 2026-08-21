# -*- coding: utf-8 -*-
"""Verifica el sitio publicado en Vercel."""
from playwright.sync_api import sync_playwright
import os, pathlib
U = "https://swiss-protech.vercel.app/"
SHOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "_shots"
SHOT.mkdir(exist_ok=True)
PAGES = ["", "productos.html", "proceso.html", "producto.html", "contacto.html"]
with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
    for f in PAGES:
        del errs[:]
        pg.goto(U + f, wait_until="networkidle", timeout=60000); pg.wait_for_timeout(1200)
        print("%-16s ovf=%-3s rotas=%-2s claro=%-5s err=%s" % (
            "/" + f,
            pg.evaluate("document.documentElement.scrollWidth - window.innerWidth"),
            pg.evaluate("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length"),
            pg.evaluate("getComputedStyle(document.body).backgroundColor === 'rgb(255, 255, 255)'"),
            errs[:1]))
        pg.screenshot(path=str(SHOT / ("live_" + (f or "index.html").replace(".html", ".png"))))
    b.close()
