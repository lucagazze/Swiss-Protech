# -*- coding: utf-8 -*-
import json, os, sys, re, urllib.request
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8915"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shots3d")
os.makedirs(OUT, exist_ok=True)

PAGS = ["institucional.html", "representaciones.html", "educacion.html", "multimedia.html"]
TODAS = PAGS
VPS = [(1440, 900, "d"), (768, 1024, "t"), (390, 844, "m")]

JS_MEDIR = r"""
() => {
  const R = {};
  const se = document.scrollingElement;
  R.scrollW = se.scrollWidth; R.innerW = window.innerWidth;
  // desbordes horizontales
  const off = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    if (r.right > window.innerWidth + 1.5 || r.left < -1.5) {
      off.push({t: el.tagName + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : ''),
                l: Math.round(r.left), r: Math.round(r.right), w: Math.round(r.width),
                tx: (el.textContent||'').trim().slice(0,50)});
    }
  });
  R.overflow = off.slice(0, 25);

  // overflow de contenido dentro del elemento (texto que se desborda de su caja)
  const clip = [];
  document.querySelectorAll('body *').forEach(el => {
    if (el.children.length > 0) return;
    const cs = getComputedStyle(el);
    if (cs.overflow === 'hidden' || cs.overflowX === 'hidden') {
      if (el.scrollWidth > el.clientWidth + 1) clip.push({t: el.tagName+'.'+el.className, sw: el.scrollWidth, cw: el.clientWidth, tx:(el.textContent||'').trim().slice(0,40)});
    }
    if (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0) {
      clip.push({t: el.tagName+'.'+(typeof el.className==='string'?el.className:''), sw: el.scrollWidth, cw: el.clientWidth, ov: cs.overflow, tx:(el.textContent||'').trim().slice(0,40)});
    }
  });
  R.clipped = clip.slice(0, 25);

  // imagenes rotas
  R.imgs = [];
  document.querySelectorAll('img').forEach(i => {
    if (!i.complete || i.naturalWidth === 0) R.imgs.push({src: i.getAttribute('src'), nw: i.naturalWidth});
  });

  // videos
  R.videos = [];
  document.querySelectorAll('video').forEach(v => {
    R.videos.push({src: v.getAttribute('src'), poster: v.getAttribute('poster'), rs: v.readyState,
                   vw: v.videoWidth, vh: v.videoHeight, err: v.error ? v.error.code : null});
  });

  // areas tactiles
  R.tap = [];
  document.querySelectorAll('a, button, [onclick], input, select, textarea, summary').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') return;
    if (r.width < 40 || r.height < 40) {
      R.tap.push({t: el.tagName + '.' + (typeof el.className==='string'?el.className:''), w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                  tx: (el.textContent||'').trim().slice(0,34), href: el.getAttribute('href')});
    }
  });

  // contraste
  function parseRGB(s){ const m = s.match(/[\d.]+/g); if(!m) return null; return [+m[0],+m[1],+m[2], m[3]!==undefined?+m[3]:1]; }
  function lum(c){ const f = c.map(v => { v/=255; return v<=0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }); return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; }
  function bgOf(el){
    let n = el;
    while (n && n !== document.documentElement) {
      const c = parseRGB(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0.85) return c;
      n = n.parentElement;
    }
    return [255,255,255,1];
  }
  const seen = new Set(); R.contraste = [];
  document.querySelectorAll('body *').forEach(el => {
    const txt = Array.from(el.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join('').trim();
    if (!txt) return;
    const r = el.getBoundingClientRect(); if (r.width===0||r.height===0) return;
    const cs = getComputedStyle(el);
    const fg = parseRGB(cs.color); if (!fg) return;
    const bg = bgOf(el);
    // alpha compose
    const a = fg[3];
    const mix = [0,1,2].map(i => fg[i]*a + bg[i]*(1-a));
    const L1 = lum(mix), L2 = lum(bg.slice(0,3));
    const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const fs = parseFloat(cs.fontSize), fw = parseInt(cs.fontWeight)||400;
    const grande = fs >= 24 || (fs >= 18.66 && fw >= 700);
    const min = grande ? 3.0 : 4.5;
    if (ratio < min) {
      const k = cs.color + '|' + bg.join(',') + '|' + Math.round(fs) + '|' + fw;
      if (seen.has(k)) return; seen.add(k);
      R.contraste.push({sel: el.tagName+'.'+(typeof el.className==='string'?el.className:''), fg: cs.color, bg: 'rgb('+bg.slice(0,3).map(Math.round).join(',')+')',
                        fs: fs, fw: fw, ratio: +ratio.toFixed(2), min: min, tx: txt.slice(0,44)});
    }
  });

  // headings
  R.h = [];
  document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => R.h.push({n: +h.tagName[1], tx: h.textContent.trim().slice(0,50)}));

  // nav activo
  const on = Array.from(document.querySelectorAll('.navlink.on')).map(a=>a.textContent.trim());
  R.navOn = on;
  R.navTotal = document.querySelectorAll('.navlink').length;

  // hrefs internos
  R.hrefs = Array.from(new Set(Array.from(document.querySelectorAll('a[href]')).map(a=>a.getAttribute('href'))));

  // marcadores
  const html = document.body.innerHTML;
  R.marc = [];
  ['[COMPLETAR','FOTO A SOLICITAR','{{','TODO','LOREM','XXXX','PENDIENTE','pendiente de confirmar','A DEFINIR'].forEach(m=>{
    let i = html.indexOf(m);
    while (i >= 0) { R.marc.push({m: m, ctx: html.slice(Math.max(0,i-70), i+90).replace(/\s+/g,' ')}); i = html.indexOf(m, i+1); if (R.marc.length>30) break; }
  });
  return R;
}
"""

# ---- solapamiento especifico de la linea de tiempo
JS_HITO = r"""
() => {
  const out = [];
  document.querySelectorAll('.hito').forEach((h, i) => {
    const a = h.querySelector('.a'); const b = h.children[1];
    if (!a || !b) return;
    const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
    const h3 = b.querySelector('h3');
    const rh = h3 ? h3.getBoundingClientRect() : null;
    // ancho real del texto del rotulo
    const rng = document.createRange(); rng.selectNodeContents(a);
    const rt = rng.getBoundingClientRect();
    out.push({i: i, rotulo: a.textContent.trim(),
              colW: +ra.width.toFixed(1), textoW: +rt.width.toFixed(1), textoRight: +rt.right.toFixed(1),
              colScrollW: a.scrollWidth,
              filaLeft: +rb.left.toFixed(1), h3Left: rh ? +rh.left.toFixed(1) : null,
              h3Text: h3 ? h3.textContent.trim().slice(0,44) : null,
              pisa: rt.right > rb.left + 0.5,
              solape: +(rt.right - rb.left).toFixed(1)});
  });
  return out;
}
"""

res = {}
with sync_playwright() as p:
    br = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    for pag in TODAS:
        slug = pag.split("?")[0].replace(".html", "")
        res[pag] = {}
        for w, hgt, tag in VPS:
            ctx = br.new_context(viewport={"width": w, "height": hgt}, device_scale_factor=1,
                                 has_touch=(tag == "m"), is_mobile=(tag == "m"))
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.type + ": " + m.text) if m.type == "error" else None)
            fails = []
            pg.on("requestfailed", lambda r: fails.append(r.url + " :: " + str(r.failure)))
            pg.goto(BASE + "/" + pag, wait_until="load")
            pg.wait_for_timeout(1200)
            try:
                d = pg.evaluate(JS_MEDIR)
            except Exception as e:
                d = {"err": str(e)}
            d["consoleErr"] = errs[:6]
            d["reqFail"] = fails[:8]
            if pag == "institucional.html":
                d["hitos"] = pg.evaluate(JS_HITO)
            res[pag][tag] = d
            if pag in PAGS:
                pg.screenshot(path=os.path.join(OUT, "diag_paginas_%s_%s.png" % (slug, tag)), full_page=True)
            ctx.close()
    br.close()

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_diag_paginas_out4.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)

# ---- resumen consola
def pr(*a):
    print(*a)

pr("=== SCROLL HORIZONTAL / OVERFLOW ===")
for pag in TODAS:
    for tag in ("d", "t", "m"):
        d = res[pag][tag]
        if d.get("scrollW", 0) > d.get("innerW", 0):
            pr("  %-34s %s  scrollW=%s innerW=%s" % (pag, tag, d["scrollW"], d["innerW"]))
        for o in d.get("overflow", []):
            pr("    OVF %-30s %s  %s l=%s r=%s w=%s | %s" % (pag, tag, o["t"][:44], o["l"], o["r"], o["w"], o["tx"]))

pr("\n=== HITOS (linea de tiempo institucional) ===")
for tag in ("d", "t", "m"):
    pr(" viewport", tag)
    for h in res["institucional.html"][tag].get("hitos", []):
        pr("   %-18s colW=%-6s textoW=%-6s scrollW=%-5s filaLeft=%-7s PISA=%s solape=%s | %s"
           % (h["rotulo"], h["colW"], h["textoW"], h["colScrollW"], h["filaLeft"], h["pisa"], h["solape"], h["h3Text"]))

pr("\n=== TEXTO RECORTADO (scrollWidth > clientWidth) ===")
for pag in TODAS:
    for tag in ("d", "t", "m"):
        for c in res[pag][tag].get("clipped", []):
            pr("  %-34s %s %-40s sw=%s cw=%s ov=%s | %s" % (pag, tag, c["t"][:40], c["sw"], c["cw"], c.get("ov"), c["tx"]))

pr("\n=== IMAGENES ROTAS ===")
for pag in TODAS:
    for tag in ("d",):
        for i in res[pag][tag].get("imgs", []):
            pr("  %-34s %s nw=%s" % (pag, i["src"], i["nw"]))

pr("\n=== VIDEOS ===")
for pag in TODAS:
    for tag in ("d", "m"):
        for v in res[pag][tag].get("videos", []):
            pr("  %-22s %s poster=%s rs=%s %sx%s err=%s | %s" % (pag, tag, v["poster"], v["rs"], v["vw"], v["vh"], v["err"], v["src"]))

pr("\n=== TAP TARGETS <40 (390px) ===")
for pag in TODAS:
    vis = {}
    for t in res[pag]["m"].get("tap", []):
        k = (t["t"], t["tx"], t["w"], t["h"])
        vis[k] = vis.get(k, 0) + 1
    for k, n in vis.items():
        pr("  %-34s %-38s %sx%s  x%s | %s" % (pag, k[0][:38], k[2], k[3], n, k[1]))

pr("\n=== CONTRASTE < min ===")
for pag in TODAS:
    for c in res[pag]["d"].get("contraste", []):
        pr("  %-34s ratio=%-5s min=%s fs=%s fw=%s fg=%s bg=%s | %s | %s" % (pag, c["ratio"], c["min"], c["fs"], c["fw"], c["fg"], c["bg"], c["sel"][:34], c["tx"]))

pr("\n=== HEADINGS ===")
for pag in TODAS:
    hs = res[pag]["d"].get("h", [])
    seq = [h["n"] for h in hs]
    h1 = [h for h in hs if h["n"] == 1]
    saltos = []
    prev = 0
    for h in hs:
        if prev and h["n"] > prev + 1:
            saltos.append("h%d->h%d (%s)" % (prev, h["n"], h["tx"]))
        prev = h["n"]
    pr("  %-34s h1=%d seq=%s" % (pag, len(h1), seq))
    for s in saltos:
        pr("      SALTO %s" % s)

pr("\n=== NAV ACTIVO ===")
for pag in TODAS:
    pr("  %-34s on=%s total=%s" % (pag, res[pag]["d"].get("navOn"), res[pag]["d"].get("navTotal")))

pr("\n=== MARCADORES ===")
for pag in TODAS:
    for m in res[pag]["d"].get("marc", []):
        pr("  %-34s [%s] %s" % (pag, m["m"], m["ctx"][:150]))

pr("\n=== CONSOLE / REQ FAIL ===")
for pag in TODAS:
    for tag in ("d",):
        for e in res[pag][tag].get("consoleErr", []):
            pr("  %-34s CONSOLE %s" % (pag, e[:140]))
        for e in res[pag][tag].get("reqFail", []):
            pr("  %-34s REQFAIL %s" % (pag, e[:140]))

# ---- enlaces
pr("\n=== ENLACES ===")
todos = {}
for pag in TODAS:
    for h in res[pag]["d"].get("hrefs", []):
        todos.setdefault(h, set()).add(pag)
for h in sorted(todos):
    if h.startswith("http") or h.startswith("mailto") or h.startswith("tel"):
        continue
    if h == "#" or h.startswith("#"):
        pr("  ANCLA/VACIO  %-30s en %s" % (h, sorted(todos[h])))
        continue
    url = BASE + "/" + h.lstrip("/")
    try:
        r = urllib.request.urlopen(url, timeout=8)
        code = r.getcode()
    except Exception as e:
        code = getattr(e, "code", str(e))
    if code != 200:
        pr("  ROTO %-4s %-40s en %s" % (code, h, sorted(todos[h])))
    else:
        pr("  ok   200  %-40s" % h)

print("\nOK")
