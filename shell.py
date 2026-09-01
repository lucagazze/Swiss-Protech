# -*- coding: utf-8 -*-
"""
Fuente unica del armazon del sitio: barra superior, CTA de cierre, pie, y los
datos de la empresa. Lo consumen build_site.py, build_paginas.py y la ficha
producto.html (a traves de build_ficha.py).

Si un dato de contacto cambia, se cambia aca y se reconstruye todo el sitio.

Verificado en swipro.com.ar el 01-09-2026:
  - "Contamos con mas de 20 anos de trayectoria en la comercializacion de protesis"
  - Sedes: Av. Belgrano 863, CABA  ·  Pte. Roca 782, piso 1, Rosario
  - Tel: 1135935241 en ambas sedes
  - No publica correo de contacto.
  - No publica cobertura por provincias ni menciona Chile ni Uruguay.
"""

BASE_URL = "https://swipro.com.ar"

# --------------------------------------------------------------------- datos
TRAYECTORIA = "20"          # "mas de 20 anos", textual del sitio del cliente
N_PRODUCTOS = "21"
N_MARCAS    = "3"
N_SEDES     = "2"

TEL_DISPLAY = "11 3593 5241"
TEL_LINK    = "+541135935241"
WA_NUMERO   = "5491135935241"   # 11 3593 5241 en formato internacional

# Enlace al Formulario F960/NM (Data Fiscal) de AFIP. Requiere el CUIT de la
# empresa: mientras este vacio el pie no muestra el item en lugar de mostrar un
# enlace roto.
AFIP_URL = ""

SEDES = [
    dict(rotulo="Sede Buenos Aires", nombre="Casa central",
         dir="Av. Belgrano 863, CABA", tel=TEL_DISPLAY,
         horario="Lunes a viernes, 8 a 17 h",
         mapa="https://www.openstreetmap.org/export/embed.html?bbox=-58.3897%2C-34.6141%2C-58.3797%2C-34.6091&layer=mapnik&marker=-34.6116%2C-58.3847"),
    dict(rotulo="Sede Rosario", nombre="Rosario, Santa Fe",
         dir="Pte. Roca 782, piso 1, Rosario", tel=TEL_DISPLAY,
         horario="Lunes a viernes, 8 a 17 h",
         mapa="https://www.openstreetmap.org/export/embed.html?bbox=-60.6448%2C-32.9498%2C-60.6348%2C-32.9448&layer=mapnik&marker=-32.9473%2C-60.6398"),
]

DESC_EMPRESA = ("Importaci&oacute;n y comercializaci&oacute;n de implantes ortop&eacute;dicos de origen alem&aacute;n "
                "y norteamericano. Habilitados por el Ministerio de Salud de la Naci&oacute;n y A.N.M.A.T.")


def wa(texto="Hola, quisiera hacer una consulta."):
    """URL de WhatsApp con el mensaje ya escrito."""
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (WA_NUMERO, quote(texto))


WA_GENERAL   = wa("Hola, quisiera hacer una consulta sobre sus implantes.")
WA_URGENTE   = wa("Hola, necesito coordinar un implante para una cirugia en las proximas 48 horas.")
WA_CATALOGO  = wa("Hola, queria consultar disponibilidad y medidas de un producto del catalogo.")


# ----------------------------------------------------------------------- css
# Todo va prefijado con sp- para poder convivir con los dos sistemas de estilos
# que tiene el sitio (los artboards con estilos en linea y las paginas nuevas).
CSS = """
/* ================= armazon compartido (shell.py) ================= */
.sp-wrap { max-width: 1240px; margin: 0 auto; padding: 0 40px; }

.sp-topbar { background: #10222A; color: #A7A9AC; font-size: 12.5px; letter-spacing: .04em; }
.sp-topbar .sp-wrap { padding-top: 1px; padding-bottom: 1px; display: flex; align-items: center;
                      justify-content: space-between; gap: 14px; flex-wrap: nowrap; white-space: nowrap; }
.sp-topbar a { color: #A7A9AC; text-decoration: none; display: inline-flex; align-items: center;
                min-height: 38px; }
.sp-topbar a:hover { color: #FFFFFF; }
.sp-topbar a.sp-reg { color: #72C5C2; font-weight: 600; }
.sp-topbar .sp-tb-l { display: flex; align-items: center; gap: 7px; min-width: 0; }
.sp-topbar .sp-tb-l svg { flex: none; }
.sp-topbar .sp-tb-r { display: flex; align-items: center; gap: 16px; }

.sp-cta { background: #0095A1; padding: 72px 0; }
.sp-cta .sp-wrap { display: flex; align-items: center; justify-content: space-between; gap: 44px; flex-wrap: wrap; }
.sp-cta h2 { margin: 0; font-size: 34px; line-height: 1.14; color: #FFFFFF; letter-spacing: -0.03em; font-weight: 700; }
.sp-cta p { margin: 12px 0 0; font-size: 16px; color: rgba(255,255,255,.88); line-height: 1.6; max-width: 60ch; }
.sp-cta .sp-acts { display: flex; align-items: center; gap: 13px; flex-wrap: wrap; }
.sp-cta a { display: inline-flex; align-items: center; gap: 10px; font-size: 15px; padding: 16px 30px;
            border-radius: 4px; white-space: nowrap; text-decoration: none; min-height: 52px; box-sizing: border-box;
            transition: background .28s, color .28s, border-color .28s; }
.sp-cta .sp-b1 { background: #FFFFFF; color: #0095A1; font-weight: 700; }
.sp-cta .sp-b1:hover { background: #EAF7F8; color: #007C87; }
.sp-cta .sp-b2 { border: 1px solid rgba(255,255,255,.5); color: #FFFFFF; font-weight: 600; }
.sp-cta .sp-b2:hover { border-color: #FFFFFF; background: rgba(255,255,255,.10); color: #FFFFFF; }

.sp-foot { background: #0A171D; padding: 62px 0 30px; }
.sp-foot .sp-cols { display: grid; grid-template-columns: 320px repeat(3, minmax(0, 1fr)); gap: 44px;
                    padding-bottom: 44px; border-bottom: 1px solid rgba(255,255,255,.09); }
.sp-foot .sp-col { display: flex; flex-direction: column; gap: 13px; }
.sp-foot .sp-col a, .sp-foot .sp-legal a { display: inline-flex; align-items: center;
                    min-height: 38px; align-self: flex-start; }
.sp-foot p, .sp-foot a, .sp-foot span { font-size: 13.5px; color: #A7A9AC; line-height: 1.65; text-decoration: none; }
.sp-foot p { margin: 0; color: #69727D; }
.sp-foot a:hover { color: #72C5C2; }
.sp-foot .sp-t { font-size: 11.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #FFFFFF; }
.sp-foot .sp-hr { font-size: 12.5px; color: #69727D; }
.sp-foot .sp-fin { display: flex; align-items: center; justify-content: space-between; gap: 24px;
                   padding-top: 26px; flex-wrap: wrap; }
.sp-foot .sp-fin span, .sp-foot .sp-fin a { font-size: 12.5px; color: #69727D; }
.sp-foot .sp-legal { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.sp-foot .sp-rs { display: flex; gap: 10px; margin-top: 4px; }
.sp-foot .sp-rs a { width: 42px; height: 42px; border-radius: 4px; border: 1px solid rgba(255,255,255,.14);
                    display: flex; align-items: center; justify-content: center; transition: border-color .28s, background .28s; }
.sp-foot .sp-rs a:hover { border-color: #0095A1; background: rgba(0,149,161,.14); }

/* ---- boton flotante de WhatsApp ---- */
.sp-wa { position: fixed; right: 22px; bottom: 22px; z-index: 60;
         display: inline-flex; align-items: center; gap: 0;
         height: 58px; padding: 0 17px; border-radius: 99px;
         background: #25D366; color: #FFFFFF; text-decoration: none;
         box-shadow: 0 14px 34px -10px rgba(16,34,42,.5), 0 0 0 6px rgba(37,211,102,.16);
         transition: background .28s, box-shadow .28s, gap .3s cubic-bezier(.4,0,.2,1); }
.sp-wa:hover, .sp-wa:focus-visible { background: #1EBE57; color: #FFFFFF; gap: 11px;
         box-shadow: 0 18px 40px -10px rgba(16,34,42,.55), 0 0 0 9px rgba(37,211,102,.22); }
.sp-wa svg { flex: none; }
.sp-wa b { font-size: 14.5px; font-weight: 600; white-space: nowrap; letter-spacing: -0.01em;
           max-width: 0; overflow: hidden; opacity: 0;
           transition: max-width .34s cubic-bezier(.4,0,.2,1), opacity .24s; }
.sp-wa:hover b, .sp-wa:focus-visible b { max-width: 190px; opacity: 1; }
@media (max-width: 720px) {
  .sp-wa { right: 16px; bottom: 16px; height: 54px; padding: 0 15px; }
  .sp-wa b { display: none; }
}
@media (prefers-reduced-motion: reduce) { .sp-wa, .sp-wa b { transition: none; } }

@media (max-width: 1000px) { .sp-foot .sp-cols { grid-template-columns: repeat(2, minmax(0,1fr)); gap: 30px; } }
@media (max-width: 860px) {
  /* en pantallas chicas queda la habilitacion corta: el renglon no se parte */
  .sp-topbar { font-size: 11px; letter-spacing: .01em; }
  .sp-topbar .sp-tb-mas { display: none; }
  .sp-topbar .sp-wrap { gap: 10px; }
  .sp-topbar .sp-tb-r { gap: 9px; }
}
@media (max-width: 720px) {
  .sp-wrap { padding: 0 20px; }
  /* en el pie apilado el gap ya separa: sin el, los enlaces quedan pegados */
  .sp-foot .sp-col { gap: 4px; }
  .sp-foot .sp-legal { gap: 14px; }
  .sp-cta { padding: 48px 0; }
  .sp-cta h2 { font-size: 26px; }
  .sp-cta .sp-acts { width: 100%; }
  .sp-cta .sp-acts a { flex-grow: 1; justify-content: center; }
  .sp-foot .sp-cols { grid-template-columns: 1fr; }
  .sp-foot .sp-fin { flex-direction: column; align-items: flex-start; gap: 12px; }
}


/* ================= movimiento: entradas al hacer scroll =================
   Nada se mueve solo ni parpadea: cada bloque aparece una vez, al entrar en
   pantalla, y se queda. Con prefers-reduced-motion todo nace ya visible. */
.sp-rev { opacity: 0; transform: translateY(22px); }
.sp-rev.vis { opacity: 1; transform: none;
              transition: opacity .7s cubic-bezier(.22,.61,.36,1), transform .7s cubic-bezier(.22,.61,.36,1); }
.sp-rev-1.vis { transition-delay: .06s; }
.sp-rev-2.vis { transition-delay: .12s; }
.sp-rev-3.vis { transition-delay: .18s; }
.sp-rev-4.vis { transition-delay: .24s; }
@media (prefers-reduced-motion: reduce) {
  .sp-rev { opacity: 1 !important; transform: none !important; transition: none !important; }
}

/* la barra se despega del borde cuando arranca el scroll */
.sp-nav-fija { position: sticky; top: 0; z-index: 40; transition: box-shadow .3s, backdrop-filter .3s; }
.sp-nav-fija.sp-pegada { box-shadow: 0 10px 30px -22px rgba(16,34,42,.55); }
"""

_ESCUDO = ('<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0095A1" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4.5 8-11V5l-8-3-8 3v6c0 6.5 8 11 8 11z"></path></svg>')
_WA_GLIFO = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" width="%s" height="%s"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>'

_WA_ICO = _WA_GLIFO % ("18", "18")

REDES = [
    ("https://www.instagram.com/swissprotech/", "Instagram",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A7A9AC" stroke-width="1.9" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="5"></rect><circle cx="12" cy="12" r="4"></circle><circle cx="17.2" cy="6.8" r="1.1" fill="#A7A9AC" stroke="none"></circle></svg>'),
    ("https://www.facebook.com/SwissProtechSA", "Facebook",
     '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#A7A9AC" stroke-width="1.9" stroke-linecap="round"><path d="M15 3h-2.5A3.5 3.5 0 0 0 9 6.5V9H7v3h2v9h3v-9h2.4l.6-3H12V6.8c0-.5.4-.8.9-.8H15z"></path></svg>'),
]


def topbar():
    return """
<div class="sp-topbar"><div class="sp-wrap">
  <span class="sp-tb-l">%s<span>Habilitado por ANMAT<span class="sp-tb-mas"> y Ministerio de Salud de la Naci&oacute;n</span></span></span>
  <span class="sp-tb-r"><a href="educacion.html">Ingresar</a><span style="opacity:.32">|</span><a href="educacion.html" class="sp-reg">Registro m&eacute;dico</a></span>
</div></div>
""" % _ESCUDO


def cta():
    return """
<div class="sp-cta"><div class="sp-wrap">
  <div><h2>&iquest;Necesit&aacute;s asesoramiento t&eacute;cnico?</h2>
    <p>Contanos si escrib&iacute;s como m&eacute;dico, como financiador o como paciente, y la consulta llega directo a quien corresponde.</p></div>
  <div class="sp-acts">
    <a class="sp-b1" href="%s" target="_blank" rel="noopener">%s Escribir por WhatsApp</a>
    <a class="sp-b2" href="contacto.html">Ver sedes</a></div>
</div></div>
""" % (WA_GENERAL, _WA_ICO)


def footer():
    sedes = ""
    for s in SEDES:
        sedes += """
    <div class="sp-col"><span class="sp-t">%s</span>
      <span>%s</span>
      <a href="tel:%s">%s</a>
      <span class="sp-hr">%s</span></div>""" % (s["rotulo"], s["dir"], TEL_LINK, s["tel"], s["horario"])

    redes = "".join('<a href="%s" target="_blank" rel="noopener" aria-label="%s">%s</a>' % r for r in REDES)

    legal = '<a href="privacidad.html">Pol&iacute;ticas de privacidad</a>'
    if AFIP_URL:
        legal += '<a href="%s" target="_blank" rel="noopener">Formulario AFIP F960</a>' % AFIP_URL

    return """
<footer class="sp-foot"><div class="sp-wrap">
  <div class="sp-cols">
    <div class="sp-col">
      <img src="assets/logo-blanco.webp" alt="Swiss Protech" style="height: 40px; width: auto; align-self: flex-start;">
      <p>%s</p>
      <div class="sp-rs">%s</div>
    </div>
    <div class="sp-col"><span class="sp-t">Productos</span>
      <a href="productos.html#cadera">Cadera</a>
      <a href="productos.html#rodilla">Rodilla</a>
      <a href="productos.html#cementos">Cementos</a>
      <a href="representaciones.html">Representaciones</a></div>%s
  </div>
  <div class="sp-fin"><span>Swiss Protech S.A. &mdash; Todos los derechos reservados 2026.</span>
    <span class="sp-legal">%s</span></div>
</div></footer>
""" % (DESC_EMPRESA, redes, sedes, legal)


def wa_flotante():
    """Acceso directo a WhatsApp, presente en todas las paginas."""
    return ('<a class="sp-wa" href="%s" target="_blank" rel="noopener" '
            'aria-label="Escribinos por WhatsApp">%s<b>Escribinos</b></a>'
            % (WA_GENERAL, _WA_GLIFO % ("27", "27")))


def pie():
    """CTA + pie, que es como se cierran todas las paginas."""
    return cta() + footer() + wa_flotante()


# ---------------------------------------------------------------------- head
def meta(titulo, desc, archivo, og_img="assets/og.jpg"):
    """Etiquetas de <head> comunes: canonica, redes sociales, favicon."""
    url = "%s/%s" % (BASE_URL, "" if archivo == "index.html" else archivo)
    return """<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:site_name" content="Swiss Protech">
<meta property="og:locale" content="es_AR">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:url" content="%s">
<meta property="og:image" content="%s/%s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0095A1">
<link rel="icon" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/favicon.png">""" % (titulo, desc, url, titulo, desc, url, BASE_URL, og_img)


def jsonld_organizacion():
    import json
    d = {
        "@context": "https://schema.org",
        "@type": "MedicalBusiness",
        "name": "Swiss Protech S.A.",
        "url": BASE_URL,
        "logo": "%s/assets/logo.webp" % BASE_URL,
        "description": ("Importación y comercialización de implantes ortopédicos de cadera y rodilla. "
                        "Representantes exclusivos en Argentina de Waldemar Link, Advita Ortho y Heraeus Medical."),
        "telephone": TEL_LINK,
        "areaServed": ["AR"],
        "sameAs": [r[0] for r in REDES],
        "address": [{
            "@type": "PostalAddress",
            "streetAddress": "Av. Belgrano 863",
            "addressLocality": "Ciudad Autónoma de Buenos Aires",
            "addressCountry": "AR",
        }, {
            "@type": "PostalAddress",
            "streetAddress": "Pte. Roca 782, piso 1",
            "addressLocality": "Rosario",
            "addressRegion": "Santa Fe",
            "addressCountry": "AR",
        }],
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "08:00", "closes": "17:00",
        }],
    }
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)


def jsonld_migas(items):
    """items: [(nombre, archivo), ...] desde Home hasta la pagina actual."""
    import json
    d = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n,
         "item": "%s/%s" % (BASE_URL, "" if f == "index.html" else f)}
        for i, (n, f) in enumerate(items)]}
    return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)


# --------------------------------------------------------------------- js
# Un solo script para todo el sitio: entradas al hacer scroll y barra pegada.
MOVIMIENTO_JS = """
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  // que se anima: bloques de contenido, nunca la navegacion ni el pie legal
  var sel = ['section > .wrap > *', '.card', '.marca', '.vid', '.hito', '.st',
             '.kpi > div', '.heroimg', '.cerrado', '.film', '.film-pie',
             '.pc', '.step', '.prov'];
  var lista = [];
  sel.forEach(function (q) {
    Array.prototype.forEach.call(document.querySelectorAll(q), function (el) {
      if (el.closest('.sp-topbar') || el.closest('nav') || el.closest('.drawer') ||
          el.closest('.sp-foot') || lista.indexOf(el) >= 0) return;
      lista.push(el);
    });
  });
  if (!lista.length) return;

  lista.forEach(function (el, i) {
    el.classList.add('sp-rev');
    var k = i % 4;
    if (k) el.classList.add('sp-rev-' + k);
  });

  // Se revela por posicion, no por interseccion: si el usuario salta de golpe
  // al pie o abre un ancla, todo lo que quedo arriba igual aparece. Nada puede
  // quedarse invisible.
  var pendientes = lista.slice();
  function revelar() {
    var limite = window.innerHeight * 0.94;
    for (var i = pendientes.length - 1; i >= 0; i--) {
      var el = pendientes[i];
      if (el.getBoundingClientRect().top < limite) {
        el.classList.add('vis');
        pendientes.splice(i, 1);
      }
    }
    if (!pendientes.length) {
      window.removeEventListener('scroll', pedir);
      window.removeEventListener('resize', pedir);
    }
  }
  var pedido = false;
  function pedir() {
    if (pedido) return;
    pedido = true;
    requestAnimationFrame(function () { pedido = false; revelar(); });
  }
  window.addEventListener('scroll', pedir, { passive: true });
  window.addEventListener('resize', pedir);
  revelar();

  // red de seguridad: pase lo que pase, a los 4 s no queda nada oculto
  setTimeout(function () {
    lista.forEach(function (el) { el.classList.add('vis'); });
  }, 4000);
})();
"""
