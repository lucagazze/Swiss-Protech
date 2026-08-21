# -*- coding: utf-8 -*-
"""Mide el salto de maquetado (CLS) de cada pagina en 3 anchos."""
from playwright.sync_api import sync_playwright
import os, sys
BASE = os.environ.get("QA_BASE", "http://localhost:8899")
PAGS = sys.argv[1:] or ["index.html", "productos.html", "producto.html?p=mobilelink-dual-mobility",
                        "proceso.html", "contacto.html", "institucional.html",
                        "representaciones.html", "educacion.html", "multimedia.html"]
PROBE = """(() => { window.__cls = 0; window.__src = [];
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) {
    window.__cls += e.value;
    window.__src.push([+e.value.toFixed(4), (e.sources||[]).slice(0,2).map(s => {
      const n = s.node; return n ? (n.tagName||'#t') + (n.id ? '#'+n.id : '') + (n.className && n.className.toString ? '.'+n.className.toString().split(' ')[0] : '') : '?'; }).join(' ')]);
  } }).observe({type: 'layout-shift', buffered: true}); })()"""

peor = 0
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for vw, vh in ((1440, 900), (768, 1024), (390, 844)):
        c = b.new_context(viewport={"width": vw, "height": vh}); pg = c.new_page()
        pg.add_init_script(PROBE)
        for pa in PAGS:
            pg.goto(BASE + "/" + pa, wait_until="load"); pg.wait_for_timeout(4200)
            cls = pg.evaluate("window.__cls || 0")
            src = pg.evaluate("(window.__src||[]).sort((a,b)=>b[0]-a[0]).slice(0,2)")
            peor = max(peor, cls)
            marca = "<<<" if cls > 0.1 else "   "
            print("%-4d %-42s CLS=%6.3f %s %s" % (vw, pa, cls, marca, src if cls > 0.02 else ""))
        c.close()
    b.close()
print("\npeor CLS:", round(peor, 3), "| umbral 0.1")
