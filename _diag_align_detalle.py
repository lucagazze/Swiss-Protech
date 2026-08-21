import json, os
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8912"
REPR = ["mobilelink-dual-mobility","crown-cup","lubinus-spii","mp-link","optetrak-logic","endomodel-hinged","uni-sled","lcu"]
os.makedirs("_shots3d", exist_ok=True)

JS = r"""
() => {
  const api = window.__v3d, d = api._d, T = d.THREE, M = d.M, anat = d.anat, sil = d.silueta;
  if (!anat) return {err:'sin anat'};
  anat.visible = true; M.raiz.updateMatrixWorld(true);
  const huesoM = [], refM = [];
  anat.traverse(o => { if (o.isMesh) (o.material.opacity <= 0.2 ? refM : huesoM).push(o); });
  const hset = new Set(huesoM.concat(refM));
  const impM = []; M.raiz.traverse(o => { if (o.isMesh && !hset.has(o) && o.visible) impM.push(o); });

  const rc = new T.Raycaster(); rc.far = 1e6;
  const dirs = [new T.Vector3(0.37,0.61,0.70).normalize(), new T.Vector3(-0.81,0.21,0.55).normalize(),
                new T.Vector3(0.11,-0.93,0.35).normalize()];
  function dentro(p, objs) {
    let v = 0;
    for (const dir of dirs) { rc.set(p, dir); const hits = rc.intersectObjects(objs, false);
      let n=0, u=-1e9; for (const h of hits) { if (h.distance-u > 1e-4) { n++; u=h.distance; } }
      if (n % 2 === 1) v++; }
    return v >= 2;
  }
  const porPieza = [];
  for (const o of impM) {
    const p = o.geometry.attributes.position; if (!p) continue;
    const paso = Math.max(1, Math.floor(p.count/80)); const v = new T.Vector3();
    let tot=0, din=0;
    for (let i=0;i<p.count;i+=paso){ v.fromBufferAttribute(p,i); const w=o.localToWorld(v.clone());
      tot++; if (dentro(w, huesoM)) din++; }
    const bb = new T.Box3().setFromObject(o);
    porPieza.push({n:o.name||o.geometry.type, tot, frac:+(din/tot).toFixed(2),
      c: o.getWorldPosition(new T.Vector3()).toArray().map(x=>+x.toFixed(2)),
      dim: [+(bb.max.x-bb.min.x).toFixed(2),+(bb.max.y-bb.min.y).toFixed(2),+(bb.max.z-bb.min.z).toFixed(2)]});
  }
  // eje local +Y de raiz vs vertical, y eje del canal/boca
  const q = M.raiz.getWorldQuaternion(new T.Quaternion());
  const eY = new T.Vector3(0,1,0).applyQuaternion(q);
  const ang = (a,b)=>+(Math.acos(Math.min(1,Math.abs(a.dot(b))))*180/Math.PI).toFixed(1);
  return { porPieza, angRaizYvsVertical: ang(eY,new T.Vector3(0,1,0)),
           anat: M.anatomia };
}
"""

def main():
    out = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width":1180,"height":780})
        for s in REPR:
            pg.goto(f"{BASE}/producto.html?p={s}", wait_until="load", timeout=45000)
            pg.wait_for_timeout(3800)
            try: out[s] = pg.evaluate(JS)
            except Exception as e: out[s] = {"err": str(e)[:200]}
            # capturas: detener autorotacion para reproducibilidad
            pg.evaluate("() => { window.__v3d.setAuto(false); }")
            host = pg.query_selector("#v-solo").evaluate_handle("e => e.closest('body')")
            for ctx, bid in [("1solo","#v-solo"),("2hueso","#v-anatomia"),("3cuerpo","#v-cuerpo")]:
                try:
                    pg.click(bid); pg.wait_for_timeout(1500)
                    pg.evaluate("() => { window.__v3d.setAuto(false); }")
                    pg.wait_for_timeout(400)
                    pg.screenshot(path=f"_shots3d/diag_align_{s}_{ctx}.png", clip=_clip(pg))
                except Exception as e:
                    print("shot err", s, ctx, str(e)[:80])
            print(s, "ok", flush=True)
        b.close()
    json.dump(out, open("_diag_align_detalle.json","w",encoding="utf-8"), indent=1)
    print("LISTO")

def _clip(pg):
    box = pg.evaluate("""() => { const c = document.querySelector('canvas'); const r = c.getBoundingClientRect();
      return {x:Math.max(0,r.x), y:Math.max(0,r.y), width:Math.min(r.width,1180), height:Math.min(r.height,780)}; }""")
    return box

main()
