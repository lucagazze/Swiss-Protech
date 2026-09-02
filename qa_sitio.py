# -*- coding: utf-8 -*-
"""
Comprobaciones automaticas del sitio, contra la copia publicable.

  python -u build_site.py       # deja site/ al dia
  python -u qa_sitio.py         # levanta site/ y lo revisa

Revisa el armazon y el <head> de las diez paginas, los filtros del catalogo, el
formulario de contacto, el visor 3D, el comportamiento en celular y la
tipografia y las areas tactiles en siete anchos. Sale con codigo 1 si algo
falla, para poder encadenarlo.
"""
import asyncio, os, subprocess, sys, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.async_api import async_playwright

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "site")
PUERTO = 8917
U = "http://127.0.0.1:%d/" % PUERTO

PAGS = ["index", "productos", "producto", "proceso", "institucional",
        "representaciones", "educacion", "multimedia", "contacto", "privacidad"]
ANCHOS = [320, 360, 390, 430, 600, 768, 1024]

fallos, oks = [], []


def chk(cond, msg):
    (oks if cond else fallos).append(msg)


def servir():
    """Sirve site/ en un hilo, que es lo que se sube al hosting."""
    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=OUT, **k)
        def log_message(self, *a):
            pass
    s = ThreadingHTTPServer(("127.0.0.1", PUERTO), H)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    time.sleep(0.6)
    return s


JS_PAGINA = """() => ({
  topbar: !!document.querySelector('.sp-topbar'),
  cta:    !!document.querySelector('.sp-cta'),
  foot:   !!document.querySelector('.sp-foot'),
  wa:     !!document.querySelector('.sp-wa[href*="wa.me"]'),
  canon:  !!document.querySelector('link[rel=canonical]'),
  icon:   !!document.querySelector('link[rel=icon]'),
  og:     !!document.querySelector('meta[property="og:image"]'),
  ld:     document.querySelectorAll('script[type="application/ld+json"]').length,
  primero:(document.querySelector('.navlinks a') || {}).textContent,
  h1:     document.querySelectorAll('h1').length,
  muertos:document.querySelectorAll('a[href="#"], a[href=""]').length,
  sinAlt: Array.from(document.images).filter(i => !i.alt).length,
  completar: /\\[COMPLETAR/i.test(document.body.innerText),
})"""

JS_MEDIDAS = """() => {
  const chico = [...document.querySelectorAll('p,span,a,li,b')].filter(e => {
    const f = parseFloat(getComputedStyle(e).fontSize);
    return f > 0 && f < 11 && e.textContent.trim().length > 3 && e.getBoundingClientRect().width > 0;
  }).length;
  const tap = [...document.querySelectorAll('a,button')].filter(e => {
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && (r.height < 34 || r.width < 34)
        && !(e.className + '').includes('sr-skip') && !(e.className + '').includes('hs');
  }).length;
  return { chico, tap,
           desb: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1 };
}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        pg = await (await b.new_context(viewport={"width": 1440, "height": 900})).new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))

        # ---------------------------------------------- armazon y <head>
        for n in PAGS:
            errs.clear()
            await pg.goto(U + n + ".html"); await pg.wait_for_timeout(700)
            d = await pg.evaluate(JS_PAGINA)
            chk(d["topbar"] and d["cta"] and d["foot"], f"{n}: armazon completo")
            chk(d["wa"], f"{n}: boton flotante de WhatsApp")
            chk(d["canon"] and d["icon"] and d["og"], f"{n}: canonical, favicon y og:image")
            chk(d["ld"] >= 1, f"{n}: datos estructurados")
            chk((d["primero"] or "").strip() == "Inicio", f"{n}: 'Inicio' primero en la nav")
            chk(d["h1"] == 1, f"{n}: un solo h1 ({d['h1']})")
            chk(d["muertos"] == 0, f"{n}: sin enlaces muertos ({d['muertos']})")
            chk(d["sinAlt"] == 0, f"{n}: todas las imagenes con alt")
            chk(not d["completar"], f"{n}: sin marcadores [COMPLETAR]")
            chk(not errs, f"{n}: sin errores de JS ({errs[:1]})")

        # ---------------------------------------------- home: tarjetas de linea
        for slug, esp in [("cadera", 9), ("rodilla", 7), ("cementos", 5)]:
            await pg.goto(U + "index.html"); await pg.wait_for_timeout(500)
            await pg.click(f"a.cardw[href*='{slug}']"); await pg.wait_for_timeout(900)
            v = await pg.evaluate("Array.from(document.querySelectorAll('.pc')).filter(e=>e.offsetParent).length")
            chk(slug in pg.url and v == esp, f"home: la tarjeta {slug} abre su linea ({v} de {esp})")

        # ---------------------------------------------- catalogo
        await pg.goto(U + "productos.html"); await pg.wait_for_timeout(700)
        async def visibles():
            return await pg.evaluate("Array.from(document.querySelectorAll('.pc')).filter(e=>e.offsetParent).length")
        chk(await visibles() == 21, "catalogo: 21 productos al entrar")
        for lbl, esp in [("cadera", 9), ("rodilla", 7), ("cementos", 5)]:
            await pg.click(f"[data-filter='{lbl}']"); await pg.wait_for_timeout(300)
            chk(await visibles() == esp, f"catalogo: linea {lbl} = {esp}")
        await pg.click("[data-filter='todos']"); await pg.wait_for_timeout(300)
        for m, esp in [("link", 11), ("advita", 5), ("heraeus", 5)]:
            await pg.click(f"[data-marca-f='{m}']"); await pg.wait_for_timeout(300)
            chk(await visibles() == esp, f"catalogo: marca {m} = {esp}")
            await pg.click(f"[data-marca-f='{m}']"); await pg.wait_for_timeout(200)
        await pg.click("[data-filter='cementos']"); await pg.click("[data-marca-f='link']")
        await pg.wait_for_timeout(300)
        vac = await pg.evaluate("(document.getElementById('sinResultados')||{}).offsetParent !== null")
        chk(await visibles() == 0 and vac, "catalogo: el cruce vacio avisa")
        # el rotulo de marca sale del catalogo, no del maquetado
        await pg.goto(U + "productos.html"); await pg.wait_for_timeout(500)
        cc = await pg.evaluate("""() => { const a = document.querySelector("a[href*='crown-cup']");
                                          return a ? a.querySelector('span').textContent : '' }""")
        chk("ADVITA" in cc, f"catalogo: Crown Cup rotulado {cc!r}")

        # ---------------------------------------------- contacto
        await pg.goto(U + "contacto.html"); await pg.wait_for_timeout(700)
        t = await pg.evaluate("""() => ({
            inputs: document.querySelectorAll('#formConsulta input, #formConsulta textarea').length,
            submit: !!document.querySelector('#formConsulta button[type=submit]'),
            mapa: (document.getElementById('mapa') || {}).src || '' })""")
        chk(t["inputs"] >= 5 and t["submit"], "contacto: formulario con campos reales")
        chk("openstreetmap" in t["mapa"], "contacto: mapa cargado")
        for c, txt in [("cl", "Chile"), ("uy", "Uruguay")]:
            await pg.click(f"[data-pais='{c}']"); await pg.wait_for_timeout(400)
            body = await pg.evaluate("document.body.innerText")
            chk("[COMPLETAR" not in body.upper(), f"contacto: {txt} sin placeholders")
        await pg.click("[data-pais='ar']"); await pg.wait_for_timeout(300)
        await pg.click("#formConsulta button[type=submit]"); await pg.wait_for_timeout(300)
        chk(await pg.evaluate("(document.getElementById('formError')||{}).offsetParent !== null"),
            "contacto: valida antes de enviar")
        await pg.fill("#fNombre", "Dr. Prueba"); await pg.fill("#fMail", "a@b.com")
        await pg.fill("#fTel", "1122334455"); await pg.fill("#fMsg", "Consulta de prueba")
        await pg.check("#fOk")
        await pg.click("#formConsulta button[type=submit]"); await pg.wait_for_timeout(500)
        chk(not await pg.evaluate("(document.getElementById('formError')||{}).offsetParent !== null"),
            "contacto: acepta un formulario valido")

        # ---------------------------------------------- visor 3D
        await pg.goto(U + "producto.html?p=endomodel-modular"); await pg.wait_for_timeout(4200)
        v = await pg.evaluate("""() => {
            const st = document.querySelector('#stage3d');
            const h = [...document.querySelectorAll('.hs')].filter(e => parseFloat(e.style.opacity || 1) > 0.05)
              .map(e => { const m = /translate\\(([-\\d.]+)px, ([-\\d.]+)px\\)/.exec(e.style.transform);
                          return m ? [+m[1], +m[2]] : null }).filter(Boolean);
            let min = 1e9;
            for (let i = 0; i < h.length; i++) for (let j = i + 1; j < h.length; j++)
              min = Math.min(min, Math.hypot(h[i][0] - h[j][0], h[i][1] - h[j][1]));
            const t = [...document.querySelectorAll('.hs-item')].map(e => e.textContent.trim().toLowerCase()
              .normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''));
            return { min, n: h.length, dup: t.length - new Set(t).size,
                     enCanvas: st.querySelectorAll('.v-grupo').length,
                     barra: !!document.querySelector('.v-barra') };
        }""")
        chk(v["min"] > 25, f"visor 3D: marcadores separados (min {v['min']:.0f} px)")
        chk(v["dup"] == 0, "visor 3D: sin puntos duplicados")
        chk(v["enCanvas"] == 0 and v["barra"], "visor 3D: los controles no tapan el modelo")

        # ---------------------------------------------- celular
        pg2 = await (await b.new_context(viewport={"width": 390, "height": 800})).new_page()
        await pg2.goto(U + "index.html"); await pg2.wait_for_timeout(600)
        await pg2.click(".burger"); await pg2.wait_for_timeout(400)
        n_it = await pg2.evaluate("document.querySelectorAll('#drawer a').length")
        chk(await pg2.evaluate("document.getElementById('drawer').classList.contains('open')") and n_it == 7,
            f"movil: el menu abre con 7 items (dio {n_it})")

        # ---------------------------------------------- tipografia y tacto
        for w in ANCHOS:
            ctx = await b.new_context(viewport={"width": w, "height": 900})
            p3 = await ctx.new_page()
            tap = chico = desb = 0
            for n in PAGS:
                await p3.goto(U + n + ".html")
                await p3.wait_for_timeout(3400 if n == "producto" else 800)
                d = await p3.evaluate(JS_MEDIDAS)
                tap += d["tap"]; chico += d["chico"]; desb += 1 if d["desb"] else 0
            chk(desb == 0, f"{w} px: sin desborde horizontal ({desb})")
            chk(chico == 0, f"{w} px: sin texto por debajo de 11 px ({chico})")
            chk(tap == 0, f"{w} px: sin objetivos tactiles por debajo de 34 px ({tap})")
            await ctx.close()

        await b.close()

    # ---------------------------------------------- archivos que se publican
    for f in ["sitemap.xml", "robots.txt", "privacidad.html", "assets/favicon.png",
              "assets/og.jpg", "assets/film-poster.webp",
              "media/swiss-protech.mp4", "media/swiss-protech-loop.mp4"]:
        chk(os.path.exists(os.path.join(OUT, f)), f"site/: esta {f}")
    png = [x for x in os.listdir(os.path.join(OUT, "assets")) if x.endswith(".png")]
    chk(png == ["favicon.png"], f"assets: solo WebP mas el favicon ({png})")

    print("\n=== OK (%d) ===" % len(oks))
    for o in oks:
        print("  +", o)
    print("\n=== FALLAS (%d) ===" % len(fallos))
    for f in fallos:
        print("  !", f)
    return 1 if fallos else 0


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        print("Falta site/. Corre antes:  python -u build_site.py")
        sys.exit(1)
    servir()
    sys.exit(asyncio.run(main()))
