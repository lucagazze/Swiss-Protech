# -*- coding: utf-8 -*-
"""
Convierte los artboards .dc.html en un sitio estatico navegable.
Salida: site/  ->  index.html, productos.html, proceso.html, producto.html,
                   contacto.html, assets/
Ejecutar:  python -u build_site.py
"""
import os, re, shutil

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, "site")
ACCENT = "#0095A1"

PAGES = [
    ("Main.dc.html",      "index.html",     "Swiss Protech — Implantes ortopédicos con trazabilidad de punta a punta",
     "Importadores y representantes exclusivos en Argentina de prótesis de cadera y rodilla de origen alemán y norteamericano. Más de 25 años de trayectoria."),
    ("Productos.dc.html", "productos.html", "Catálogo de productos — Swiss Protech",
     "21 productos entre prótesis de cadera, rodilla y cementos óseos. Marcas Link, Advita Ortho y Heraeus."),
    ("Proceso.dc.html",   "proceso.html",   "Nuestro proceso — Swiss Protech",
     "Las cinco etapas de trazabilidad: depósito, control, esterilización, traslado y entrega en quirófano."),
    ("Ficha.dc.html",     "producto.html",  "MobileLink Dual Mobility — Swiss Protech",
     "Sistema de cotilo no cementado de doble movilidad. Waldemar Link, Hamburgo."),
    ("Contacto.dc.html",  "contacto.html",  "Contacto — Swiss Protech",
     "Sedes en CABA y Rosario. Consultas de médicos, obras sociales, prepagas y pacientes."),
]

NAV = [
    ("Institucional",    "index.html#institucional"),
    ("Productos",        "productos.html"),
    ("Nuestro proceso",  "proceso.html"),
    ("Educación médica", "index.html#portal"),
    ("Representaciones", "index.html#representaciones"),
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
  h1 { font-size: clamp(30px, 6.4vw, 52px) !important; }
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
  .stage { height: 340px !important; }
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
  .stage { height: 380px !important; }
  .shot, .refl, .refl-box { width: 230px !important; }
  .shot { height: 230px !important; }
  .refl { height: 230px !important; }
  .refl-box { height: 88px !important; }
  .orbit.o1 { width: 300px !important; height: 300px !important; margin: -150px 0 0 -150px !important; }
  .orbit.o2 { display: none !important; }
  .floor { width: 320px !important; margin-left: -160px !important; }
  .thumb { width: 48px !important; height: 48px !important; }
  [style*="align-items: center; justify-content: space-between; gap: 26px"] {
    flex-direction: column !important; align-items: flex-start !important; gap: 18px !important; }
}
"""

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
    for texto, href in NAV:
        cuerpo = re.sub(
            r'<a href="#"(\s+class="navlink"[^>]*)>(\s*)' + re.escape(texto) + r'(\s*)</a>',
            lambda m, h=href, t=texto: '<a href="%s"%s>%s</a>' % (h, m.group(1), t),
            cuerpo)
    return cuerpo


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
    cuerpo = cuerpo.replace('<div style="display: flex; align-items: center; gap: 34px;',
                            '<div class="navlinks" style="display: flex; align-items: center; gap: 34px;')
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
  var chips = document.querySelectorAll('[data-filter]');
  var grupos = document.querySelectorAll('[data-grupo]');
  function pintar(v){
    chips.forEach(function(c){
      var on = c.getAttribute('data-filter') === v;
      c.style.cssText = on
        ? 'font-size:13px;font-weight:600;color:#FFFFFF;border:1px solid #0095A1;background:#0095A1;padding:9px 16px;border-radius:99px;'
        : 'font-size:13px;font-weight:500;color:#10222A;border:1px solid #E3E7E9;background:#FFFFFF;padding:9px 16px;border-radius:99px;';
    });
    grupos.forEach(function(g){
      g.style.display = (v === 'todos' || g.getAttribute('data-grupo') === v) ? '' : 'none';
    });
  }
  chips.forEach(function(c){ c.addEventListener('click', function(){ pintar(c.getAttribute('data-filter')); }); });
  pintar('todos');
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
  var P = {
    ar: { s1:['Sede Buenos Aires','Casa central','Av. Belgrano 863, CABA','11 3593 5241'],
          s2:['Sede Rosario','Santa Fe','Pte. Roca 782, piso 1, Rosario','11 3593 5241'],
          tel:'+54 9 11 0000-0000' },
    cl: { s1:['Chile','Oficina comercial','[COMPLETAR DIRECCIÓN]','[COMPLETAR TELÉFONO]'],
          s2:['Chile','Cobertura','[COMPLETAR ZONAS DE ENTREGA]','[COMPLETAR WHATSAPP]'],
          tel:'+56 9 0000 0000' },
    uy: { s1:['Uruguay','Oficina comercial','[COMPLETAR DIRECCIÓN]','[COMPLETAR TELÉFONO]'],
          s2:['Uruguay','Cobertura','[COMPLETAR ZONAS DE ENTREGA]','[COMPLETAR WHATSAPP]'],
          tel:'+598 00 000 000' }
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
    set('quienTxt', q[0]); set('campo2', q[1]); set('campo2ph', q[2]); set('msgPh', q[3]); set('telPh', p.tel);
    set('sede1Tag', p.s1[0]); set('sede1Nom', p.s1[1]); set('sede1Dir', p.s1[2]); set('sede1Tel', p.s1[3]);
    set('sede2Tag', p.s2[0]); set('sede2Nom', p.s2[1]); set('sede2Dir', p.s2[2]); set('sede2Tel', p.s2[3]);
  }
  document.querySelectorAll('[data-pais]').forEach(function(c){
    c.addEventListener('click', function(){ pais = c.getAttribute('data-pais'); pintar(); }); });
  document.querySelectorAll('[data-quien]').forEach(function(c){
    c.addEventListener('click', function(){ quien = c.getAttribute('data-quien'); pintar(); }); });
  pintar();
})();
"""


JS_MAIN = """
(function(){
  var HERO = [
    ['Cadera',   'MobileLink Dual Mobility', 'Waldemar Link · Alemania'],
    ['Rodilla',  'Endomodel Modular',        'Waldemar Link · Alemania'],
    ['Cadera',   'Lubinus SPII Revision',    'Waldemar Link · Alemania'],
    ['Rodilla',  'Optetrak Logic',           'Sistema de reemplazo total'],
    ['Cementos', 'Palamix',                  'Heraeus Medical · Alemania']
  ];
  var slots = document.querySelectorAll('.slot');
  var thumbs = document.querySelectorAll('[data-hero]');
  var i = 0, timer = null;
  function pintar(){
    slots.forEach(function(s, k){
      s.style.cssText = (k === i)
        ? 'position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:1;transform:scale(1);'
        : 'position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;transform:scale(.94);pointer-events:none;';
    });
    thumbs.forEach(function(t, k){
      t.style.cssText = 'width:56px;height:56px;border-radius:6px;display:flex;align-items:center;'
        + 'justify-content:center;border:1px solid ' + (k === i ? 'rgba(114,197,194,.75)' : 'rgba(255,255,255,.12)')
        + ';background:' + (k === i ? 'rgba(0,149,161,.16)' : 'rgba(255,255,255,.035)') + ';';
    });
    document.getElementById('heroLinea').textContent  = HERO[i][0];
    document.getElementById('heroNombre').textContent = HERO[i][1];
    document.getElementById('heroMarca').textContent  = HERO[i][2];
  }
  function auto(){ timer = setInterval(function(){ i = (i + 1) % HERO.length; pintar(); }, 6000); }
  thumbs.forEach(function(t, k){
    t.addEventListener('click', function(){ clearInterval(timer); i = k; pintar(); });
  });
  pintar(); auto();
})();
"""


def transformar_main(c):
    for k in range(5):
        c = c.replace('<div class="slot" style="{{s%d}}">' % k, '<div class="slot">')
        c = c.replace('onClick="{{v%d}}" style="{{t%d}}"' % (k, k), 'data-hero="%d"' % k)
    c = c.replace("{{linea}}", '<span id="heroLinea"></span>')
    c = c.replace("{{nombre}}", '<span id="heroNombre"></span>')
    c = c.replace("{{marca}}", '<span id="heroMarca"></span>')
    return c


def transformar_productos(c):
    c = re.sub(r'<sc-if value="\{\{show(\w+)\}\}"[^>]*>', lambda m: '<div data-grupo="%s">' % m.group(1).lower(), c)
    c = c.replace("</sc-if>", "</div>")
    for cat in ["todos", "cadera", "rodilla", "cementos"]:
        c = c.replace('onClick="{{ver%s}}" style="{{s%s}}"' % (cat.capitalize(), cat.capitalize()),
                      'data-filter="%s"' % cat)
    return c


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
    for hid in ["quienTxt", "campo2", "campo2ph", "msgPh", "telPh",
                "sede1Tag", "sede1Nom", "sede1Dir", "sede1Tel",
                "sede2Tag", "sede2Nom", "sede2Dir", "sede2Tel"]:
        c = c.replace("{{%s}}" % hid, '<span id="%s"></span>' % hid)
    return c


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<meta property="og:type" content="website">
<link rel="icon" href="assets/logo.png">
__LINKS__
<style>
__CSS__
__BURGER__
__RESP__
</style>
</head>
<body>
__BODY__
<script>
document.addEventListener('click', function(e){
  var d = document.getElementById('drawer');
  if (d && d.classList.contains('open') && !e.target.closest('.drawer') && !e.target.closest('.burger')) d.classList.remove('open');
});
</script>
__JS__
</body>
</html>
"""


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
        cuerpo = cuerpo.replace("{{accent}}", ACCENT).replace("{{ringCls}}", "")
        if src in trans:
            cuerpo = trans[src](cuerpo)
        cuerpo = raiz_fluida(cuerpo)
        cuerpo = marcar(cuerpo)
        cuerpo = wire_nav(cuerpo, dst)
        cuerpo = add_burger(cuerpo, oscuro=(src == "Proceso.dc.html"))
        cuerpo = cuerpo.replace('src="', 'src="assets/').replace('src="assets/https', 'src="https')
        # botones que deben ir a una pagina real
        cuerpo = cuerpo.replace('>Ver los 21 productos', ' data-go>Ver los 21 productos')
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Ver catálogo de productos|Ver los 21 productos|Ver la línea|Ver el catálogo|Ver los 9 de cadera)',
                        lambda m: '<a href="productos.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Cómo trabajamos|Ver el proceso completo)',
                        lambda m: '<a href="proceso.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)(Ver sedes|Coordinar una cirugía|Escribir por WhatsApp|Consultar este producto|Consultar por WhatsApp|Enviar consulta)',
                        lambda m: '<a href="contacto.html"%s>%s%s' % (m.group(1), m.group(2), m.group(3)), cuerpo)
        cuerpo = re.sub(r'<a href="#"([^>]*?)>(\s*)Ver ficha', lambda m: '<a href="producto.html"%s>%sVer ficha' % (m.group(1), m.group(2)), cuerpo)

        html = (PLANTILLA
                .replace("__TITLE__", title).replace("__DESC__", desc)
                .replace("__LINKS__", links).replace("__CSS__", css)
                .replace("__BURGER__", BURGER_CSS).replace("__RESP__", RESPONSIVE)
                .replace("__BODY__", cuerpo)
                .replace("__JS__", "<script>%s</script>" % extras[src] if src in extras else ""))
        with open(os.path.join(OUT, dst), "w", encoding="utf-8") as f:
            f.write(html)

    quedan = []
    for _, dst, _, _ in PAGES:
        t = open(os.path.join(OUT, dst), encoding="utf-8").read()
        h = re.findall(r"\{\{[^}]+\}\}", t)
        if h:
            quedan.append((dst, sorted(set(h))))
    print("paginas:", ", ".join(d for _, d, _, _ in PAGES))
    print("holes sin resolver:", quedan if quedan else "ninguno")


if __name__ == "__main__":
    main()
