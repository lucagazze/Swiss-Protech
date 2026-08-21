import json, os, sys
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8912"
SLUGS = ["mobilelink-dual-mobility","mobilelink","bimobile","crown-cup","element","lcu","lubinus-cup",
         "lubinus-spii","mp-link","endomodel-modular","endomodel-hinged","endomodel-standard",
         "optetrak-cc","optetrak-hiflex","optetrak-logic","uni-sled",
         "copal","palacos-mv","palacos-r","palamix-gun","palamix-uno"]

JS = r"""
() => {
  const api = window.__v3d; if (!api) return {err:'sin __v3d'};
  const d = api._d, T = d.THREE;
  const anat = d.anat, sil = d.silueta, M = d.M;
  M.raiz.updateMatrixWorld(true);

  // ---- set de mallas del hueso / referencia / silueta
  const huesoM = [], refM = [];
  if (anat) { anat.visible = true; anat.updateMatrixWorld(true);
    anat.traverse(o => { if (o.isMesh) { (o.material.opacity <= 0.2 ? refM : huesoM).push(o); } }); }
  const huesoSet = new Set(huesoM.concat(refM));

  // ---- mallas del implante
  const impM = [];
  M.raiz.traverse(o => { if (o.isMesh && !huesoSet.has(o) && o.visible) impM.push(o); });

  const cajaImp = new T.Box3(); impM.forEach(o => cajaImp.expandByObject(o));
  const esfImp = cajaImp.getBoundingSphere(new T.Sphere());
  const cajaHue = new T.Box3(); huesoM.forEach(o => cajaHue.expandByObject(o));

  // ---- a) transform de raiz
  const R = M.raiz;
  const out = {
    raiz: { pos:[+R.position.x.toFixed(4),+R.position.y.toFixed(4),+R.position.z.toFixed(4)],
            rot:[+R.rotation.x.toFixed(4),+R.rotation.y.toFixed(4),+R.rotation.z.toFixed(4)],
            rotDeg:[+(R.rotation.x*180/Math.PI).toFixed(2),+(R.rotation.y*180/Math.PI).toFixed(2),+(R.rotation.z*180/Math.PI).toFixed(2)],
            esc:[+R.scale.x.toFixed(4),+R.scale.y.toFixed(4),+R.scale.z.toFixed(4)] },
    anatomia: M.anatomia || null,
    impCentro: [+esfImp.center.x.toFixed(4),+esfImp.center.y.toFixed(4),+esfImp.center.z.toFixed(4)],
    impRadio: +esfImp.radius.toFixed(4),
    impCaja: cajaImp.isEmpty()?null:{min:cajaImp.min.toArray().map(v=>+v.toFixed(3)), max:cajaImp.max.toArray().map(v=>+v.toFixed(3))},
    huesoCaja: cajaHue.isEmpty()?null:{min:cajaHue.min.toArray().map(v=>+v.toFixed(3)), max:cajaHue.max.toArray().map(v=>+v.toFixed(3))},
    nImp: impM.length, nHueso: huesoM.length
  };

  // ---- b) fraccion del implante dentro del hueso (parity raycast)
  if (huesoM.length) {
    const rc = new T.Raycaster(); rc.far = 1e6;
    const dirs = [new T.Vector3(0.37,0.61,0.70).normalize(), new T.Vector3(-0.8,0.2,0.55).normalize()];
    const pts = [];
    for (const o of impM) {
      const p = o.geometry.attributes.position; if (!p) continue;
      const paso = Math.max(1, Math.floor(p.count / 60));
      const v = new T.Vector3();
      for (let i = 0; i < p.count; i += paso) { v.fromBufferAttribute(p, i); o.localToWorld(v.clone()); pts.push(o.localToWorld(v.clone())); }
    }
    let dentro = 0, total = 0;
    for (const p of pts) {
      total++;
      let votos = 0;
      for (const dir of dirs) {
        rc.set(p, dir);
        const hits = rc.intersectObjects(huesoM, false);
        // contar cruces unicos (evitar dobles por DoubleSide en misma cara)
        let n = 0, ult = -1e9;
        for (const h of hits) { if (h.distance - ult > 1e-4) { n++; ult = h.distance; } }
        if (n % 2 === 1) votos++;
      }
      if (votos >= 1) dentro++;
    }
    out.fracDentro = total ? +(dentro/total).toFixed(3) : null;
    out.nMuestras = total;
  }

  // ---- c) ejes
  const ejeHuesoLocalY = new T.Vector3(0,1,0).applyQuaternion(R.getWorldQuaternion(new T.Quaternion())).normalize();
  // PCA del implante
  let ejeImp = null;
  {
    const pts = [];
    for (const o of impM) {
      const p = o.geometry.attributes.position; if (!p) continue;
      const paso = Math.max(1, Math.floor(p.count / 40)); const v = new T.Vector3();
      for (let i = 0; i < p.count; i += paso) { v.fromBufferAttribute(p, i); pts.push(o.localToWorld(v.clone())); }
    }
    if (pts.length > 8) {
      const c = new T.Vector3(); pts.forEach(p => c.add(p)); c.multiplyScalar(1/pts.length);
      let cov = [[0,0,0],[0,0,0],[0,0,0]];
      for (const p of pts) { const x=p.x-c.x,y=p.y-c.y,z=p.z-c.z;
        cov[0][0]+=x*x;cov[0][1]+=x*y;cov[0][2]+=x*z;cov[1][1]+=y*y;cov[1][2]+=y*z;cov[2][2]+=z*z; }
      cov[1][0]=cov[0][1];cov[2][0]=cov[0][2];cov[2][1]=cov[1][2];
      let v = new T.Vector3(0.3,1,0.2).normalize();
      for (let it=0; it<80; it++) {
        const nx = cov[0][0]*v.x+cov[0][1]*v.y+cov[0][2]*v.z;
        const ny = cov[1][0]*v.x+cov[1][1]*v.y+cov[1][2]*v.z;
        const nz = cov[2][0]*v.x+cov[2][1]*v.y+cov[2][2]*v.z;
        v.set(nx,ny,nz).normalize();
      }
      ejeImp = v;
    }
  }
  const ang = (a,b) => +(Math.acos(Math.min(1,Math.abs(a.dot(b))))*180/Math.PI).toFixed(2);
  const UP = new T.Vector3(0,1,0);
  out.ejeHuesoWorld = ejeHuesoLocalY.toArray().map(v=>+v.toFixed(3));
  out.angHuesoVsVerticalCuerpo = ang(ejeHuesoLocalY, UP);
  if (ejeImp) { out.ejeImpWorld = ejeImp.toArray().map(v=>+v.toFixed(3));
                out.angImpVsHueso = ang(ejeImp, ejeHuesoLocalY);
                out.angImpVsVertical = ang(ejeImp, UP); }

  // ---- d/e) anillo marcador
  if (sil) {
    sil.visible = true; sil.updateMatrixWorld(true);
    let marca = null;
    sil.traverse(o => { if (o.isMesh && o.geometry && o.geometry.type === 'TorusGeometry') marca = o; });
    const cajaSil = new T.Box3();
    sil.traverse(o => { if (o.isMesh && o !== marca) cajaSil.expandByObject(o); });
    const altoSil = cajaSil.max.y - cajaSil.min.y;
    out.silEscala = +sil.scale.x.toFixed(4);
    out.silAlto = +altoSil.toFixed(3);
    out.silCaja = {min:cajaSil.min.toArray().map(v=>+v.toFixed(3)), max:cajaSil.max.toArray().map(v=>+v.toFixed(3))};
    out.ratioSilImp = +(altoSil / (esfImp.radius*2)).toFixed(2);
    if (marca) {
      const wp = marca.getWorldPosition(new T.Vector3());
      out.anilloPos = wp.toArray().map(v=>+v.toFixed(4));
      out.distAnilloImp = +wp.distanceTo(esfImp.center).toFixed(4);
      out.distAnilloImpPctAlto = +((wp.distanceTo(esfImp.center)/altoSil)*100).toFixed(2);
      out.alturaRelAnillo = +(((wp.y - cajaSil.min.y)/altoSil)).toFixed(3);
      const cm = new T.Box3().setFromObject(marca);
      out.anilloRadioMundo = +(((cm.max.x-cm.min.x)/2)).toFixed(4);
      out.anilloRadioPctAlto = +(((cm.max.x-cm.min.x)/2/altoSil*100).toFixed(2));
    }
    // f) piso vs cuerpo
    out.pisoY = +d.piso.position.y.toFixed(4);
    out.pisoDentroDelCuerpo = (d.piso.position.y > cajaSil.min.y + 0.001 && d.piso.position.y < cajaSil.max.y - 0.001);
    out.pisoAlturaRel = +(((d.piso.position.y - cajaSil.min.y)/altoSil)).toFixed(3);
    let sol = null; d.escena.traverse(o => { if (o.isDirectionalLight && o.castShadow) sol = o; });
    if (sol) { const sc = sol.shadow.camera;
      out.shadowCam = {l:sc.left,r:sc.right,t:sc.top,b:sc.bottom,near:sc.near,far:sc.far};
      out.shadowCubreCuerpo = ( (sc.right-sc.left) >= (cajaSil.max.x-cajaSil.min.x) ); }
  }
  return out;
}
"""

def main():
    res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width":1280,"height":820})
        for s in SLUGS:
            try:
                pg.goto(f"{BASE}/producto.html?p={s}", wait_until="load", timeout=45000)
                pg.wait_for_timeout(3800)
                r = pg.evaluate(JS)
            except Exception as e:
                r = {"err": str(e)[:200]}
            res[s] = r
            print(s, "OK" if "err" not in r else r["err"], flush=True)
        b.close()
    with open("_diag_align_datos.json","w",encoding="utf-8") as f:
        json.dump(res,f,indent=1)
    print("LISTO")

main()
