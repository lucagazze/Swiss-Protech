# -*- coding: utf-8 -*-
"""Prueba el visor a fondo: encuadre monotono, piezas completas, marcadores a traves,
   clic al fondo para salir, y la camara siguiendo la pieza mirada."""
from playwright.sync_api import sync_playwright
import pathlib, os, json
ROOT = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
SHOT = ROOT / "_shots3d"; SHOT.mkdir(exist_ok=True)
BASE = os.environ.get("QA_BASE", "http://localhost:8899")

SONDA = """() => { const d = window.__v3d._d; window.__m = [];
  (function l(){ window.__m.push(d.cam.position.distanceTo(d.ctl.target)); requestAnimationFrame(l); })(); }"""

ANALIZA = """() => { const m = window.__m.slice(); window.__m = [];
  if (m.length < 5) return {n: m.length, rebote: 0, salto: 0};
  const rec = Math.max(1e-6, Math.abs(m[m.length-1] - m[0]));
  let subeMax = 0, bajaMax = 0, salto = 0;
  for (let i = 1; i < m.length; i++) {
    const dd = m[i] - m[i-1];
    if (dd > 0) subeMax += dd; else bajaMax += -dd;
    salto = Math.max(salto, Math.abs(dd) / rec);
  }
  // rebote = cuanto se movio en contra del sentido general, en % del recorrido
  const neto = m[m.length-1] - m[0];
  const contra = neto >= 0 ? bajaMax : subeMax;
  return {n: m.length, d0: +m[0].toFixed(3), d1: +m[m.length-1].toFixed(3),
          rebote: +(contra / rec * 100).toFixed(1), salto: +(salto * 100).toFixed(1)}; }"""

# centro y tamano del implante proyectados a pantalla
ENCUADRE = """() => { const d = window.__v3d._d, T = d.THREE;
  const anat = []; if (d.anat) d.anat.traverse(o => { if (o.isMesh) anat.push(o); });
  if (d.silueta) d.silueta.traverse(o => { if (o.isMesh) anat.push(o); });
  const c = new T.Box3();
  d.M.raiz.traverse(o => { if (o.isMesh && o.visible && !anat.includes(o)) c.expandByObject(o); });
  if (c.isEmpty()) return null;
  const w = d.cam.userData.w || window.__v3d._d.cam, cv = document.querySelector('#stage3d canvas');
  const W = cv.clientWidth, H = cv.clientHeight;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  for (const X of [c.min.x, c.max.x]) for (const Y of [c.min.y, c.max.y]) for (const Z of [c.min.z, c.max.z]) {
    const v = new T.Vector3(X,Y,Z).project(d.cam);
    const px = (v.x*.5+.5)*W, py = (-v.y*.5+.5)*H;
    x0=Math.min(x0,px); x1=Math.max(x1,px); y0=Math.min(y0,py); y1=Math.max(y1,py);
  }
  return { cx: +(((x0+x1)/2 - W/2)/W*100).toFixed(1), cy: +(((y0+y1)/2 - H/2)/H*100).toFixed(1),
           alto: +((y1-y0)/H*100).toFixed(1), ancho: +((x1-x0)/W*100).toFixed(1) }; }"""

PRODS = ["mobilelink-dual-mobility", "crown-cup", "lubinus-cup", "lubinus-spii", "optetrak-logic", "palacos-r"]
fallos = []

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    c = b.new_context(viewport={"width": 1440, "height": 900}); pg = c.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))

    for prod in PRODS:
        pg.goto(BASE + "/producto.html?p=" + prod, wait_until="load")
        pg.wait_for_timeout(3800)
        st = pg.locator("#stage3d"); st.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
        enc = pg.evaluate(ENCUADRE)
        print("\n== %s ==  encuadre inicial centro=(%.1f%%,%.1f%%) tam=%.0f%%x%.0f%%"
              % (prod, enc["cx"], enc["cy"], enc["ancho"], enc["alto"]))
        if abs(enc["cx"]) > 8 or abs(enc["cy"]) > 8:
            fallos.append("%s: encuadre inicial descentrado %s" % (prod, enc))
        if enc["alto"] < 25:
            fallos.append("%s: producto muy chico en el encuadre inicial (%s%%)" % (prod, enc["alto"]))
        st.screenshot(path=str(SHOT / ("v_%s_inicial.png" % prod)))

        # piezas visibles en reposo vs explotado
        n0 = pg.evaluate("() => { let n=0; window.__v3d._d.M.raiz.traverse(o => { if (o.isMesh && o.visible) n++; }); return n; }")
        pg.click("#v-explotar"); pg.wait_for_timeout(1200)
        n1 = pg.evaluate("() => { let n=0; window.__v3d._d.M.raiz.traverse(o => { if (o.isMesh && o.visible) n++; }); return n; }")
        st.screenshot(path=str(SHOT / ("v_%s_explotado.png" % prod)))
        print("   piezas visibles  reposo=%d  explotado=%d  %s" % (n0, n1, "OK" if n0 == n1 else "<<< APARECEN PIEZAS"))
        if n0 != n1:
            fallos.append("%s: en reposo se ven %d mallas y explotado %d" % (prod, n0, n1))
        pg.click("#v-explotar"); pg.wait_for_timeout(1000)

        # transiciones: la distancia no puede rebotar
        acciones = [("punto 3", ".hs-item[data-i='2']"), ("punto 1", ".hs-item[data-i='0']")]
        if pg.locator("#v-anatomia").is_visible():
            acciones += [("en el hueso", "#v-anatomia"), ("en el cuerpo", "#v-cuerpo"),
                         ("producto", "#v-solo"), ("cuerpo directo", "#v-cuerpo")]
        acciones += [("zoom +", "#v-zoomin"), ("zoom -", "#v-zoomout")]
        if pg.evaluate("() => !!window.__v3d.hayMovimiento"):
            acciones += [("movimiento on", "#v-mov"), ("movimiento off", "#v-mov")]
        for nombre, sel in acciones:
            pg.evaluate(SONDA); pg.wait_for_timeout(80)
            pg.click(sel); pg.wait_for_timeout(2300)
            r = pg.evaluate(ANALIZA)
            mal = r["rebote"] > 4
            print("   %-14s d %6.2f -> %6.2f  rebote=%5.1f%%  n=%3d  %s"
                  % (nombre, r.get("d0", 0), r.get("d1", 0), r["rebote"], r["n"], "<<< REBOTE" if mal else ""))
            if mal:
                fallos.append("%s / %s: rebote=%.1f%% salto=%.1f%%" % (prod, nombre, r["rebote"], r["salto"]))

        # el producto sigue centrado en cualquier contexto
        if pg.locator("#v-cuerpo").is_visible():
            for k, sel in (("solo", "#v-solo"), ("hueso", "#v-anatomia"), ("cuerpo", "#v-cuerpo")):
                pg.click(sel); pg.wait_for_timeout(1600)
                e = pg.evaluate(ENCUADRE)
                if abs(e["cx"]) > 8 or abs(e["cy"]) > 8:
                    fallos.append("%s / contexto %s: producto fuera del centro %s" % (prod, k, e))
                print("   centro en %-7s (%5.1f%%, %5.1f%%)" % (k, e["cx"], e["cy"]))
            pg.click("#v-solo"); pg.wait_for_timeout(1400)

        # marcadores: los de atras se ven igual
        pg.evaluate("() => window.__v3d.setAuto(false)")
        pg.wait_for_timeout(400)
        vis = pg.evaluate("[...document.querySelectorAll('.hs')].filter(h => parseFloat(h.style.opacity||1) > 0.05).length")
        tot = pg.evaluate("document.querySelectorAll('.hs').length")
        atras = pg.evaluate("document.querySelectorAll('.hs.atras').length")
        print("   marcadores visibles %d/%d (de atras: %d)" % (vis, tot, atras))
        if vis < tot:
            fallos.append("%s: %d de %d marcadores invisibles" % (prod, tot - vis, tot))

        # clic al fondo sale del punto
        pg.click(".hs-item[data-i='1']"); pg.wait_for_timeout(1500)
        activo_antes = pg.evaluate("document.querySelectorAll('.hs-item.on').length")
        caja = st.bounding_box()
        vh = pg.viewport_size["height"]
        bx = caja["x"] + 26
        by = min(caja["y"] + caja["height"] - 130, vh - 40)
        by = max(by, caja["y"] + 90)
        quien = pg.evaluate("([x,y]) => { const e = document.elementFromPoint(x,y); return e ? (e.tagName + '.' + (e.className||'')) : 'nada'; }", [bx, by])
        print("   elemento bajo el clic:", quien)
        pg.mouse.click(bx, by)
        pg.wait_for_timeout(1300)
        activo_desp = pg.evaluate("document.querySelectorAll('.hs-item.on').length")
        info = pg.evaluate("document.getElementById('v-info').classList.contains('on')")
        print("   clic al fondo: punto activo %d -> %d, tarjeta abierta=%s" % (activo_antes, activo_desp, info))
        if activo_antes != 1 or activo_desp != 0 or info:
            fallos.append("%s: el clic al fondo no cierra el punto (%d->%d, tarjeta=%s)" % (prod, activo_antes, activo_desp, info))

    print("\nerrores JS:", errs[:4])
    print("\nFALLOS:", "ninguno" if not fallos else "")
    for f in fallos: print("  -", f)
    b.close()
