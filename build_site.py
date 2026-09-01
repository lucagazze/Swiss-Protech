# -*- coding: utf-8 -*-
"""
Convierte los artboards .dc.html en un sitio estatico navegable.
Salida: site/  ->  index.html, productos.html, proceso.html, producto.html,
                   contacto.html, assets/
Ejecutar:  python -u build_site.py
"""
import json, os, re, shutil

import shell

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "site")
ACCENT = "#0095A1"

PAGES = [
    ("Main.dc.html",      "index.html",     "Swiss Protech — Implantes ortopédicos con trazabilidad de punta a punta",
     "Representantes exclusivos en Argentina de prótesis de cadera y rodilla de Waldemar Link, Advita Ortho y Heraeus Medical. Más de 20 años de trayectoria."),
    ("Productos.dc.html", "productos.html", "Catálogo de productos — Swiss Protech",
     "21 productos entre prótesis de cadera, rodilla y cementos óseos. Marcas Link, Advita Ortho y Heraeus."),
    ("Proceso.dc.html",   "proceso.html",   "Nuestro proceso — Swiss Protech",
     "Las cinco etapas de trazabilidad: depósito, control, esterilización, traslado y entrega en quirófano."),
    ("Contacto.dc.html",  "contacto.html",  "Contacto — Swiss Protech",
     "Sedes en CABA y Rosario. Consultas de médicos, obras sociales, prepagas y pacientes."),
]

MIGAS = {
    "index.html":     [("Home", "index.html")],
    "productos.html": [("Home", "index.html"), ("Productos", "productos.html")],
    "proceso.html":   [("Home", "index.html"), ("Nuestro proceso", "proceso.html")],
    "contacto.html":  [("Home", "index.html"), ("Contacto", "contacto.html")],
}


def cargar_productos():
    """Lee js/productos.js para que el catálogo salga de una sola fuente."""
    t = open(os.path.join(SRC, "js", "productos.js"), encoding="utf-8").read()
    i, j = t.index("window.PRODUCTOS = "), t.index(";\nwindow.ORDEN")
    return json.loads(t[i + len("window.PRODUCTOS = "):j])


def marca_corta(marca):
    m = marca.lower()
    if "link" in m:
        return "link", "LINK"
    if "advita" in m:
        return "advita", "ADVITA"
    return "heraeus", "HERAEUS"

NAV = [
    ("Inicio",           "index.html"),
    ("Institucional",    "institucional.html"),
    ("Productos",        "productos.html"),
    ("Nuestro proceso",  "proceso.html"),
    ("Educación médica", "educacion.html"),
    ("Representaciones", "representaciones.html"),
    ("Contacto",         "contacto.html"),
]

RESPONSIVE = """
/* ============ responsive ============ */
.wrap { width: 100%; max-width: 1440px; margin: 0 auto; }
img { max-width: 100%; }
html, body { overflow-x: hidden; }
html { scroll-behavior: smooth; }
.navwrap { overflow-x: auto; }

@media (max-width: 1240px) {
  [style*="grid-template-columns: 1fr 620px"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 700px 1fr"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 400px 1fr"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 1fr 420px"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 320px repeat(3"] { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  [style*="grid-template-columns: 1fr 300px"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: repeat(5"] { grid-template-columns: repeat(3, minmax(0,1fr)) !important; }
  .rail { display: none !important; }
  .navlinks { display: none !important; }
  .burger { display: flex !important; }
}
@media (max-width: 980px) {
  [style*="grid-template-columns: repeat(4"] { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  [style*="grid-template-columns: repeat(3"] { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  [style*="grid-template-columns: repeat(5"] { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  h1:not(.hero-h1) { font-size: clamp(30px, 6.4vw, 52px) !important; }
  h2 { font-size: clamp(24px, 4.6vw, 40px) !important; }
  .viewer { height: 480px !important; }
  .filtbar { flex-direction: column !important; align-items: flex-start !important; gap: 14px !important; }
}
@media (max-width: 720px) {
  .navcta { display: none !important; }
  [style*="grid-template-columns: repeat(4"] { grid-template-columns: repeat(2, minmax(0,1fr)) !important; }
  [style*="grid-template-columns: repeat(3"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: repeat(5"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: repeat(2"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 320px repeat(3"] { grid-template-columns: minmax(0,1fr) !important; }
  [style*="grid-template-columns: 200px 1fr"] { grid-template-columns: minmax(0,1fr) !important; gap: 2px !important; }
  [style*="grid-template-columns: 88px 1fr"] { grid-template-columns: 62px 1fr !important; gap: 14px !important; }
  [style*="padding: 92px 40px 100px"] { padding: 52px 20px 60px !important; }
  [style*="padding: 0 40px"] { padding: 0 20px !important; }
  [style*="padding: 20px 40px"] { padding: 14px 20px !important; }
  [style*="padding: 60px 56px"] { padding: 40px 22px !important; }
  [style*="padding: 40px 42px"] { padding: 26px 22px !important; }
  [style*="padding: 44px 46px"] { padding: 28px 22px !important; }
  [style*="padding: 34px 40px"] { padding: 24px 22px !important; flex-direction: column !important; align-items: flex-start !important; }
  .ring { width: 240px !important; height: 240px !important; }
  .ring-i { width: 150px !important; height: 150px !important; }
  .viewer { height: 400px !important; }
  .obj img { width: 190px !important; height: 190px !important; }
  .disc { display: none !important; }
  .ctarow { flex-direction: column !important; align-items: flex-start !important; gap: 22px !important; }
  .ctarow a { width: 100%; justify-content: center; }
  .btnrow { flex-wrap: wrap !important; }
  .btnrow a { flex-grow: 1; justify-content: center; }
  .spine { display: none !important; }

  /* paddings anchos heredados del diseno de escritorio */
  [style*="padding: 18px 40px"] { padding: 14px 20px !important; }
  [style*="padding: 26px 28px"] { padding: 20px 18px !important; }
  [style*="padding: 30px 28px"] { padding: 22px 18px !important; }
  [style*="padding: 32px 26px"] { padding: 22px 18px !important; }
  [style*="padding: 34px 30px"] { padding: 22px 18px !important; }
  [style*="padding: 44px 40px"] { padding: 26px 20px !important; }
  [style*="padding: 28px 32px 28px 0"] { padding: 20px 18px 20px 0 !important; }
  [style*="padding: 30px 22px 26px"] { padding: 26px 18px 22px !important; }
  [style*="padding: 24px 26px"] { padding: 20px 18px !important; }
  [style*="padding: 62px 0 58px"] { padding: 40px 0 36px !important; }
  [style*="padding: 60px 0 54px"] { padding: 40px 0 34px !important; }
  [style*="padding: 86px 0 78px"] { padding: 48px 0 44px !important; }

  /* filas de chips que no deben empujar el ancho */
  .filtbar > div, .paisbar { flex-wrap: wrap !important; }
  .obj img { width: 180px !important; height: 180px !important; }
  h1, h2, h3 { overflow-wrap: break-word; }

  /* encabezados de seccion con boton al costado: se apilan */
  [style*="align-items: flex-end; justify-content: space-between; gap: 40px"] {
    flex-direction: column !important; align-items: flex-start !important; gap: 22px !important; }
  [style*="align-items: baseline; gap: 14px"] { flex-wrap: wrap !important; }
  /* fila de logos representados: envuelve en vez de cortarse */
  [style*="gap: 13px; padding-top: 8px"] { flex-wrap: wrap !important; row-gap: 16px !important; }
  [style*="gap: 13px; padding-top: 8px"] > span[style*="flex-grow: 1"] { display: none !important; }
  [style*="align-items: center; justify-content: space-between; gap: 26px"] {
    flex-direction: column !important; align-items: flex-start !important; gap: 18px !important; }
}
"""

HERO3D_CSS = ""

BURGER_CSS = """
.burger { display: none; width: 44px; height: 44px; border-radius: 6px; border: 1px solid #E3E7E9;
          align-items: center; justify-content: center; cursor: pointer; flex: none; }
.burger.dark { border-color: rgba(255,255,255,.2); }
.drawer { display: none; flex-direction: column; gap: 2px; padding: 10px 20px 18px;
          border-bottom: 1px solid #E3E7E9; background: #FFFFFF; }
.drawer.dark { background: #0A171D; border-color: rgba(255,255,255,.09); }
.drawer.open { display: flex; }
.drawer a { padding: 14px 4px; font-size: 15px; font-weight: 500; color: #10222A;
            border-bottom: 1px solid #F1F4F5; min-height: 50px; display: flex; align-items: center; }
.drawer.dark a { color: #C6D0D4; border-color: rgba(255,255,255,.07); }
"""


def leer(nombre):
    with open(os.path.join(SRC, nombre), encoding="utf-8") as f:
        return f.read()


def extraer(src):
    """Devuelve (css_helmet, links_helmet, cuerpo)."""
    helmet = re.search(r"<helmet>(.*?)</helmet>", src, re.S)
    hm = helmet.group(1) if helmet else ""
    css = "\n".join(m.group(1) for m in re.finditer(r"<style>(.*?)</style>", hm, re.S))
    links = "\n".join(re.findall(r'<link[^>]*>', hm))
    cuerpo = re.search(r"<x-dc>(.*?)</x-dc>", src, re.S).group(1)
    cuerpo = re.sub(r"<helmet>.*?</helmet>", "", cuerpo, flags=re.S)
    return css, links, cuerpo


def wire_nav(cuerpo, actual):
    """Pone los href reales en la navegacion y marca la pagina activa."""
    # los artboards se disenaron sin "Inicio": se agrega como primer item
    cuerpo = cuerpo.replace('<a href="#" class="navlink" style="color: #10222A;">Institucional</a>',
                            '<a href="index.html" class="navlink" style="color: #10222A;">Inicio</a>'
                            '<a href="#" class="navlink" style="color: #10222A;">Institucional</a>', 1)
    cuerpo = cuerpo.replace('gap: 34px; font-size: 14px; font-weight: 500; color: #10222A;',
                            'gap: 26px; font-size: 14px; font-weight: 500; color: #10222A;')
    for texto, href in NAV:
        cuerpo = re.sub(
            r'<a href="#"(\s+class="navlink"[^>]*)>(\s*)' + re.escape(texto) + r'(\s*)</a>',
            lambda m, h=href, t=texto: '<a href="%s"%s>%s</a>' % (h, m.group(1), t),
            cuerpo)
    # el maquetado trae un item resaltado a mano: el resaltado real depende de
    # que pagina se esta construyendo
    def repintar(m):
        href, resto, texto = m.group(1), m.group(2), m.group(3)
        on = (href == actual)
        estilo = 'color: #0095A1; font-weight: 600;' if on else 'color: #10222A;'
        cls = 'navlink on' if on else 'navlink'
        aria = ' aria-current="page"' if on else ''
        return '<a href="%s" class="%s"%s style="%s">%s</a>' % (href, cls, aria, estilo, texto)
    cuerpo = re.sub(r'<a href="([a-z]+\.html)"( class="navlink"[^>]*)>([^<]+)</a>', repintar, cuerpo)

    # el logo de la barra tiene que volver al home
    cuerpo = re.sub(r'(?<!">)<img src="logo\.webp" alt="Swiss Protech"',
                    '<a href="index.html" aria-label="Swiss Protech — inicio"><img src="logo.webp" alt="Swiss Protech"', cuerpo)
    cuerpo = cuerpo.replace('style="height: 42px; width: auto; display: block;">',
                            'style="height: 42px; width: auto; display: block;"></a>', 1)
    return cuerpo


# ------------------------------------------------------------ ruteo de botones
# El maquetado deja todos los enlaces en href="#". Se resuelven por el texto
# visible del boton, no por su posicion, porque muchos llevan un icono adelante.
def _wa(msg):
    return lambda: (shell.wa(msg), True)


DESTINOS = [
    ("ver catálogo de productos", "productos.html"), ("ver los 21 productos", "productos.html"),
    ("ver la línea", "productos.html"), ("ver el catálogo", "productos.html"),
    ("ver los 9 de cadera", "productos.html#cadera"), ("catálogo", "productos.html"),
    ("cómo trabajamos", "proceso.html"), ("ver el proceso completo", "proceso.html"),
    ("ver sedes", "contacto.html"), ("coordinar una cirugía", "contacto.html"),
    ("consultar este producto", "contacto.html"), ("consultar", "contacto.html"),
    ("registrarme como médico", "contacto.html?q=medico"), ("registro médico", "educacion.html"),
    ("ingresar", "educacion.html"), ("ya tengo cuenta", "educacion.html"),
    ("técnica quirúrgica (médicos)", "educacion.html"),
    ("políticas de privacidad", "privacidad.html"),
    ("cadera", "productos.html#cadera"), ("rodilla", "productos.html#rodilla"),
    ("cementos", "productos.html#cementos"), ("representaciones", "representaciones.html"),
    ("link-ortho", "representaciones.html"), ("advita", "representaciones.html"),
    ("heraeus", "representaciones.html"),
]

WHATSAPP = {
    "escribir por whatsapp": "Hola, quisiera hacer una consulta sobre sus implantes.",
    "consultar por whatsapp": "Hola, queria consultar disponibilidad y medidas de un producto del catalogo.",
    "abrir whatsapp": "Hola, necesito coordinar un implante para una cirugia en las proximas 48 horas.",
    "whatsapp": "Hola, quisiera hacer una consulta sobre sus implantes.",
}


def rutear_botones(cuerpo):
    def resolver(m):
        attrs, interior = m.group(1), m.group(2)
        txt = re.sub(r"<[^>]+>", " ", interior)
        txt = re.sub(r"\s+", " ", txt).replace("→", "").replace("&rarr;", "").strip().lower().rstrip(".")
        if not txt:
            return m.group(0)
        for clave, msg in WHATSAPP.items():
            if txt == clave:
                return '<a href="%s" target="_blank" rel="noopener"%s>%s</a>' % (shell.wa(msg), attrs, interior)
        for clave, destino in DESTINOS:
            if txt == clave or txt.startswith(clave + " "):
                return '<a href="%s"%s>%s</a>' % (destino, attrs, interior)
        return m.group(0)
    return re.sub(r'<a href="#"([^>]*)>(.*?)</a>', resolver, cuerpo, flags=re.S)


# --------------------------------------------------------------- armazon comun
MARCA_TOPBAR = "<!-- ================= BARRA SUPERIOR ================= -->"
MARCA_NAV_M  = "<!-- ================= NAVEGACIÓN ================= -->"
MARCA_CTA    = "<!-- ================= CTA FINAL ================= -->"


def poner_armazon(cuerpo, es_main):
    """Una sola barra superior, un solo CTA y un solo pie para todo el sitio."""
    if es_main:
        # el artboard del home trae su propia version de los tres: se sacan y se
        # reemplazan por las de shell.py, que son las que usan las 9 paginas
        i, j = cuerpo.index(MARCA_TOPBAR), cuerpo.index(MARCA_NAV_M)
        cuerpo = cuerpo[:i] + cuerpo[j:]
        k = cuerpo.index(MARCA_CTA)
        cuerpo = cuerpo[:k] + "</div>\n"
        cuerpo = cuerpo.replace(MARCA_NAV_M, MARCA_NAV_M + shell.topbar(), 1)
    else:
        cuerpo = cuerpo.replace("<!-- NAV -->", shell.topbar() + "<!-- NAV -->", 1)
    # destino del enlace "Ir al contenido"
    cuerpo = cuerpo.replace('</div>\n<div class="drawer"', '</div>\n<span id="contenido" tabindex="-1"></span>\n<div class="drawer"', 1)
    if 'id="contenido"' not in cuerpo:
        cuerpo = cuerpo.replace('<div class="drawer"', '<span id="contenido" tabindex="-1"></span><div class="drawer"', 1)
    return cuerpo + shell.pie()


def add_burger(cuerpo, oscuro=False):
    """Inserta el boton de menu y el cajon movil despues de la barra de navegacion."""
    d = " dark" if oscuro else ""
    stroke = "#C6D0D4" if oscuro else "#10222A"
    items = "".join('<a href="%s">%s</a>' % (h, t) for t, h in NAV)
    burger = ('<span class="burger%s" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">'
              '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="2" '
              'stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"></path></svg></span>' % (d, stroke))
    drawer = '<div class="drawer%s" id="drawer">%s</div>' % (d, items)
    # el burger va justo antes del boton Consultar de la barra
    cuerpo = cuerpo.replace('<a href="#" class="btn-p" style="display: inline-flex; align-items: center; gap: 9px;'
                            ' background: %s; color: #fff; font-size: 13.5px;' % ACCENT,
                            burger + '<a href="contacto.html" class="btn-p navcta" style="display: inline-flex;'
                            ' align-items: center; gap: 9px; background: %s; color: #fff; font-size: 13.5px;' % ACCENT, 1)
    # el cajon va JUSTO DEBAJO de la barra de navegacion: se ancla en el boton
    # Consultar de la barra y se cierran sus dos contenedores.
    i = cuerpo.find('class="btn-p navcta"')
    if i == -1:
        return cuerpo
    m = re.compile(r'</div>\s*</div>').search(cuerpo, i)
    if m:
        cuerpo = cuerpo[:m.end()] + "\n" + drawer + cuerpo[m.end():]
    return cuerpo


def raiz_fluida(cuerpo):
    cuerpo = cuerpo.replace('<div style="width: 1440px; background: #FFFFFF; overflow: hidden;">',
                            '<div style="width: 100%; background: #FFFFFF; overflow: hidden;">')
    cuerpo = cuerpo.replace('<div style="width: 1440px; background: #FFFFFF;">',
                            '<div style="width: 100%; background: #FFFFFF;">')
    cuerpo = cuerpo.replace('<div style="width: 1440px; background: #0A171D;">',
                            '<div style="width: 100%; background: #0A171D;">')
    return cuerpo


def marcar(cuerpo):
    """Clases utilitarias para las reglas responsive."""
    # la barra pasa de seis a siete items: se achica la separacion antes de
    # etiquetar el contenedor, para que el selector siga siendo uno solo
    cuerpo = cuerpo.replace('<div style="display: flex; align-items: center; gap: 34px; font-size: 14px;',
                            '<div style="display: flex; align-items: center; gap: 26px; font-size: 14px;')
    cuerpo = cuerpo.replace('<div style="display: flex; align-items: center; gap: 26px; font-size: 14px;',
                            '<div class="navlinks" style="display: flex; align-items: center; gap: 26px; font-size: 14px;')
    cuerpo = cuerpo.replace('padding: 0 40px; display: flex; align-items: center; justify-content: space-between; gap: 48px;',
                            'padding: 0 40px; display: flex; align-items: center; justify-content: space-between; gap: 48px;" class="ctarow')
    cuerpo = cuerpo.replace('<div style="display: flex; align-items: center; gap: 14px;">\n          <a href="#" class="btn-p"',
                            '<div class="btnrow" style="display: flex; align-items: center; gap: 14px;">\n          <a href="#" class="btn-p"')
    cuerpo = cuerpo.replace('padding: 18px 40px; display: flex; align-items: center; justify-content: space-between; gap: 24px;',
                            'padding: 18px 40px; display: flex; align-items: center; justify-content: space-between; gap: 24px;" class="filtbar')
    cuerpo = cuerpo.replace('padding: 0 40px; display: flex; align-items: center; gap: 16px;',
                            'padding: 0 40px; display: flex; align-items: center; gap: 16px;" class="paisbar')
    return cuerpo


# ---------------------------------------------------------------- interactivos
JS_PRODUCTOS = """
(function(){
  var chips  = document.querySelectorAll('[data-filter]');
  var marcas = document.querySelectorAll('[data-marca-f]');
  var grupos = document.querySelectorAll('[data-grupo]');
  var cards  = document.querySelectorAll('.pc');
  var vacio  = document.getElementById('sinResultados');
  var linea = 'todos', marca = 'todas';

  var ON  = 'font-size:13px;font-weight:600;color:#FFFFFF;border:1px solid #0095A1;background:#0095A1;padding:9px 16px;border-radius:99px;cursor:pointer;';
  var OFF = 'font-size:13px;font-weight:500;color:#10222A;border:1px solid #E3E7E9;background:#FFFFFF;padding:9px 16px;border-radius:99px;cursor:pointer;';
  var MON = 'font-size:13px;font-weight:600;color:#0095A1;border:1px solid #0095A1;background:rgba(0,149,161,.08);padding:8px 14px;border-radius:99px;cursor:pointer;';
  var MOFF= 'font-size:13px;font-weight:500;color:#5A6570;border:1px solid #E3E7E9;background:#FFFFFF;padding:8px 14px;border-radius:99px;cursor:pointer;';

  function pintar(){
    var total = 0;
    cards.forEach(function(c){
      var ok = (linea === 'todos' || c.getAttribute('data-linea') === linea)
            && (marca === 'todas' || c.getAttribute('data-marca') === marca);
      c.style.display = ok ? '' : 'none';
      if (ok) total++;
    });
    // un grupo de línea desaparece si se quedó sin tarjetas visibles
    grupos.forEach(function(g){
      var vis = 0;
      g.querySelectorAll('.pc').forEach(function(c){ if (c.style.display !== 'none') vis++; });
      g.style.display = vis ? '' : 'none';
      var n = g.querySelector('[data-cuenta]');
      if (n) n.textContent = vis + (vis === 1 ? ' producto' : ' productos');
    });
    chips.forEach(function(c){
      c.style.cssText = (c.getAttribute('data-filter') === linea) ? ON : OFF;
    });
    marcas.forEach(function(c){
      c.style.cssText = (c.getAttribute('data-marca-f') === marca) ? MON : MOFF;
    });
    if (vacio) vacio.style.display = total ? 'none' : '';
  }

  chips.forEach(function(c){ c.addEventListener('click', function(){
    linea = c.getAttribute('data-filter'); pintar(); }); });
  marcas.forEach(function(c){ c.addEventListener('click', function(){
    var v = c.getAttribute('data-marca-f');
    marca = (marca === v && v !== 'todas') ? 'todas' : v;   // volver a tocar la marca activa la saca
    pintar(); }); });

  // permite entrar directo a una línea desde el pie: productos.html#rodilla
  var h = (location.hash || '').replace('#', '');
  if (['cadera','rodilla','cementos'].indexOf(h) >= 0) linea = h;
  pintar();
})();
"""

JS_FICHA = """
(function(){
  var obj = document.getElementById('obj');
  var ang = -22, zoom = 1;
  function pintar(){
    obj.style.transform = 'rotateY(' + ang + 'deg) rotateX(6deg) scale(' + zoom + ')';
    document.getElementById('angTxt').textContent = 'Rotación ' + (((ang % 360) + 360) % 360) + '°';
    document.getElementById('zoomTxt').textContent = Math.round(zoom * 100) + '%';
  }
  document.getElementById('rotL').addEventListener('click', function(){ ang -= 45; pintar(); });
  document.getElementById('rotR').addEventListener('click', function(){ ang += 45; pintar(); });
  document.getElementById('zoomB').addEventListener('click', function(){ zoom = zoom >= 1.5 ? 0.85 : zoom + 0.25; pintar(); });
  document.getElementById('resetB').addEventListener('click', function(){ ang = -22; zoom = 1; pintar(); });
  var arrastre = false, x0 = 0, a0 = 0;
  var stage = document.querySelector('.viewer');
  stage.addEventListener('pointerdown', function(e){ arrastre = true; x0 = e.clientX; a0 = ang; obj.style.transition = 'none'; });
  window.addEventListener('pointermove', function(e){ if(!arrastre) return; ang = a0 + (e.clientX - x0) * 0.6; pintar(); });
  window.addEventListener('pointerup', function(){ if(!arrastre) return; arrastre = false; obj.style.transition = ''; });
  pintar();
})();
"""

JS_CONTACTO = """
(function(){
  var TEL = '__TEL__';
  var MAPA_BA  = '__MAPA_BA__',  LINK_BA  = 'https://www.openstreetmap.org/?mlat=-34.6116&mlon=-58.3847#map=17/-34.6116/-58.3847';
  var MAPA_ROS = '__MAPA_ROS__', LINK_ROS = 'https://www.openstreetmap.org/?mlat=-32.9473&mlon=-60.6398#map=17/-32.9473/-60.6398';

  var P = {
    ar: { s1:['Sede Buenos Aires','Casa central','Av. Belgrano 863, CABA', TEL],
          s2:['Sede Rosario','Rosario, Santa Fe','Pte. Roca 782, piso 1, Rosario', TEL],
          tel:'+54 9 11 0000-0000', mapa: MAPA_BA, link: LINK_BA },
    cl: { s1:['Chile','Atención desde casa central','Las consultas desde Chile las toma el equipo comercial en Buenos Aires.', TEL],
          s2:['Chile','Cómo trabajamos allá','Coordinamos la entrega y el acompañamiento técnico con el centro de salud para cada cirugía.', TEL],
          tel:'+56 9 0000 0000', mapa: MAPA_BA, link: LINK_BA },
    uy: { s1:['Uruguay','Atención desde casa central','Las consultas desde Uruguay las toma el equipo comercial en Buenos Aires.', TEL],
          s2:['Uruguay','Cómo trabajamos allá','Coordinamos la entrega y el acompañamiento técnico con el centro de salud para cada cirugía.', TEL],
          tel:'+598 00 000 000', mapa: MAPA_BA, link: LINK_BA }
  };
  var Q = {
    medico:['Médico','Matrícula profesional','MN / MP','Contanos qué producto necesitás, para qué fecha está programada la cirugía y en qué centro.'],
    financiador:['Obra social / prepaga','Institución','Nombre de la institución','Contanos si necesitás un presupuesto, documentación de trazabilidad o avanzar con un convenio.'],
    paciente:['Paciente','Centro donde te operás','Nombre del centro u hospital','Contanos qué implante te indicaron y quién es tu médico tratante.']
  };
  var pais = 'ar', quien = 'medico';
  function set(id, txt){ var e = document.getElementById(id); if(e) e.textContent = txt; }
  function pintar(){
    document.querySelectorAll('[data-pais]').forEach(function(c){
      var on = c.getAttribute('data-pais') === pais;
      c.style.cssText = on
        ? 'font-size:13.5px;font-weight:600;color:#FFFFFF;border:1px solid #0095A1;background:#0095A1;padding:10px 20px;border-radius:99px;cursor:pointer;'
        : 'font-size:13.5px;font-weight:500;color:#10222A;border:1px solid #DDE3E5;background:#FFFFFF;padding:10px 20px;border-radius:99px;cursor:pointer;';
    });
    document.querySelectorAll('[data-quien]').forEach(function(c){
      var on = c.getAttribute('data-quien') === quien;
      var card = c.querySelector('.who-in'), ic = c.querySelector('.who-ic');
      var base = 'border-radius:6px;padding:30px 28px;display:flex;flex-direction:column;gap:13px;height:100%;';
      card.style.cssText = base + (on
        ? 'background:#FFFFFF;border:2px solid #0095A1;box-shadow:0 16px 30px -18px rgba(0,149,161,.6);'
        : 'background:#FFFFFF;border:1px solid #E3E7E9;');
      var ib = 'width:46px;height:46px;border-radius:6px;display:flex;align-items:center;justify-content:center;';
      ic.style.cssText = ib + (on ? 'background:#0095A1;color:#FFFFFF;' : 'background:rgba(0,149,161,.09);color:#0095A1;');
    });
    var p = P[pais], q = Q[quien];
    set('quienTxt', q[0]); set('campo2', q[1]);
    set('sede1Tag', p.s1[0]); set('sede1Nom', p.s1[1]); set('sede1Dir', p.s1[2]); set('sede1Tel', p.s1[3]);
    set('sede2Tag', p.s2[0]); set('sede2Nom', p.s2[1]); set('sede2Dir', p.s2[2]); set('sede2Tel', p.s2[3]);
    ph('fCampo2', q[2]); ph('fMsg', q[3]); ph('fTel', p.tel);
    var f = document.getElementById('mapa'), a = document.getElementById('mapaLink');
    if (f && f.getAttribute('src') !== p.mapa) f.setAttribute('src', p.mapa);
    if (a) a.setAttribute('href', p.link);
  }
  function ph(id, txt){ var e = document.getElementById(id); if (e) e.setAttribute('placeholder', txt); }

  // el segundo mapa de Argentina: al tocar la tarjeta de Rosario cambia el mapa
  var t2 = document.getElementById('sede2Nom');
  if (t2) {
    var caja2 = t2.closest('div[style*="border-radius: 6px"]');
    if (caja2) {
      caja2.style.cursor = 'pointer';
      caja2.addEventListener('click', function(){
        if (pais !== 'ar') return;
        var f = document.getElementById('mapa'), a = document.getElementById('mapaLink');
        if (f) f.setAttribute('src', MAPA_ROS);
        if (a) a.setAttribute('href', LINK_ROS);
      });
    }
  }
  document.querySelectorAll('[data-pais]').forEach(function(c){
    c.addEventListener('click', function(){ pais = c.getAttribute('data-pais'); pintar(); }); });
  document.querySelectorAll('[data-quien]').forEach(function(c){
    c.addEventListener('click', function(){ quien = c.getAttribute('data-quien'); pintar(); }); });
  pintar();

  // ---- envio: arma el mensaje y abre WhatsApp con la consulta ya escrita
  var PAIS_TXT = { ar: 'Argentina', cl: 'Chile', uy: 'Uruguay' };
  var form = document.getElementById('formConsulta');
  var err  = document.getElementById('formError');
  function marcar(el, mal){ if (el) el.classList[mal ? 'add' : 'remove']('mal'); }
  function fallar(msg, el){
    if (err) { err.textContent = msg; err.style.display = ''; }
    if (el) { marcar(el, true); el.focus(); }
    return false;
  }
  if (form) form.addEventListener('submit', function(e){
    e.preventDefault();
    var g = function(id){ return (document.getElementById(id).value || '').trim(); };
    ['fNombre','fMail','fTel','fMsg'].forEach(function(i){ marcar(document.getElementById(i), false); });
    if (err) err.style.display = 'none';

    if (!g('fNombre')) return fallar('Escribinos tu nombre para saber con quién hablamos.', document.getElementById('fNombre'));
    if (!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]{2,}$/.test(g('fMail')))
      return fallar('Revisá el e-mail: no parece una dirección válida.', document.getElementById('fMail'));
    if (g('fTel').replace(/[^0-9]/g, '').length < 8)
      return fallar('Dejanos un teléfono con característica para poder responderte.', document.getElementById('fTel'));
    if (!g('fMsg')) return fallar('Contanos brevemente qué necesitás.', document.getElementById('fMsg'));
    if (!document.getElementById('fOk').checked)
      return fallar('Necesitamos que aceptes las políticas de privacidad para poder contactarte.');

    var q = Q[quien], extra = g('fCampo2');
    var t = 'Consulta desde la web de Swiss Protech'
          + '\\n\\nSoy: ' + q[0]
          + '\\nPaís: ' + PAIS_TXT[pais]
          + '\\nNombre: ' + g('fNombre')
          + (extra ? '\\n' + q[1] + ': ' + extra : '')
          + '\\nE-mail: ' + g('fMail')
          + '\\nTeléfono: ' + g('fTel')
          + '\\n\\n' + g('fMsg');
    window.open('https://wa.me/__WA__?text=' + encodeURIComponent(t), '_blank', 'noopener');
  });
})();
"""


JS_MAIN = """
(function () {
  var bucle  = document.getElementById('filmLoop');
  var entero = document.getElementById('film');
  var boton  = document.getElementById('filmPlay');
  if (!bucle || !entero || !boton) return;

  // Algunos navegadores bloquean incluso el autoplay mudo (modo ahorro de
  // datos, iOS con poca bateria). Si el bucle no arranca, se queda el poster:
  // el boton sigue siendo la unica via de entrada, asi que nada se rompe.
  var arranque = bucle.play();
  if (arranque && arranque.catch) arranque.catch(function () {});

  boton.addEventListener('click', function () {
    boton.hidden = true;
    bucle.pause();
    bucle.hidden = true;
    entero.hidden = false;
    entero.controls = true;
    entero.currentTime = 0;
    var p = entero.play();
    if (p && p.catch) p.catch(function () { entero.controls = true; });
    entero.focus({ preventScroll: true });
  });

  // al terminar la pieza vuelve el bucle, para que el bloque no quede en negro
  entero.addEventListener('ended', function () {
    entero.controls = false;
    entero.hidden = true;
    bucle.hidden = false;
    boton.hidden = false;
    var p = bucle.play();
    if (p && p.catch) p.catch(function () {});
  });
})();
"""




def transformar_main(c):
    return c


# orden real de las tarjetas en Productos.dc.html
SLUGS = [
    "mobilelink-dual-mobility", "crown-cup", "lubinus-cup", "lubinus-spii", "mp-link",
    "element", "mobilelink", "bimobile", "lcu",
    "optetrak-logic", "optetrak-hiflex", "optetrak-cc", "uni-sled",
    "endomodel-modular", "endomodel-hinged", "endomodel-standard",
    "copal", "palacos-mv", "palacos-r", "palamix-gun", "palamix-uno",
]


def transformar_productos(c):
    P = cargar_productos()

    c = re.sub(r'<sc-if value="\{\{show(\w+)\}\}"[^>]*>',
               lambda m: '<div data-grupo="%s" id="%s">' % (m.group(1).lower(), m.group(1).lower()), c)
    c = c.replace("</sc-if>", "</div>")
    for cat in ["todos", "cadera", "rodilla", "cementos"]:
        c = c.replace('onClick="{{ver%s}}" style="{{s%s}}"' % (cat.capitalize(), cat.capitalize()),
                      'data-filter="%s"' % cat)

    # el contador de cada grupo lo recalcula el JS al filtrar
    c = re.sub(r'<span style="font-size: 13.5px; color: #69727D;">(\d+) productos</span>',
               lambda m: '<span data-cuenta style="font-size: 13.5px; color: #69727D;">%s productos</span>' % m.group(1), c)

    # cada tarjeta lleva a su ficha y declara línea y marca para el filtro
    it = iter(SLUGS)
    def abrir(_m):
        s = next(it)
        p = P[s]
        return ('<a class="pc" href="producto.html?p=%s" data-linea="%s" data-marca="%s">'
                % (s, p["linea"].lower(), marca_corta(p["marca"])[0]))
    c = re.sub(r'<div class="pc">', abrir, c)
    c = c.replace("</div></div>", "</div></a>")

    # el rótulo "Línea · MARCA" sale del catálogo, no del maquetado: así no se
    # puede volver a desincronizar de js/productos.js
    it2 = iter(SLUGS)
    def rotulo(m):
        p = P[next(it2)]
        return '%s%s · %s</span>' % (m.group(1), p["linea"], marca_corta(p["marca"])[1])
    c = re.sub(r'(<span style="font-size: 10\.5px; font-weight: 700; letter-spacing: \.13em; '
               r'text-transform: uppercase; color: #0095A1;">)[^<]*</span>', rotulo, c)

    # barra de marcas: de texto decorativo a filtro real
    c = re.sub(r'<span style="font-size: 12px; font-weight: 700; letter-spacing: \.12em; text-transform: uppercase; color: #A7A9AC;">Marca</span>.*?(?=</div>\s*</div>\s*</div>)',
               MARCAS_HTML, c, flags=re.S)

    # que decir cuando el cruce de filtros no deja nada
    c = c.replace("<!-- AYUDA -->", VACIO_HTML + "<!-- AYUDA -->", 1)
    return c


VACIO_HTML = """
<div id="sinResultados" style="display: none; background: #FFFFFF; border: 1px solid #E3E7E9; border-radius: 6px; padding: 44px 40px; text-align: center;">
  <h3 style="font-size: 19px; color: #10222A; margin-bottom: 8px;">No hay productos con esa combinación</h3>
  <p style="font-size: 14px; color: #69727D; line-height: 1.6;">Esa marca no tiene productos en la línea elegida. Probá con otra línea o mirá el catálogo completo.</p>
</div>
"""


MARCAS_HTML = (
    '<span style="font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: #A7A9AC;">Marca</span>'
    '<span class="mlink" data-marca-f="todas">Todas</span>'
    '<span class="mlink" data-marca-f="link">LINK</span>'
    '<span class="mlink" data-marca-f="advita">Advita</span>'
    '<span class="mlink" data-marca-f="heraeus">Heraeus</span>'
)


def transformar_ficha(c):
    c = c.replace('<div class="obj" style="{{objTf}}">', '<div class="obj" id="obj">')
    c = c.replace('onClick="{{girarIzq}}"', 'id="rotL"').replace('onClick="{{girarDer}}"', 'id="rotR"')
    c = c.replace('onClick="{{acercar}}"', 'id="zoomB"').replace('onClick="{{reset}}"', 'id="resetB"')
    c = c.replace("{{zoomTxt}}", '<span id="zoomTxt">100%</span>')
    c = c.replace("{{angTxt}}", '<span id="angTxt">Rotación 338°</span>')
    return c


def transformar_contacto(c):
    for k in ["ar", "cl", "uy"]:
        c = c.replace('onClick="{{ver%s}}" style="{{s%s}}"' % (k.capitalize(), k.capitalize()),
                      'class="flag" data-pais="%s"' % k)
    mapa = [("soyMedico", "cMedico", "iMedico", "medico"),
            ("soyFin", "cFin", "iFin", "financiador"),
            ("soyPac", "cPac", "iPac", "paciente")]
    for h, card, icon, val in mapa:
        c = c.replace('<div class="who" onClick="{{%s}}"><div class="who-in" style="{{%s}}">' % (h, card),
                      '<div class="who" data-quien="%s"><div class="who-in">' % val)
        c = c.replace('<span style="{{%s}}">' % icon, '<span class="who-ic">')
    # estos tres viven dentro de atributos placeholder="": los completa el JS
    for hid in ["campo2ph", "msgPh", "telPh"]:
        c = c.replace("{{%s}}" % hid, "")
    for hid in ["quienTxt", "campo2",
                "sede1Tag", "sede1Nom", "sede1Dir", "sede1Tel",
                "sede2Tag", "sede2Nom", "sede2Dir", "sede2Tel"]:
        c = c.replace("{{%s}}" % hid, '<span id="%s"></span>' % hid)
    return c


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
__META__
<script type="importmap">{ "imports": { "three": "./vendor/three.module.js" } }</script>
__LINKS__
<style>
__CSS__
__BURGER__
__SHELL__
__RESP__
</style>
__LD__
</head>
<body>
<a href="#contenido" class="sr-skip">Ir al contenido</a>
__BODY__
<script>
document.addEventListener('click', function(e){
  var d = document.getElementById('drawer');
  if (d && d.classList.contains('open') && !e.target.closest('.drawer') && !e.target.closest('.burger')) d.classList.remove('open');
});
</script>
__JS__
<script>__MOV__</script>
</body>
</html>
"""

LEGIBILIDAD_CSS = """
/* ---- navegacion: siete items no pueden partirse en dos renglones ---- */
.navlinks a { white-space: nowrap; }
@media (max-width: 1330px) { .navlinks { gap: 20px !important; font-size: 13.5px !important; } }

/* ---- ritmo y legibilidad ----
   El maquetado venia con cuerpos de 12,5-13,5 px y lineas de hasta 75 caracteres.
   Se sube el cuerpo, se abre el interlineado y se acota la medida: es un sitio que
   leen medicos y administrativos, no un folleto. */
body { font-size: 16px; line-height: 1.6; color: #10222A; text-rendering: optimizeLegibility; }
p { text-wrap: pretty; }
h1, h2, h3 { text-wrap: balance; }

/* parrafos de tarjeta y de bajada: piso de 14,5 px */
[style*="font-size: 12.5px"]:not(.sp-foot *):not([class*="crumb"]) { font-size: 13.5px !important; }
[style*="font-size: 13px; color: #69727D"] { font-size: 14.5px !important; line-height: 1.65 !important; }
[style*="font-size: 14px; color: #69727D"] { font-size: 15px !important; line-height: 1.68 !important; }
[style*="font-size: 15.5px; color: #69727D"] { font-size: 16.5px !important; line-height: 1.7 !important; }
[style*="font-size: 15px; color: #69727D"] { font-size: 15.5px !important; line-height: 1.68 !important; }

/* titulos de seccion con mas presencia y menos ruido */
h2[style*="font-size: 27px"] { font-size: 30px !important; }
h2[style*="font-size: 32px"] { font-size: 34px !important; }
h2[style*="font-size: 34px"] { letter-spacing: -0.035em !important; }

/* medida de lectura: ninguna columna de texto arriba de 68 caracteres */
p[style*="max-width: 60ch"], p[style*="max-width: 64ch"] { max-width: 62ch !important; }

/* separacion vertical mas pareja entre secciones */
[style*="padding: 90px 0"] { padding: 96px 0 !important; }
[style*="padding: 86px 0 78px"] { padding: 96px 0 !important; }

/* enlaces de texto: subrayado al pasar, para que se lean como enlaces */
a[style*="color: #0095A1"]:hover { text-decoration: underline; text-underline-offset: 3px; }

@media (max-width: 720px) {
  body { font-size: 15.5px; }
  h1 { letter-spacing: -0.03em !important; }
}
"""

A11Y_CSS = """
.sr-skip { position: absolute; left: -9999px; top: 0; z-index: 99; background: #0095A1; color: #fff;
           padding: 12px 20px; font-size: 14px; font-weight: 600; border-radius: 0 0 4px 0; }
.sr-skip:focus { left: 0; }
a:focus-visible, button:focus-visible, [tabindex]:focus-visible, .fbtn:focus-visible, .mlink:focus-visible {
  outline: 3px solid #0095A1; outline-offset: 2px; border-radius: 3px; }
.fbtn, .mlink { cursor: pointer; user-select: none; }
@media (max-width: 720px) { .fbtn, .mlink { min-height: 40px; display: inline-flex; align-items: center; } }
@media (prefers-reduced-motion: reduce) { * { animation-duration: .01ms !important; transition-duration: .01ms !important; } html { scroll-behavior: auto; } }
"""


FICHA_CSS = """
.creditos { margin: 0; padding: 26px 0 34px; background: #FFFFFF; border-top: 1px solid #E3E7E9; }
.creditos .wrap { display: block; font-size: 12.5px; color: #8A929A; }
""" + A11Y_CSS


def parchar_ficha():
    """producto.html se mantiene a mano; el armazon se le inyecta entre marcas.
    Es idempotente: se puede volver a correr el build sin duplicar nada."""
    ruta = os.path.join(SRC, "producto.html")
    t = open(ruta, encoding="utf-8").read()

    bloques = {
        "META": shell.meta("Ficha de producto — Swiss Protech",
                           "Cada implante de Swiss Protech con su ficha: especificaciones, material del "
                           "fabricante, técnica quirúrgica y consulta directa.", "producto.html")
                + "\n" + shell.jsonld_migas([("Home", "index.html"), ("Productos", "productos.html")]),
        "CSS":    shell.CSS + FICHA_CSS,
        "TOPBAR": shell.topbar(),
        "PIE":    shell.pie(),
    }
    for nombre, contenido in bloques.items():
        abre, cierra = ("/* SHELL:%s */" % nombre, "/* /SHELL:%s */" % nombre) if nombre == "CSS" \
                       else ("<!-- SHELL:%s -->" % nombre, "<!-- /SHELL:%s -->" % nombre)
        i, j = t.index(abre), t.index(cierra)
        t = t[:i + len(abre)] + "\n" + contenido + "\n" + t[j:]

    open(ruta, "w", encoding="utf-8").write(t)
    shutil.copyfile(ruta, os.path.join(OUT, "producto.html"))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"))

    extras = {"Main.dc.html": JS_MAIN, "Productos.dc.html": JS_PRODUCTOS,
              "Ficha.dc.html": JS_FICHA, "Contacto.dc.html": JS_CONTACTO}
    trans = {"Main.dc.html": transformar_main, "Productos.dc.html": transformar_productos,
             "Ficha.dc.html": transformar_ficha, "Contacto.dc.html": transformar_contacto}

    for src, dst, title, desc in PAGES:
        css, links, cuerpo = extraer(leer(src))
        # el color de marca tambien se resuelve en el CSS del helmet, no solo en
        # el cuerpo: si no, una regla con {{accent}} queda invalida y no pinta
        css = css.replace("{{accent}}", ACCENT)
        cuerpo = cuerpo.replace("{{accent}}", ACCENT).replace("{{ringCls}}", "")
        if src in trans:
            cuerpo = trans[src](cuerpo)
        cuerpo = raiz_fluida(cuerpo)
        cuerpo = marcar(cuerpo)
        cuerpo = wire_nav(cuerpo, dst)
        cuerpo = add_burger(cuerpo)
        cuerpo = cuerpo.replace('src="', 'src="assets/').replace('src="assets/https', 'src="https')
        cuerpo = cuerpo.replace('src="assets/media/', 'src="media/')
        cuerpo = cuerpo.replace('poster="', 'poster="assets/')
        # el srcset lleva varias rutas y no lo alcanza el reemplazo de arriba
        cuerpo = re.sub(r'srcset="([^"]+)"',
                        lambda m: 'srcset="%s"' % ", ".join(
                            (t if t.startswith(("http", "assets/")) else "assets/" + t)
                            for t in (x.strip() for x in m.group(1).split(","))),
                        cuerpo)
        # botones que deben ir a una pagina real
        cuerpo = rutear_botones(cuerpo)
        cuerpo = cuerpo.replace('>Ver los 21 productos', ' data-go>Ver los 21 productos')
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Ver catálogo de productos|Ver los 21 productos|Ver la línea|Ver el catálogo|Ver los 9 de cadera)',
                        lambda m: '<a href="productos.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Cómo trabajamos|Ver el proceso completo)',
                        lambda m: '<a href="proceso.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Ver sedes|Coordinar una cirugía|Consultar este producto)',
                        lambda m: '<a href="contacto.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        # todo lo que dice WhatsApp abre WhatsApp de verdad
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Escribir por WhatsApp|Consultar por WhatsApp)',
                        lambda m: '<a href="%s" target="_blank" rel="noopener"%s>%s%s'
                        % (shell.WA_CATALOGO, m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Abrir WhatsApp)',
                        lambda m: '<a href="%s" target="_blank" rel="noopener"%s>%s%s'
                        % (shell.WA_URGENTE, m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = cuerpo.replace('<a href="#" data-wa',
                                '<a href="%s" target="_blank" rel="noopener" data-wa' % shell.WA_GENERAL)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Ver la línea|Ver los 21 productos)',
                        lambda m: '<a href="productos.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Registrarme como médico|Ya tengo cuenta|Registro médico|Ingresar)',
                        lambda m: '<a href="educacion.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(link-ortho|advita|heraeus)',
                        lambda m: '<a href="representaciones.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = cuerpo.replace('<a href="#" style="font-size: 13.5px; color: #A7A9AC;">Cadera</a>', '<a href="productos.html" style="font-size: 13.5px; color: #A7A9AC;">Cadera</a>')
        cuerpo = cuerpo.replace('<a href="#" style="font-size: 13.5px; color: #A7A9AC;">Rodilla</a>', '<a href="productos.html" style="font-size: 13.5px; color: #A7A9AC;">Rodilla</a>')
        cuerpo = cuerpo.replace('<a href="#" style="font-size: 13.5px; color: #A7A9AC;">Cementos</a>', '<a href="productos.html" style="font-size: 13.5px; color: #A7A9AC;">Cementos</a>')
        cuerpo = cuerpo.replace('<a href="#" style="font-size: 13.5px; color: #A7A9AC;">Representaciones</a>', '<a href="representaciones.html" style="font-size: 13.5px; color: #A7A9AC;">Representaciones</a>')
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)Ver ficha', lambda m: '<a href="producto.html"%s>%sVer ficha' % (m.group(1), m.group(2)), cuerpo)
        cuerpo = cuerpo.replace('<a href="#">políticas de privacidad</a>',
                                '<a href="privacidad.html">políticas de privacidad</a>')

        cuerpo = poner_armazon(cuerpo, src == "Main.dc.html")

        ld = shell.jsonld_migas(MIGAS[dst])
        if dst == "index.html":
            ld = shell.jsonld_organizacion() + ld

        js = extras.get(src, "")
        js = (js.replace("__WA__", shell.WA_NUMERO)
                .replace("__TEL__", shell.TEL_DISPLAY)
                .replace("__MAPA_BA__", shell.SEDES[0]["mapa"])
                .replace("__MAPA_ROS__", shell.SEDES[1]["mapa"]))

        html = (PLANTILLA
                .replace("__META__", shell.meta(title, desc, dst))
                .replace("__LINKS__", links).replace("__CSS__", css)
                .replace("__BURGER__", BURGER_CSS + HERO3D_CSS + A11Y_CSS + LEGIBILIDAD_CSS)
                .replace("__SHELL__", shell.CSS).replace("__RESP__", RESPONSIVE)
                .replace("__LD__", ld)
                .replace("__BODY__", cuerpo)
                .replace("__MOV__", shell.MOVIMIENTO_JS)
                .replace("__JS__", "<script>%s</script>" % js if js else ""))
        with open(os.path.join(OUT, dst), "w", encoding="utf-8") as f:
            f.write(html)

    parchar_ficha()

    quedan, pendientes = [], []
    for _, dst, _, _ in PAGES:
        t = open(os.path.join(OUT, dst), encoding="utf-8").read()
        h = re.findall(r"\{\{[^}]+\}\}", t)
        if h:
            quedan.append((dst, sorted(set(h))))
        if "[COMPLETAR" in t.upper():
            pendientes.append(dst)
        # las paginas se publican desde la raiz: se copian solas
        shutil.copyfile(os.path.join(OUT, dst), os.path.join(SRC, dst))

    armar_publicable()

    print("paginas:", ", ".join(d for _, d, _, _ in PAGES))
    print("holes sin resolver:", quedan if quedan else "ninguno")
    print("marcadores [COMPLETAR]:", pendientes if pendientes else "ninguno")


# Lo que hay que subir al hosting. Antes site/ quedaba con cinco paginas y sin
# media/: abrirla desde ahi mostraba el sitio a medias (video roto, visor 3D
# sin cargar, media navegacion en 404).
PUBLICAR_HTML = ["index.html", "productos.html", "producto.html", "proceso.html",
                 "institucional.html", "representaciones.html", "educacion.html",
                 "multimedia.html", "contacto.html", "privacidad.html"]
PUBLICAR_DIRS = ["assets", "js", "vendor"]
PUBLICAR_MEDIA = ["clips", "gifs", "stills", "views"]      # lo que referencia el sitio
PUBLICAR_SUELTOS = ["sitemap.xml", "robots.txt", "media/swiss-protech.mp4"]


def armar_publicable():
    """Deja site/ como una copia completa y navegable, lista para subir."""
    for d in PUBLICAR_DIRS:
        org, dst = os.path.join(SRC, d), os.path.join(OUT, d)
        if os.path.isdir(org):
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(org, dst)
    for d in PUBLICAR_MEDIA:
        org, dst = os.path.join(SRC, "media", d), os.path.join(OUT, "media", d)
        if os.path.isdir(org):
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(org, dst)
    for f in PUBLICAR_HTML + PUBLICAR_SUELTOS:
        org, dst = os.path.join(SRC, f), os.path.join(OUT, f)
        if os.path.exists(org):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(org, dst)

    # nada de lo que pide una pagina puede faltar en la copia
    rotas = []
    for f in PUBLICAR_HTML:
        p = os.path.join(OUT, f)
        if not os.path.exists(p):
            rotas.append((f, "FALTA LA PAGINA"))
            continue
        t = open(p, encoding="utf-8").read()
        for ref in set(re.findall(r'(?:src|href|poster)="((?:assets|media|js|vendor)/[^"]+)"', t)):
            if not os.path.exists(os.path.join(OUT, ref)):
                rotas.append((f, ref))
    print("site/ publicable:", len(PUBLICAR_HTML), "paginas |",
          "referencias rotas:", rotas if rotas else "ninguna")


if __name__ == "__main__":
    main()
