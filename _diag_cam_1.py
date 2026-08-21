import json, os, sys, math
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8911"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shots3d")
os.makedirs(OUT, exist_ok=True)
RES = {}

# ---------------------------------------------------------------- instrumentacion
# Se engancha cam.updateMatrixWorld: WebGLRenderer.render() la llama justo antes de
# dibujar, asi que lo que se registra es EXACTAMENTE el estado que ve el usuario
# (post ctl.update(), o sea post-clamp y post-autoRotate).
HOOK = r"""
() => {
  const d = window.__v3d._d;
  if (window.__hooked) return true;
  window.__hooked = true;
  window.__rend = [];   // serie renderizada (ground truth)
  window.__tw   = [];   // serie escrita por el tween (post-paso, pre-clamp)
  const orig = d.cam.updateMatrixWorld.bind(d.cam);
  d.cam.updateMatrixWorld = function (f) {
    if (window.__rec) window.__rend.push({
      t: performance.now(),
      dist: d.cam.position.distanceTo(d.ctl.target),
      cam: d.cam.position.toArray().map(x => +x.toFixed(5)),
      tgt: d.ctl.target.toArray().map(x => +x.toFixed(5)),
      auto: d.ctl.autoRotate, mn: d.ctl.minDistance, mx: d.ctl.maxDistance
    });
    return orig(f);
  };
  (function loop(){
    if (window.__rec) window.__tw.push({
      t: performance.now(),
      dist: d.cam.position.distanceTo(d.ctl.target),
      auto: d.ctl.autoRotate
    });
    requestAnimationFrame(loop);
  })();
  return true;
}
"""

START = "() => { window.__rend = []; window.__tw = []; window.__rec = true; }"
STOP  = "() => { window.__rec = false; return { rend: window.__rend, tw: window.__tw }; }"

# encuadre: caja del IMPLANTE (mallas de M.raiz que no cuelgan de d.anat) proyectada
ENC = r"""
() => {
  const d = window.__v3d._d, T = d.THREE;
  const anatSet = new Set();
  if (d.anat) d.anat.traverse(o => anatSet.add(o));
  const caja = new T.Box3();
  let n = 0;
  d.M.raiz.traverse(o => { if (o.isMesh && o.visible && !anatSet.has(o)) { caja.expandByObject(o); n++; } });
  if (n === 0 || caja.isEmpty()) return null;
  const cv = d.cam.parent ? null : null;
  const host = document.querySelector('#stage3d');
  const W = host.clientWidth, H = host.clientHeight;
  d.cam.updateMatrixWorld(true); d.cam.updateProjectionMatrix();
  let minx=1e9, maxx=-1e9, miny=1e9, maxy=-1e9, detras=0;
  const v = new T.Vector3();
  for (const x of [caja.min.x, caja.max.x])
   for (const y of [caja.min.y, caja.max.y])
    for (const z of [caja.min.z, caja.max.z]) {
      v.set(x,y,z).project(d.cam);
      if (v.z > 1) detras++;
      const px = (v.x*0.5+0.5)*W, py = (-v.y*0.5+0.5)*H;
      minx=Math.min(minx,px); maxx=Math.max(maxx,px);
      miny=Math.min(miny,py); maxy=Math.max(maxy,py);
    }
  const cx = (minx+maxx)/2, cy = (miny+maxy)/2;
  return {
    W, H, detras,
    dx_px: +(cx - W/2).toFixed(1), dy_px: +(cy - H/2).toFixed(1),
    dx_pct: +(100*(cx - W/2)/W).toFixed(2), dy_pct: +(100*(cy - H/2)/H).toFixed(2),
    alto_pct: +(100*(maxy-miny)/H).toFixed(2), ancho_pct: +(100*(maxx-minx)/W).toFixed(2),
    dist: +d.cam.position.distanceTo(d.ctl.target).toFixed(4),
    ctx: d.contexto, mn: +d.ctl.minDistance.toFixed(4), mx: +d.ctl.maxDistance.toFixed(4)
  };
}
"""

def analiza(serie):
    ds = [s["dist"] for s in serie]
    if len(ds) < 4:
        return {"n": len(ds), "vacio": True}
    lo, hi = min(ds), max(ds)
    rec = hi - lo
    neto = abs(ds[-1] - ds[0])
    tv = sum(abs(ds[i+1]-ds[i]) for i in range(len(ds)-1))
    exceso = tv - neto            # cuanto se va y vuelve
    saltos = [abs(ds[i+1]-ds[i]) for i in range(len(ds)-1)]
    salto_max = max(saltos) if saltos else 0
    ref = max(rec, neto, 1e-9)
    # pelea: autoRotate true mientras la distancia cambia
    pelea = any(serie[i]["auto"] and abs(ds[i+1]-ds[i]) > 0.001*ref for i in range(len(ds)-1))
    # donde ocurre el maximo / minimo (para ver si sube y baja)
    i_hi, i_lo = ds.index(hi), ds.index(lo)
    return {
        "n": len(ds), "d0": round(ds[0],4), "dfin": round(ds[-1],4),
        "min": round(lo,4), "max": round(hi,4), "recorrido": round(rec,4),
        "exceso": round(exceso,4), "exceso_pct": round(100*exceso/ref,2),
        "salto_max_pct": round(100*salto_max/ref,2),
        "i_max": i_hi, "i_min": i_lo,
        "NO_MONOTONA": exceso > 0.03*ref,
        "SALTO": salto_max > 0.15*ref,
        "PELEA": pelea,
        "auto_fin": serie[-1]["auto"],
        "mn": round(serie[-1].get("mn",0),4), "mx": round(serie[-1].get("mx",0),4),
    }

def medir(page, nombre, accion, espera=2500):
    page.evaluate(START)
    accion()
    page.wait_for_timeout(espera)
    data = page.evaluate(STOP)
    r = analiza(data["rend"])
    r["tween"] = analiza(data["tw"])
    r["enc"] = page.evaluate(ENC)
    # muestreo comprimido de la serie renderizada para inspeccion
    ds = [round(s["dist"],4) for s in data["rend"]]
    r["serie"] = ds[::max(1, len(ds)//28)][:30]
    RES.setdefault(nombre[0], {})[nombre[1]] = r
    return r

def corre(page, slug, tiene_anat, tiene_hs=True):
    page.goto(f"{BASE}/producto.html?p={slug}", wait_until="load")
    page.wait_for_timeout(3800)
    ok = page.evaluate("() => !!(window.__v3d && window.__v3d._d)")
    if not ok:
        RES[slug] = {"ERROR": "sin window.__v3d"}
        return
    page.evaluate(HOOK)
    inf = page.evaluate("""() => { const d = window.__v3d._d;
        return { anat: !!d.anat, sil: !!d.silueta, ctx: d.contexto,
                 mn: d.ctl.minDistance, mx: d.ctl.maxDistance,
                 dist: d.cam.position.distanceTo(d.ctl.target), auto: d.ctl.autoRotate,
                 npuntos: window.__v3d.total, mov: window.__v3d.hayMovimiento }; }""")
    RES.setdefault(slug, {})["_info"] = inf
    RES[slug]["_enc_inicial"] = page.evaluate(ENC)

    C = lambda sel: (lambda: page.click(sel, force=True))

    if tiene_anat:
        # 1 solo -> hueso
        medir(page, (slug, "1_solo_a_hueso"), C("#v-anatomia"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_hueso.png")
        # 2 hueso -> cuerpo
        medir(page, (slug, "2_hueso_a_cuerpo"), C("#v-cuerpo"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_cuerpo.png")
        # 3 cuerpo -> solo
        medir(page, (slug, "3_cuerpo_a_solo"), C("#v-solo"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_solo.png")
        # 4 solo -> cuerpo DIRECTO  (el que reporta el usuario)
        medir(page, (slug, "4_solo_a_cuerpo_DIRECTO"), C("#v-cuerpo"), espera=3000)
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_cuerpo_directo.png")
        # 5 punto estando en cuerpo
        if tiene_hs:
            medir(page, (slug, "5_punto2_desde_cuerpo"), C(".hs-item[data-i='2']"))
            page.screenshot(path=f"{OUT}/diag_cam_{slug}_p2_desde_cuerpo.png")
        # volver a solo limpio
        page.click("#v-solo", force=True); page.wait_for_timeout(1400)

    # 6 punto en solo, luego otro
    if tiene_hs:
        medir(page, (slug, "6a_punto1_desde_solo"), C(".hs-item[data-i='1']"))
        medir(page, (slug, "6b_punto3_desde_punto1"), C(".hs-item[data-i='3']"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_p3.png")
        # 9 reiniciar
        medir(page, (slug, "9_info_x_reiniciar"), C("#v-info-x"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_reiniciar.png")

    # 7 movimiento
    if inf.get("mov"):
        medir(page, (slug, "7a_mov_on"), C("#v-mov"))
        medir(page, (slug, "7b_mov_off"), C("#v-mov"))
        page.click("#v-solo", force=True) if tiene_anat else None
        page.wait_for_timeout(1200)

    # 8 zoom en cada contexto
    ctxs = [("solo", "#v-solo")] + ([("hueso", "#v-anatomia"), ("cuerpo", "#v-cuerpo")] if tiene_anat else [])
    for nom, sel in ctxs:
        page.click(sel, force=True); page.wait_for_timeout(1500)
        def zin():
            for _ in range(3):
                page.click("#v-zoomin", force=True); page.wait_for_timeout(140)
        def zout():
            for _ in range(3):
                page.click("#v-zoomout", force=True); page.wait_for_timeout(140)
        medir(page, (slug, f"8a_zoomin3_{nom}"), zin, espera=2200)
        medir(page, (slug, f"8b_zoomout3_{nom}"), zout, espera=2200)
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_zoom_{nom}.png")

    # 10 pantalla completa
    page.click("#v-solo", force=True) if tiene_anat else None
    page.wait_for_timeout(1200)
    try:
        antes = page.evaluate(ENC)
        page.evaluate(START)
        page.click("#v-full", force=True)
        page.wait_for_timeout(2500)
        fs = page.evaluate("() => ({ fs: !!document.fullscreenElement, w: document.querySelector('#stage3d').clientWidth, h: document.querySelector('#stage3d').clientHeight })")
        dfs = page.evaluate(STOP)
        r = analiza(dfs["rend"]); r["enc"] = page.evaluate(ENC); r["fs"] = fs; r["enc_antes"] = antes
        RES[slug]["10a_entrar_full"] = r
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_full.png")
        medir(page, (slug, "10b_salir_full"), C("#v-full"))
        page.screenshot(path=f"{OUT}/diag_cam_{slug}_full_salir.png")
    except Exception as e:
        RES[slug]["10_full"] = {"ERROR": repr(e)}

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1440,"height":900})
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append("PAGEERROR " + str(e)))
    for slug, anat in [("mobilelink-dual-mobility", True), ("lubinus-spii", True),
                       ("optetrak-logic", True), ("palacos-r", False)]:
        try:
            corre(pg, slug, anat)
        except Exception as e:
            RES.setdefault(slug, {})["FATAL"] = repr(e)
    RES["_console"] = errs[:40]
    b.close()

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_diag_cam_out.json")
open(p, "w", encoding="utf-8").write(json.dumps(RES, indent=1, ensure_ascii=False))
print("LISTO ->", p)
