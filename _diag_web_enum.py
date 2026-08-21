import json, os, sys
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

JS_ENUM = r"""
() => {
  const out = {transitions:[], animations:[], keyframes:[], reducedMotion:[], mediaBlocks:[]};
  const LAYOUT_PROPS = ['top','left','right','bottom','width','height','margin','margin-top','margin-left','margin-right','margin-bottom','padding','padding-top','padding-left','padding-bottom','padding-right','font-size','line-height','border-width','flex-basis','gap','max-height','min-height','max-width','min-width'];
  function walk(rules, ctx) {
    for (const r of rules) {
      try {
        if (r.type === 1) { // style
          const s = r.style;
          const tr = s.getPropertyValue('transition') || s.getPropertyValue('transition-property');
          const trd = s.getPropertyValue('transition-duration');
          const an = s.getPropertyValue('animation') || s.getPropertyValue('animation-name');
          if (tr && tr.trim()) {
            out.transitions.push({sel:r.selectorText, value:tr.trim(), dur:trd, ctx:ctx, css:r.cssText.slice(0,300)});
          }
          if (an && an.trim() && an.trim()!=='none') {
            out.animations.push({sel:r.selectorText, value:an.trim(), ctx:ctx});
          }
        } else if (r.type === 7) { // keyframes
          const frames = [];
          for (const k of r.cssRules) frames.push(k.keyText + ' {' + k.style.cssText + '}');
          out.keyframes.push({name:r.name, frames:frames, ctx:ctx});
        } else if (r.type === 4) { // media
          out.mediaBlocks.push(r.conditionText || r.media.mediaText);
          if (/prefers-reduced-motion/.test(r.conditionText||r.media.mediaText||'')) {
            out.reducedMotion.push({cond:r.conditionText||r.media.mediaText, body:r.cssText.slice(0,1200)});
          }
          walk(r.cssRules, (ctx?ctx+' | ':'') + '@media ' + (r.conditionText||r.media.mediaText));
        } else if (r.type === 12 || r.type === 5) {
          if (r.cssRules) walk(r.cssRules, ctx);
        }
      } catch(e) {}
    }
  }
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules, ''); } catch(e) { out.transitions.push({sel:'<<CORS/blocked sheet>>', value:String(e), ctx:''}); }
  }
  // count infinite animation elements currently in DOM
  const inf = [];
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    const it = cs.animationIterationCount;
    const nm = cs.animationName;
    if (nm && nm !== 'none' && it && it.split(',').some(v=>v.trim()==='infinite')) {
      inf.push({tag:el.tagName.toLowerCase(), cls:el.className && el.className.baseVal!==undefined?el.className.baseVal:String(el.className||''), id:el.id, anim:nm, dur:cs.animationDuration});
    }
    // pseudo elements
    for (const pe of ['::before','::after']) {
      const p = getComputedStyle(el, pe);
      if (p.animationName && p.animationName!=='none' && p.animationIterationCount && p.animationIterationCount.split(',').some(v=>v.trim()==='infinite')) {
        inf.push({tag:el.tagName.toLowerCase()+pe, cls:String(el.className||''), id:el.id, anim:p.animationName, dur:p.animationDuration});
      }
    }
  });
  out.infiniteEls = inf;
  return out;
}
"""

def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width":1440,"height":900})
        for name, path in PAGES:
            try:
                pg.goto(BASE+path, wait_until="load", timeout=30000)
                pg.wait_for_timeout(3800 if name=="producto" else 1500)
                res[name] = pg.evaluate(JS_ENUM)
            except Exception as e:
                res[name] = {"error": str(e)}
        b.close()
    with open("_diag_web_enum.json","w",encoding="utf-8") as f:
        json.dump(res,f,indent=1,ensure_ascii=False)
    # print summary
    for name in res:
        r = res[name]
        if "error" in r:
            print(name, "ERROR", r["error"]); continue
        print(f"{name}: trans={len(r['transitions'])} anim={len(r['animations'])} kf={len(r['keyframes'])} rm={len(r['reducedMotion'])} infiniteEls={len(r['infiniteEls'])}")

main()
