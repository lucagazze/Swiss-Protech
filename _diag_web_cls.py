import json, os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8914"
PAGES = [
    ("index", "/index.html"),
    ("productos", "/productos.html"),
    ("producto", "/producto.html?p=lubinus-spii"),
    ("proceso", "/proceso.html"),
    ("contacto", "/contacto.html"),
    ("institucional", "/institucional.html"),
    ("representaciones", "/representaciones.html"),
    ("educacion", "/educacion.html"),
    ("multimedia", "/multimedia.html"),
]
VPS = [("1440", 1440, 900), ("768", 768, 1024), ("390", 390, 844)]

INIT = r"""
window.__cls = 0; window.__shifts = [];
try {
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) {
      if (!e.hadRecentInput) {
        window.__cls += e.value;
        const srcs = (e.sources||[]).map(s => {
          const n = s.node;
          if (!n) return '?';
          let d = n.nodeName ? n.nodeName.toLowerCase() : '?';
          if (n.id) d += '#' + n.id;
          if (n.className && typeof n.className === 'string' && n.className) d += '.' + n.className.trim().split(/\s+/).join('.');
          const pr = s.previousRect, cr = s.currentRect;
          return d + ' prev[' + Math.round(pr.x)+','+Math.round(pr.y)+','+Math.round(pr.width)+','+Math.round(pr.height)+'] cur['+Math.round(cr.x)+','+Math.round(cr.y)+','+Math.round(cr.width)+','+Math.round(cr.height)+']';
        });
        window.__shifts.push({v: e.value, t: Math.round(e.startTime), srcs: srcs});
      }
    }
  }).observe({type:'layout-shift', buffered:true});
} catch(e) { window.__clsErr = String(e); }
"""

os.makedirs("_shots3d", exist_ok=True)
out = {}

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for vpn, w, h in VPS:
        ctx = b.new_context(viewport={"width":w,"height":h}, device_scale_factor=1)
        ctx.add_init_script(INIT)
        for name, path in PAGES:
            pg = ctx.new_page()
            key = f"{name}@{vpn}"
            try:
                pg.goto(BASE+path, wait_until="commit", timeout=30000)
                # shots at 150/400/1200 only on 1440 and 390 to save time
                if vpn in ("1440","390"):
                    pg.wait_for_timeout(150)
                    pg.screenshot(path=f"_shots3d/diag_web_flash_{name}_{vpn}_0150.png")
                    pg.wait_for_timeout(250)
                    pg.screenshot(path=f"_shots3d/diag_web_flash_{name}_{vpn}_0400.png")
                    pg.wait_for_timeout(800)
                    pg.screenshot(path=f"_shots3d/diag_web_flash_{name}_{vpn}_1200.png")
                    pg.wait_for_timeout(2800)
                else:
                    pg.wait_for_timeout(4000)
                cls = pg.evaluate("window.__cls")
                shifts = pg.evaluate("window.__shifts")
                out[key] = {"cls": cls, "shifts": shifts}
            except Exception as e:
                out[key] = {"error": str(e)}
            pg.close()
        ctx.close()
    b.close()

json.dump(out, open("_diag_web_cls.json","w",encoding="utf-8"), indent=1, ensure_ascii=False)
for k,v in out.items():
    if "error" in v: print(k, "ERR", v["error"][:80]); continue
    flag = "  <<<< CLS ALTO" if v["cls"] > 0.1 else ("  < moderado" if v["cls"] > 0.01 else "")
    print(f"{k}: CLS={v['cls']:.4f}{flag}")
    for s in sorted(v["shifts"], key=lambda x:-x["v"])[:3]:
        print(f"    +{s['v']:.4f} @{s['t']}ms  {s['srcs'][:2]}")
