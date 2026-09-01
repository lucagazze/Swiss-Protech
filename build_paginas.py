# -*- coding: utf-8 -*-
"""
Genera las paginas que faltaban del presupuesto, con la misma identidad que el resto:
  institucional.html · representaciones.html · educacion.html · multimedia.html
Todo el contenido sale de swipro.com.ar. Ejecutar: python -u build_paginas.py
"""
import os

import shell

SRC = os.path.dirname(os.path.abspath(__file__))

NAV = [("Inicio", "index.html"), ("Institucional", "institucional.html"), ("Productos", "productos.html"),
       ("Nuestro proceso", "proceso.html"), ("Educación médica", "educacion.html"),
       ("Representaciones", "representaciones.html"), ("Contacto", "contacto.html")]

CSS = """
  :root { --teal: #0095A1; --teal-d: #007C87; --teal-l: #72C5C2; --ink: #10222A; --txt: #5A6570; --mut: #8A929A; --line: #E3E7E9; --bg: #F7F8F9; }
  * { box-sizing: border-box; }
  html, body { overflow-x: hidden; } html { scroll-behavior: smooth; }
  body { margin: 0; font-family: Montserrat, "Helvetica Neue", Arial, sans-serif; color: var(--ink); background: #fff; -webkit-font-smoothing: antialiased; }
  a { color: var(--teal); text-decoration: none; } a:hover { color: var(--teal-d); }
  h1, h2, h3 { margin: 0; font-weight: 700; letter-spacing: -0.02em; line-height: 1.14; }
  p { margin: 0; } img { max-width: 100%; }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 0 40px; }
  .eyebrow { font-size: 11.5px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; color: var(--teal); }
  .lead { font-size: 16.5px; color: var(--txt); line-height: 1.68; }

  .topbar { background: var(--ink); color: #A7A9AC; font-size: 12.5px; letter-spacing: .04em; }
  .topbar .wrap { padding-top: 9px; padding-bottom: 9px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
  .topbar a { color: #A7A9AC; } .topbar a.reg { color: var(--teal-l); font-weight: 600; }

  .nav { background: #fff; border-bottom: 1px solid var(--line); position: relative; z-index: 5; }
  .nav .wrap { padding-top: 20px; padding-bottom: 20px; display: flex; align-items: center; justify-content: space-between; gap: 40px; }
  .navlinks { display: flex; align-items: center; gap: 26px; font-size: 14px; font-weight: 500; }
  .navlink { position: relative; color: var(--ink); transition: color .25s; }
  .navlink::after { content: ""; position: absolute; left: 0; right: 100%; bottom: -7px; height: 2px; background: var(--teal); transition: right .3s; }
  .navlink:hover { color: var(--teal); } .navlink:hover::after { right: 0; }
  .navlink.on { color: var(--teal); font-weight: 600; }
  .btn-p { display: inline-flex; align-items: center; gap: 9px; background: var(--teal); color: #fff; font-size: 14px; font-weight: 600; padding: 13px 24px; border-radius: 4px; white-space: nowrap; transition: background .28s, box-shadow .28s; border: 0; cursor: pointer; }
  .btn-p:hover { background: var(--teal-d); color: #fff; box-shadow: 0 12px 26px -12px rgba(0,149,161,.55); }
  .btn-g { display: inline-flex; align-items: center; gap: 9px; border: 1px solid #CBD2D6; color: var(--ink); background: #fff; font-size: 14px; font-weight: 600; padding: 13px 24px; border-radius: 4px; white-space: nowrap; transition: border-color .28s, color .28s, background .28s; }
  .btn-g:hover { border-color: var(--teal); color: var(--teal); background: rgba(0,149,161,.05); }
  .burger { display: none; width: 44px; height: 44px; border-radius: 6px; border: 1px solid var(--line); align-items: center; justify-content: center; cursor: pointer; flex: none; background: #fff; }
  .drawer { display: none; flex-direction: column; gap: 2px; padding: 10px 20px 18px; border-bottom: 1px solid var(--line); background: #fff; }
  .drawer.open { display: flex; }
  .drawer a { padding: 14px 4px; font-size: 15px; font-weight: 500; color: var(--ink); border-bottom: 1px solid #F1F4F5; min-height: 50px; display: flex; align-items: center; }

  .mesh { background-image: linear-gradient(rgba(16,34,42,.030) 1px, transparent 1px), linear-gradient(90deg, rgba(16,34,42,.030) 1px, transparent 1px);
          background-size: 64px 64px; -webkit-mask-image: radial-gradient(circle at 76% 44%, #000 0%, transparent 72%); mask-image: radial-gradient(circle at 76% 44%, #000 0%, transparent 72%); }
  .head { position: relative; background: linear-gradient(168deg, #FFFFFF 0%, #F6FAFB 52%, #EAF1F3 100%); border-bottom: 1px solid var(--line); overflow: hidden; }
  .head .wrap { position: relative; padding-top: 58px; padding-bottom: 54px; display: flex; flex-direction: column; gap: 14px; }
  .crumbs { font-size: 12.5px; color: var(--mut); }
  .crumbs a { display: inline-flex; align-items: center; min-height: 34px; }
  /* enlaces de cierre de tarjeta y de bloque de marca: area tactil de 40 px */
  .card > a, .marca > div > a, .cerrado .acts a,
  .card p a[href^="tel"], .hito p a[href^="tel"] { display: inline-flex; align-items: center; min-height: 40px; }
  .eyebrow { font-size: 12px; letter-spacing: .14em; }
  .head h1 { font-size: 44px; letter-spacing: -0.035em; max-width: 20ch; }
  .head .lead { max-width: 64ch; }

  section { padding: 78px 0; }
  section.alt { background: var(--bg); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .st { display: flex; flex-direction: column; gap: 13px; margin-bottom: 40px; max-width: 68ch; }
  .st h2 { font-size: 36px; letter-spacing: -0.03em; }

  .g2 { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 24px; }
  .g3 { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 24px; }
  .g4 { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 22px; }
  .card { background: #fff; border: 1px solid var(--line); border-radius: 6px; padding: 30px 28px; display: flex; flex-direction: column; gap: 13px; transition: transform .35s, border-color .35s, box-shadow .35s; }
  .card:hover { transform: translateY(-4px); border-color: var(--teal); box-shadow: 0 20px 38px -20px rgba(16,34,42,.24); }
  .card h3 { font-size: 19px; } .card p { font-size: 14.5px; color: var(--txt); line-height: 1.65; }
  .ico { width: 46px; height: 46px; border-radius: 6px; background: rgba(0,149,161,.09); display: flex; align-items: center; justify-content: center; }
  .ico svg { stroke: var(--teal); }

  .kpi { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 26px; }
  .kpi > div { display: flex; flex-direction: column; gap: 6px; border-left: 3px solid var(--line); padding-left: 20px; }
  .kpi > div:first-child { border-color: var(--teal); }
  .kpi b { font-size: 38px; font-weight: 800; letter-spacing: -0.04em; line-height: 1; }
  .kpi span { font-size: 13.5px; color: var(--txt); line-height: 1.45; }

  .hitos { display: flex; flex-direction: column; gap: 0; }
  /* 166px = el rotulo mas largo ("Representaciones", 158px a 17/800) con aire */
  .hito { display: grid; grid-template-columns: 166px minmax(0, 1fr); gap: 26px; padding: 24px 0; border-top: 1px solid var(--line); }
  .hito:last-child { border-bottom: 1px solid var(--line); }
  .hito .a { font-size: 17px; font-weight: 800; color: var(--teal); letter-spacing: -0.02em; white-space: nowrap; }
  .hito h3 { font-size: 17.5px; margin-bottom: 6px; } .hito p { font-size: 14.5px; color: var(--txt); line-height: 1.65; }

  .prov { font-size: 13px; color: var(--ink); border: 1px solid var(--line); background: #fff; padding: 8px 15px; border-radius: 4px; font-weight: 500; transition: border-color .3s, color .3s, background .3s; }
  .prov:hover { background: rgba(0,149,161,.07); border-color: var(--teal); color: var(--teal); }
  .chips { display: flex; flex-wrap: wrap; gap: 9px; }

  .marca { display: grid; grid-template-columns: 260px 1fr; gap: 34px; align-items: start; background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 34px 36px; }
  .marca .logo { height: 54px; display: flex; align-items: center; }
  .marca h3 { font-size: 24px; letter-spacing: -0.025em; }
  .marca .datos { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
  .marca .datos span { font-size: 12px; color: var(--txt); border: 1px solid var(--line); padding: 5px 11px; border-radius: 99px; }

  .vid { background: #fff; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; display: flex; flex-direction: column; }
  .vid video { width: 100%; aspect-ratio: 16/10; object-fit: cover; background: #EAF1F3; display: block; }
  .vid .bd { padding: 16px 18px 20px; display: flex; flex-direction: column; gap: 6px; }
  .vid b { font-size: 15px; } .vid span { font-size: 12.5px; color: var(--mut); }

  .cerrado { background: linear-gradient(165deg, var(--ink) 0%, #0A171D 100%); border-radius: 8px; padding: 44px 46px; color: #fff; position: relative; overflow: hidden; }
  .cerrado .glow { position: absolute; top: -90px; right: -80px; width: 320px; height: 320px; border-radius: 50%; background: radial-gradient(circle, rgba(0,149,161,.30), transparent 70%); filter: blur(34px); }
  .cerrado h3 { font-size: 26px; color: #fff; } .cerrado p { color: #A7A9AC; font-size: 15px; line-height: 1.68; }
  .cerrado .acts { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
  .cerrado .btn-g { border-color: rgba(255,255,255,.24); color: #fff; background: transparent; }
  .cerrado .btn-g:hover { border-color: var(--teal-l); color: #fff; background: rgba(255,255,255,.06); }

  .cta { background: var(--teal); padding: 68px 0; }
  .cta .wrap { display: flex; align-items: center; justify-content: space-between; gap: 44px; flex-wrap: wrap; }
  .cta h2 { font-size: 32px; color: #fff; letter-spacing: -0.03em; } .cta p { color: rgba(255,255,255,.88); font-size: 15.5px; line-height: 1.6; max-width: 58ch; margin-top: 10px; }
  .cta .b1 { background: #fff; color: var(--teal); font-weight: 700; }
  .cta .b1:hover { background: #fff; color: var(--teal-d); }
  .cta .b2 { border: 1px solid rgba(255,255,255,.5); color: #fff; background: transparent; }
  .cta .b2:hover { border-color: #fff; color: #fff; background: rgba(255,255,255,.08); }

  footer { background: #0A171D; padding: 58px 0 28px; }
  footer .cols { display: grid; grid-template-columns: 320px repeat(3, minmax(0,1fr)); gap: 42px; padding-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,.09); }
  footer p, footer a, footer span { font-size: 13.5px; color: #A7A9AC; line-height: 1.65; }
  footer .t { font-size: 11.5px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #fff; }
  footer .col { display: flex; flex-direction: column; gap: 12px; }
  footer .fin { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding-top: 24px; flex-wrap: wrap; }
  footer .fin span, footer .fin a { font-size: 12.5px; color: #69727D; }

  @media (max-width: 1240px) { .navlinks, .nav .btn-p { display: none; } .burger { display: flex; } }
  @media (max-width: 1000px) { .g4 { grid-template-columns: repeat(2, minmax(0,1fr)); } .g3 { grid-template-columns: repeat(2, minmax(0,1fr)); }
    .marca { grid-template-columns: 1fr; gap: 20px; } footer .cols { grid-template-columns: repeat(2, minmax(0,1fr)); } }
  @media (max-width: 720px) { .wrap { padding: 0 20px; } section { padding: 52px 0; } .head .wrap { padding-top: 38px; padding-bottom: 36px; }
    .head h1 { font-size: 32px; } .st h2 { font-size: 27px; } .g2, .g3, .g4 { grid-template-columns: 1fr; }
    .kpi { grid-template-columns: repeat(2, minmax(0,1fr)); } .hito { grid-template-columns: 1fr; gap: 8px; }
    .card, .marca, .cerrado { padding: 24px 20px; } footer .cols { grid-template-columns: 1fr; } .cta { padding: 48px 0; } }
"""

SVG = lambda d: '<svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % d
I_ESCUDO = SVG('<path d="M12 22s8-4.5 8-11V5l-8-3-8 3v6c0 6.5 8 11 8 11z"></path><path d="M9 12l2 2 4-4"></path>')
I_RELOJ  = SVG('<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>')
I_MAPA   = SVG('<path d="M21 10c0 6-9 12-9 12s-9-6-9-12a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>')
I_CAJA   = SVG('<path d="M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><path d="M3.3 7L12 12l8.7-5M12 22V12"></path>')
I_LIBRO  = SVG('<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>')
I_PLAY   = SVG('<circle cx="12" cy="12" r="9"></circle><path d="M10 8.5l6 3.5-6 3.5z"></path>')
I_DOC    = SVG('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6M9 15l2 2 4-4"></path>')
I_USER   = SVG('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>')

# Nota: el sitio del cliente no publica una lista de provincias ni una cantidad.
# Cualquier cifra de cobertura tiene que venir confirmada por la empresa antes de
# volver a ponerla acá.


A11Y = """
  .navlinks a { white-space: nowrap; }
  @media (max-width: 1330px) { .navlinks { gap: 20px; font-size: 13.5px; } }
  body { font-size: 16px; line-height: 1.6; text-rendering: optimizeLegibility; }
  p { text-wrap: pretty; } h1, h2, h3 { text-wrap: balance; }
  .lead { font-size: 17px; line-height: 1.7; max-width: 62ch; }
  .card p { font-size: 15px; line-height: 1.68; }
  .hito p { font-size: 15px; line-height: 1.7; }
  .st h2 { font-size: 38px; }
  section { padding: 88px 0; }
  @media (max-width: 720px) { body { font-size: 15.5px; } .st h2 { font-size: 27px; } section { padding: 52px 0; } }

  .sr-skip { position: absolute; left: -9999px; top: 0; z-index: 99; background: var(--teal); color: #fff;
             padding: 12px 20px; font-size: 14px; font-weight: 600; border-radius: 0 0 4px 0; }
  .sr-skip:focus { left: 0; }
  a:focus-visible, button:focus-visible { outline: 3px solid var(--teal); outline-offset: 2px; border-radius: 3px; }
  @media (prefers-reduced-motion: reduce) { * { animation-duration: .01ms !important; transition-duration: .01ms !important; } html { scroll-behavior: auto; } }
"""


def cabecera(activo, titulo, desc, migas=None):
    links = "".join('<a href="%s" class="navlink%s"%s>%s</a>'
                    % (h, " on" if h == activo else "", ' aria-current="page"' if h == activo else "", t)
                    for t, h in NAV)
    drawer = "".join('<a href="%s">%s</a>' % (h, t) for t, h in NAV)
    ld = shell.jsonld_migas(migas or [("Home", "index.html")])
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
%s
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap">
<style>%s
%s
%s</style>
%s
</head>
<body>
<a href="#contenido" class="sr-skip">Ir al contenido</a>
%s
<nav class="nav"><div class="wrap">
  <a href="index.html" aria-label="Swiss Protech — inicio"><img src="assets/logo.webp" alt="Swiss Protech" style="height: 42px; display: block;"></a>
  <div class="navlinks">%s</div>
  <span class="burger" onclick="document.getElementById('drawer').classList.toggle('open')">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10222A" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"></path></svg></span>
  <a href="contacto.html" class="btn-p">Consultar</a>
</div></nav>
<div class="drawer" id="drawer">%s</div>
<span id="contenido" tabindex="-1"></span>
""" % (shell.meta(titulo, desc, activo), CSS, shell.CSS, A11Y, ld, shell.topbar(), links, drawer)


PIE = shell.pie() + """
<script>
document.addEventListener('click', function (e) {
  var d = document.getElementById('drawer');
  if (d && d.classList.contains('open') && !e.target.closest('.drawer') && !e.target.closest('.burger')) d.classList.remove('open');
});
</script>
<script>""" + shell.MOVIMIENTO_JS + """</script>
</body>
</html>
"""


def head(crumb, h1, lead):
    return """
<div class="head"><div class="mesh" style="position:absolute;inset:0;"></div><div class="wrap">
  <span class="crumbs"><a href="index.html" style="color:var(--mut)">Home</a> &nbsp;/&nbsp; <span style="color:var(--teal)">%s</span></span>
  <h1>%s</h1>
  <p class="lead">%s</p>
</div></div>
""" % (crumb, h1, lead)


# ================================================================ INSTITUCIONAL
HITOS = [
    ("Origen", "Importación directa de implantes ortopédicos",
     "Swiss Protech S.A. nace para traer al país implantes de cadera y rodilla de fabricantes europeos y norteamericanos, sin intermediarios."),
    ("Habilitaciones", "Ministerio de Salud de la Nación y A.N.M.A.T.",
     "La empresa cuenta con todas las habilitaciones que exige la normativa argentina para importar y comercializar productos médicos implantables."),
    ("Representaciones", "Acuerdos de exclusividad",
     "Swiss Protech es representante exclusivo en Argentina de Waldemar Link, Advita Ortho y Heraeus Medical."),
    ("Sedes", "Buenos Aires y Rosario",
     "Dos sedes propias con depósito e instrumental, desde donde sale cada implante hacia el centro de salud donde se realiza la cirugía."),
    ("Hoy", "Más de 20 años de trayectoria",
     "Veintiún productos en catálogo entre cadera, rodilla y cementos óseos, y un circuito de trazabilidad documentado en cada implante."),
]

def institucional():
    hitos = "".join("""<div class="hito"><div class="a">%s</div><div><h3>%s</h3><p>%s</p></div></div>""" % h for h in HITOS)
    return (cabecera("institucional.html", "Institucional — Swiss Protech",
                     "Más de 20 años importando implantes ortopédicos de origen alemán y norteamericano. Habilitados por ANMAT y el Ministerio de Salud de la Nación.",
                     [("Home", "index.html"), ("Institucional", "institucional.html")])
    + head("Institucional", "Más de 20 años de trayectoria en implantes ortopédicos",
           "Importamos y comercializamos implantes de cadera y rodilla de la más alta calidad, de origen alemán y norteamericano, con todas las habilitaciones que exige la normativa argentina.")
    + """
<section><div class="wrap">
  <div class="kpi">
    <div><b>+20</b><span>años de trayectoria en el país</span></div>
    <div><b>21</b><span>productos entre cadera, rodilla y cementos</span></div>
    <div><b>3</b><span>marcas internacionales representadas</span></div>
    <div><b>2</b><span>sedes propias: Buenos Aires y Rosario</span></div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="st"><span class="eyebrow">Quiénes somos</span>
    <h2>Soluciones para mejorar la calidad de vida del paciente</h2>
    <p class="lead">Mediante nuestros productos y servicios brindamos a pacientes, médicos, prestadores y financiadores del sistema de salud público y privado de todo el país soluciones superadoras para mejorar la calidad de vida de los pacientes.</p></div>
  <div class="g3">
    <div class="card"><span class="ico">""" + I_RELOJ + """</span><h3>Experiencia</h3><p>Más de 20 años importando prótesis de cadera y rodilla.</p></div>
    <div class="card"><span class="ico">""" + I_CAJA + """</span><h3>Calidad</h3><p>Fabricantes líderes de Alemania y Estados Unidos.</p></div>
    <div class="card"><span class="ico">""" + I_ESCUDO + """</span><h3>Certificación</h3><p>Habilitados por el Ministerio de Salud y A.N.M.A.T.</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="st"><span class="eyebrow">Trayectoria</span><h2>Cómo llegamos hasta acá</h2></div>
  <div class="hitos">""" + hitos + """</div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="st"><span class="eyebrow">Dónde estamos</span><h2>Dos sedes, un mismo circuito</h2>
    <p class="lead">Casa central en Buenos Aires y sede en Rosario. Desde cualquiera de las dos coordinamos la entrega y el acompañamiento técnico en el centro de salud donde se realiza la cirugía.</p></div>
  <div class="g2">
    <div class="card"><span class="ico">""" + I_MAPA + """</span><h3>Sede Buenos Aires</h3>
      <p>Av. Belgrano 863, CABA<br><a href="tel:""" + shell.TEL_LINK + """">""" + shell.TEL_DISPLAY + """</a><br>Lunes a viernes, 8 a 17 h</p></div>
    <div class="card"><span class="ico">""" + I_MAPA + """</span><h3>Sede Rosario</h3>
      <p>Pte. Roca 782, piso 1, Rosario<br><a href="tel:""" + shell.TEL_LINK + """">""" + shell.TEL_DISPLAY + """</a><br>Lunes a viernes, 8 a 17 h</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="st"><span class="eyebrow">Nuestro diferencial</span><h2>Un implante no se entrega. Se acompaña.</h2>
    <p class="lead">Entre que una prótesis sale de nuestro depósito y entra al quirófano hay cinco etapas con registro propio. Ese circuito es lo que auditan los centros de salud antes de trabajar con nosotros.</p></div>
  <a href="proceso.html" class="btn-p">Ver el proceso completo
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"></path></svg></a>
</div></section>
""" + PIE)


# ================================================================ REPRESENTACIONES
MARCAS = [
    dict(logo="assets/link.webp", filtro="filter: invert(1) brightness(.28);", alto="30px",
         n="Waldemar Link GmbH & Co. KG", pais="Hamburgo, Alemania",
         datos=["Fundada el 1 de enero de 1948", "Presente en más de 70 países", "Cinco décadas en endoprotética de grandes articulaciones"],
         txt=["Fabricante alemán de endoprótesis articulares: cadera, rodilla, extremidad superior e implantes personalizados.",
              "De Link provienen la mayoría de los sistemas que Swiss Protech comercializa en Argentina: los cotilos MobileLink y Lubinus, los vástagos LCU, Lubinus SP II y MP Link, y las prótesis de rodilla Endo-Model."],
         prods=["MobileLink", "MobileLink Dual Mobility", "Lubinus Cup", "Lubinus SPII Revision", "MP Link", "LCU", "Endomodel", "Uni Sled"],
         web="link-ortho.com", url="https://www.link-ortho.com/"),
    dict(logo="assets/advita.webp", filtro="filter: invert(1) brightness(.28);", alto="34px",
         n="Advita Ortho", pais="Estados Unidos",
         datos=["Sistemas Novation® y Optetrak®", "Polietileno XLE con vitamina E"],
         txt=["Fabricante norteamericano de sistemas de reemplazo articular primario y de revisión para cadera y rodilla.",
              "De Advita provienen los cotilos Crown Cup, los vástagos Element y la familia de prótesis de rodilla Optetrak, en sus versiones Logic, Hi-Flex y CC de revisión."],
         prods=["Crown Cup", "Element", "Optetrak Logic", "Optetrak Hi-Flex", "Optetrak CC"],
         web="advita.com", url="https://advita.com/"),
    dict(logo="assets/heraeus.webp", filtro="", alto="28px",
         n="Heraeus Medical", pais="Alemania",
         datos=["Cementos óseos PALACOS y COPAL", "Sistemas de mezcla al vacío PALAMIX"],
         txt=["Fabricante alemán de cementos óseos para fijación de implantes. La familia PALACOS es una de las de mayor uso clínico documentado del mundo.",
              "De Heraeus provienen los cementos que Swiss Protech comercializa, con y sin antibiótico, y el sistema completo de mezcla y aplicación PALAMIX."],
         prods=["COPAL G+C", "PALACOS MV y MV+G", "PALACOS R", "PALAMIX Pistola", "PALAMIX UNO o DUO"],
         web="heraeus-medical.com", url="https://www.heraeus-medical.com/"),
]

def representaciones():
    bloques = []
    for m in MARCAS:
        datos = "".join("<span>%s</span>" % d for d in m["datos"])
        txt = "".join('<p class="lead" style="font-size:15.5px">%s</p>' % t for t in m["txt"])
        prods = "".join('<a href="productos.html" class="prov">%s</a>' % x for x in m["prods"])
        bloques.append("""<div class="marca">
  <div><div class="logo"><img src="%s" alt="%s" style="height:%s; %s"></div>
    <div class="datos" style="margin-top:16px">%s</div></div>
  <div style="display:flex;flex-direction:column;gap:14px">
    <div><h3>%s</h3><span style="font-size:13px;color:var(--mut)">%s</span></div>
    %s
    <div><span class="eyebrow">Productos que representamos</span>
      <div class="chips" style="margin-top:10px">%s</div></div>
    <a href="%s" target="_blank" rel="noopener" style="font-size:13.5px;font-weight:600;margin-top:4px">%s &#8599;</a>
  </div></div>""" % (m["logo"], m["n"], m["alto"], m["filtro"], datos, m["n"], m["pais"], txt, prods, m["url"], m["web"]))
    return (cabecera("representaciones.html", "Representaciones — Swiss Protech",
                     "Representantes exclusivos en Argentina de Waldemar Link, Advita Ortho y Heraeus Medical.",
                     [("Home", "index.html"), ("Representaciones", "representaciones.html")])
    + head("Representaciones", "Los fabricantes que representamos",
           "Somos representantes exclusivos en Argentina de compañías líderes en tecnología médica de origen alemán y norteamericano. Cada producto de nuestro catálogo viene de una de estas tres casas.")
    + '<section><div class="wrap" style="display:flex;flex-direction:column;gap:24px">' + "".join(bloques) + '</div></section>'
    + """
<section class="alt"><div class="wrap">
  <div class="st"><span class="eyebrow">Qué significa</span><h2>Representación exclusiva, no reventa</h2>
    <p class="lead">Ser representantes exclusivos implica acceso directo al fabricante: stock propio en el país, instrumental completo, soporte técnico de fábrica y trazabilidad desde el origen hasta el quirófano.</p></div>
  <div class="g3">
    <div class="card"><span class="ico">""" + I_CAJA + """</span><h3>Stock local</h3><p>Están en nuestro depósito, no se piden al exterior.</p></div>
    <div class="card"><span class="ico">""" + I_DOC + """</span><h3>Trazabilidad de origen</h3><p>Lote y número de serie, del fabricante al quirófano.</p></div>
    <div class="card"><span class="ico">""" + I_LIBRO + """</span><h3>Documentación oficial</h3><p>Técnicas y material del propio fabricante.</p></div>
  </div>
</div></section>
""" + PIE)


# ================================================================ EDUCACIÓN MÉDICA
def educacion():
    return (cabecera("educacion.html", "Educación médica — Swiss Protech",
                     "Técnicas quirúrgicas por producto, material descargable y webinars. Acceso exclusivo para profesionales registrados.",
                     [("Home", "index.html"), ("Educación médica", "educacion.html")])
    + head("Educación médica", "Técnicas quirúrgicas y formación para profesionales",
           "Material técnico de los fabricantes que representamos, organizado por producto y por línea. El acceso es exclusivo para médicos registrados y activados.")
    + """
<section><div class="wrap">
  <div style="display:grid;grid-template-columns:1fr 420px;gap:36px;align-items:start" class="g-edu">
    <div style="display:flex;flex-direction:column;gap:24px">
      <div class="st" style="margin-bottom:0"><span class="eyebrow">Qué vas a encontrar</span><h2>Todo el material técnico, en un solo lugar</h2></div>
      <div class="g2">
        <div class="card"><span class="ico">""" + I_LIBRO + """</span><h3>Técnicas quirúrgicas</h3><p>El documento oficial, paso a paso.</p></div>
        <div class="card"><span class="ico">""" + I_DOC + """</span><h3>Fichas técnicas</h3><p>Medidas, materiales e indicaciones, en PDF.</p></div>
        <div class="card"><span class="ico">""" + I_PLAY + """</span><h3>Videos de procedimiento</h3><p>Videos con la técnica completa.</p></div>
        <div class="card"><span class="ico">""" + I_USER + """</span><h3>Webinars</h3><p>Con especialistas, en vivo y grabadas.</p></div>
      </div>
    </div>
    <div class="cerrado"><div class="glow"></div>
      <div style="position:relative;display:flex;flex-direction:column;gap:16px">
        <span class="ico" style="background:rgba(0,149,161,.18);border:1px solid rgba(114,197,194,.34)">""" + I_LIBRO.replace('stroke-width="1.8"', 'stroke-width="1.8" stroke="#72C5C2"') + """</span>
        <h3>Acceso exclusivo para médicos</h3>
        <p>Material técnico: el acceso se valida con la matrícula profesional.</p>
        <div class="acts"><a href="contacto.html?q=medico" class="btn-p">Registrarme como médico</a><a href="%s" target="_blank" rel="noopener" class="btn-g">Ya tengo cuenta</a></div>""" % shell.wa("Hola, ya tengo cuenta en el portal medico y necesito acceder al material tecnico.") + """
      </div></div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="st"><span class="eyebrow">Por línea</span><h2>Material disponible por familia de producto</h2>
    <p class="lead">Cada ficha de producto enlaza directo a su técnica quirúrgica. Los 21 productos del catálogo tienen material asociado.</p></div>
  <div class="g3">
    <div class="card"><h3>Cadera</h3><p>Nueve sistemas entre cotilos y vástagos.</p><a href="productos.html" style="font-size:13.5px;font-weight:600;margin-top:auto">Ver los productos de cadera &rarr;</a></div>
    <div class="card"><h3>Rodilla</h3><p>Siete sistemas: Endo-Model y Optetrak.</p><a href="productos.html" style="font-size:13.5px;font-weight:600;margin-top:auto">Ver los productos de rodilla &rarr;</a></div>
    <div class="card"><h3>Cementos</h3><p>Cinco productos: PALACOS, COPAL y PALAMIX.</p><a href="productos.html" style="font-size:13.5px;font-weight:600;margin-top:auto">Ver los cementos &rarr;</a></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="st"><span class="eyebrow">Multimedia</span><h2>Videos y webinars</h2>
    <p class="lead">Material audiovisual oficial de los fabricantes que representamos.</p></div>
  <a href="multimedia.html" class="btn-p">Ir a multimedia
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"></path></svg></a>
</div></section>
<style>@media (max-width: 1000px) { .g-edu { grid-template-columns: 1fr !important; } }</style>
""" + PIE)


# ================================================================ MULTIMEDIA
VIDEOS = [
    ("media/clips/mobilelink_flip.mp4", "Sistema de cotilo MobileLink", "Waldemar Link · Cadera"),
    ("media/clips/mobilelink_poroso.mp4", "Superficie porosa de titanio", "Waldemar Link · Cadera"),
    ("media/clips/lcu_intro.mp4", "Vástago femoral LCU", "Waldemar Link · Cadera"),
    ("media/clips/endomodel_intro.mp4", "Prótesis de rodilla Endo-Model", "Waldemar Link · Rodilla"),
    ("media/clips/endomodel_implantado.mp4", "Endo-Model implantada", "Waldemar Link · Rodilla"),
    ("media/clips/palamix_kit.mp4", "Sistema PALAMIX completo", "Heraeus Medical · Cementos"),
    ("media/clips/palamix_uso.mp4", "Aplicación del cemento óseo", "Heraeus Medical · Cementos"),
]

def multimedia():
    vids = "".join("""<div class="vid"><video src="%s" muted loop playsinline preload="metadata"
      onmouseenter="this.play()" onmouseleave="this.pause()"></video>
      <div class="bd"><b>%s</b><span>%s</span></div></div>""" % v for v in VIDEOS)
    return (cabecera("multimedia.html", "Multimedia y webinars — Swiss Protech",
                     "Videos oficiales de Waldemar Link y Heraeus Medical sobre los sistemas que representamos.",
                     [("Home", "index.html"), ("Multimedia", "multimedia.html")])
    + head("Multimedia", "Videos y webinars",
           "Material audiovisual oficial de los fabricantes que representamos. Pasá el mouse sobre cada video para reproducirlo.")
    + '<section><div class="wrap"><div class="g4">' + vids + """</div>
      <p style="font-size:12.5px;color:var(--mut);margin-top:20px">Material audiovisual de los fabricantes: Waldemar Link GmbH &amp; Co. KG · Heraeus Medical.</p>
    </div></section>

<section class="alt"><div class="wrap">
  <div class="st"><span class="eyebrow">Webinars</span><h2>Formación con especialistas</h2>
    <p class="lead">Sesiones en vivo y grabadas sobre técnica quirúrgica, selección de implante y manejo de complicaciones. El acceso al archivo completo es exclusivo para profesionales registrados.</p></div>
  <div class="g3">
    <div class="card"><span class="ico">""" + I_PLAY + """</span><h3>Próximos webinars</h3><p>Se anuncian por correo a los médicos registrados.</p><a href="contacto.html?q=medico" style="font-size:13.5px;font-weight:600;margin-top:auto">Avisame de la próxima &rarr;</a></div>
    <div class="card"><span class="ico">""" + I_LIBRO + """</span><h3>Archivo grabado</h3><p>A demanda, organizadas por línea de producto.</p><a href="educacion.html" style="font-size:13.5px;font-weight:600;margin-top:auto">Acceder con mi cuenta &rarr;</a></div>
    <div class="card"><span class="ico">""" + I_USER + """</span><h3>Solicitar una sesión</h3><p>A medida, para servicios y equipos quirúrgicos.</p><a href="contacto.html" style="font-size:13.5px;font-weight:600;margin-top:auto">Coordinar una capacitación &rarr;</a></div>
  </div>
</div></section>
""" + PIE)


# ================================================================ PRIVACIDAD
# Texto redactado sobre la Ley 25.326 de Protección de los Datos Personales.
# No incluye datos societarios (CUIT, domicilio legal) porque no los tenemos
# confirmados: ver PENDIENTES.md.
PRIV = [
    ("Qué datos recogemos",
     "Este sitio solo recoge los datos que vos escribís en el formulario de contacto: nombre y apellido, "
     "correo electrónico, teléfono, el dato profesional o institucional que corresponda según quién nos "
     "escribe, y el texto de tu consulta. No pedimos ni almacenamos datos de salud, ni información de "
     "tarjetas o medios de pago."),
    ("Para qué los usamos",
     "Únicamente para responder tu consulta y, si corresponde, coordinar la provisión de un implante o el "
     "acceso al material técnico. No usamos tus datos para publicidad ni los cruzamos con otras bases."),
    ("Cómo se envía tu consulta",
     "Al enviar el formulario, tu consulta se abre como mensaje de WhatsApp hacia el número comercial de "
     "Swiss Protech. Eso significa que el contenido del mensaje también queda sujeto a las políticas de "
     "privacidad de WhatsApp. Si preferís no usar ese canal, podés llamarnos por teléfono a cualquiera de "
     "nuestras dos sedes."),
    ("Con quién los compartimos",
     "No cedemos ni vendemos tus datos a terceros. Solo se comparten dentro de Swiss Protech con el área que "
     "tiene que responderte, y con el centro de salud o el fabricante cuando es imprescindible para "
     "concretar la cirugía que nos consultaste."),
    ("Cuánto tiempo los guardamos",
     "Conservamos las consultas durante el tiempo necesario para atenderlas y para cumplir con las "
     "obligaciones de trazabilidad que exige la normativa de productos médicos. Pasado ese plazo se eliminan."),
    ("Tus derechos",
     "Podés pedirnos en cualquier momento acceder a tus datos, rectificarlos, actualizarlos o suprimirlos, "
     "escribiéndonos por los canales de contacto de este sitio. La AGENCIA DE ACCESO A LA INFORMACIÓN "
     "PÚBLICA, en su carácter de órgano de control de la Ley 25.326, tiene la atribución de atender las "
     "denuncias y reclamos que se interpongan con relación al incumplimiento de las normas sobre protección "
     "de datos personales."),
    ("Cookies y medición",
     "Este sitio no instala cookies de seguimiento ni de publicidad. Las tipografías se cargan desde Google "
     "Fonts y los mapas de la página de contacto desde OpenStreetMap: ambos servicios reciben tu dirección IP "
     "al cargar esos recursos, como en cualquier sitio que los use."),
    ("Cambios en esta política",
     "Si cambiamos la forma en que tratamos los datos, vamos a publicar la versión actualizada en esta misma "
     "página."),
]


def privacidad():
    bloques = "".join(
        '<div class="hito"><div class="a" style="white-space:normal">%s</div><div><p>%s</p></div></div>' % b
        for b in PRIV)
    return (cabecera("privacidad.html", "Políticas de privacidad — Swiss Protech",
                     "Cómo Swiss Protech trata los datos personales que se envían a través de este sitio, "
                     "según la Ley 25.326.",
                     [("Home", "index.html"), ("Políticas de privacidad", "privacidad.html")])
    + head("Políticas de privacidad", "Políticas de privacidad",
           "Qué datos recogemos en este sitio, para qué los usamos y cómo podés pedirnos que los "
           "modifiquemos o los borremos. Redactado según la Ley 25.326 de Protección de los Datos Personales.")
    + """
<section><div class="wrap" style="max-width: 940px;">
  <div class="hitos">""" + bloques + """</div>
  <p style="font-size: 13px; color: var(--mut); margin-top: 26px;">Última actualización: septiembre de 2026.</p>
</div></section>
""" + PIE)


PAGS = {"institucional.html": institucional, "representaciones.html": representaciones,
        "educacion.html": educacion, "multimedia.html": multimedia,
        "privacidad.html": privacidad}

# --------------------------------------------------------------- sitemap/robots
URLS = ["index.html", "productos.html", "producto.html", "proceso.html", "institucional.html",
        "representaciones.html", "educacion.html", "multimedia.html", "contacto.html", "privacidad.html"]
PRIO = {"index.html": "1.0", "productos.html": "0.9", "contacto.html": "0.8", "proceso.html": "0.8"}


def sitemap():
    hoy = "2026-09-01"
    filas = "".join(
        "  <url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n"
        % (shell.BASE_URL, "" if u == "index.html" else u, hoy, PRIO.get(u, "0.7"))
        for u in URLS)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % filas)


def robots():
    return ("User-agent: *\n"
            "Allow: /\n"
            "Disallow: /media/video/\n"
            "Disallow: /media/src/\n\n"
            "Sitemap: %s/sitemap.xml\n" % shell.BASE_URL)


if __name__ == "__main__":
    for nombre, fn in PAGS.items():
        with open(os.path.join(SRC, nombre), "w", encoding="utf-8") as f:
            f.write(fn())
        print("ok", nombre)
    for nombre, fn in [("sitemap.xml", sitemap), ("robots.txt", robots)]:
        with open(os.path.join(SRC, nombre), "w", encoding="utf-8") as f:
            f.write(fn())
        print("ok", nombre)
