import json, sys
from playwright.sync_api import sync_playwright

SLUGS = ["mobilelink-dual-mobility","mobilelink","bimobile","crown-cup","element","lcu","lubinus-cup",
"lubinus-spii","mp-link","endomodel-modular","endomodel-hinged","endomodel-standard","optetrak-cc",
"optetrak-hiflex","optetrak-logic","uni-sled","copal","palacos-mv","palacos-r","palamix-gun","palamix-uno"]

JS_REST = r"""
() => {
  const d = window.__v3d._d, T = d.THREE;
  const caja = () => { d.M.raiz.updateMatrixWorld(true);
    const c = new T.Box3(); d.M.raiz.traverse(o => { if (o.isMesh && o.visible) c.expandByObject(o); });
    return c.isEmpty()? null : [c.min.x,c.min.y,c.min.z,c.max.x,c.max.y,c.max.z]; };
  const vis = () => { const a=[]; d.M.raiz.traverse(o=>{ if(o.isMesh) a.push(o.visible?1:0); }); return a; };
  const rots = () => { const a=[]; d.M.raiz.traverse(o=>{ a.push([o.rotation.x,o.rotation.y,o.rotation.z,o.position.x,o.position.y,o.position.z]); }); return a; };
  return { hay: !!window.__v3d.hayMovimiento, caja: caja(), vis: vis(), rots: rots() };
}
"""

JS_ANGLES = r"""
() => {
  const d = window.__v3d._d;
  if (!d.M.animar) return null;
  const nodes = []; d.M.raiz.traverse(o => nodes.push(o));
  const names = nodes.map(o => o.type + (o.isMesh ? ':'+(o.geometry?o.geometry.type:'?') : ''));
  const N = 121, S = [];
  for (let i = 0; i < N; i++) { const t = i/(N-1); d.M.animar(t);
    S.push(nodes.map(o => [o.rotation.x,o.rotation.y,o.rotation.z])); }
  d.M.animar(null);
  const out = [];
  for (let j = 0; j < nodes.length; j++) {
    const r = [0,1,2].map(k => { let mn=1e9,mx=-1e9; for(const s of S){ mn=Math.min(mn,s[j][k]); mx=Math.max(mx,s[j][k]); } return [mn,mx]; });
    const amp = Math.max(...r.map(a => a[1]-a[0]));
    if (amp > 1e-6) out.push({ i:j, name:names[j], rx:r[0], ry:r[1], rz:r[2] });
  }
  return out;
}
"""

def run(pw, slug):
    b = pw.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width":1280,"height":860})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"http://localhost:8913/producto.html?p={slug}")
    pg.wait_for_timeout(3800)
    r = {"slug": slug}
    st0 = pg.evaluate(JS_REST)
    r["hayMov"] = st0["hay"]
    r["angulos"] = pg.evaluate(JS_ANGLES)
    if st0["hay"]:
        # box en reposo
        pg.wait_for_timeout(200)
        a = pg.evaluate(JS_REST)
        pg.click("#v-mov"); pg.wait_for_timeout(2600)
        r["mov_on_boton"] = pg.eval_on_selector("#v-mov", "e=>e.classList.contains('on')")
        pg.click("#v-mov"); pg.wait_for_timeout(1600)
        c = pg.evaluate(JS_REST)
        r["mov_off_boton"] = pg.eval_on_selector("#v-mov", "e=>e.classList.contains('on')")
        r["caja_pre"] = a["caja"]; r["caja_post"] = c["caja"]
        r["dmax"] = max(abs(x-y) for x,y in zip(a["caja"], c["caja"])) if a["caja"] and c["caja"] else None
        r["vis_igual"] = a["vis"] == c["vis"]
        r["rot_dmax"] = max(max(abs(u-v) for u,v in zip(p,q)) for p,q in zip(a["rots"], c["rots"]))
    r["errs"] = errs
    b.close()
    return r

res = []
with sync_playwright() as pw:
    for s in SLUGS:
        try:
            res.append(run(pw, s))
        except Exception as e:
            res.append({"slug": s, "error": repr(e)[:300]})
        print("ok", s, flush=True)

open("_diag_modelo_out1.json","w",encoding="utf-8").write(json.dumps(res, indent=1))
print("DONE")
