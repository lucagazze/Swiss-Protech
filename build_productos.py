# -*- coding: utf-8 -*-
"""
Genera js/productos.js: los 21 productos con texto real de swipro.com.ar y el
inventario de medios (clips del fabricante, stills, vistas recreadas, visor 3D).
Ejecutar:  python -u build_productos.py
"""
import json, os, re

SRC = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(SRC, "productos_swipro.json"), encoding="utf-8"))

def limpio(s):
    s = (s or "").replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def parrafos(s):
    s = limpio(s)
    out = []
    for p in re.split(r"\n+", s):
        p = p.strip(" -•·")
        if len(p) > 2:
            out.append(p)
    return out

# ---------------------------------------------------------------- inventario de medios
CL = lambda n, t: {"src": "media/clips/%s.mp4" % n, "gif": "media/gifs/%s.gif" % n if os.path.exists(os.path.join(SRC, "media/gifs/%s.gif" % n)) else None, "titulo": t, "fuente": FUENTE[n]}
ST = lambda n, t: {"src": "media/stills/%s.jpg" % n, "titulo": t}
VW = lambda n, t: {"src": "media/views/%s.jpeg" % n, "titulo": t, "recreada": True}

FUENTE = {
    "mobilelink_flip": "Video oficial Waldemar Link", "mobilelink_poroso": "Video oficial Waldemar Link",
    "lcu_intro": "Video oficial Waldemar Link", "endomodel_intro": "Video oficial Waldemar Link",
    "endomodel_implantado": "Video oficial Waldemar Link", "palamix_kit": "Video oficial Heraeus Medical",
    "palamix_uso": "Video oficial Heraeus Medical",
}

ML_CLIPS = [CL("mobilelink_flip", "Casquete y componentes del sistema"), CL("mobilelink_poroso", "Estructura porosa de titanio")]
ML_STILLS = [ST("mobilelink_explotado", "Vista explotada: casquete, tapones y tornillos"), ST("mobilelink_ensamblado", "Casquete con inserto"),
             ST("mobilelink_implantado", "Posicionado en el acetábulo"), ST("mobilelink_liner_rosa", "Revestimiento de polietileno"),
             ST("mobilelink_poroso", "Superficie porosa")]
EM_CLIPS = [CL("endomodel_intro", "Prótesis Endo-Model"), CL("endomodel_implantado", "Endo-Model implantada")]
EM_STILLS = [ST("endomodel_render", "Componentes femoral y tibial"), ST("endomodel_implantado", "Resultado final")]
PX_CLIPS = [CL("palamix_kit", "Sistema PALAMIX completo"), CL("palamix_uso", "Aplicación del cemento")]

# ---------------------------------------------------------------- catálogo
# slug, clave swipro (None si no tiene ficha propia), línea, fabricante, imagen, extras
P = [
  # ---- CADERA
  dict(slug="mobilelink-dual-mobility", key="mobilelink-dual-mobility-2", linea="Cadera", marca="Waldemar Link", img="assets/mobilelink.webp",
       visor3d=True, clips=ML_CLIPS, stills=ML_STILLS,
       specs=[["Tipo", "Cotilo acetabular"], ["Fijación", "No cementado"], ["Configuración", "Doble movilidad"], ["Inserto", "EndoDur, para revestimientos BiMobile"]],
       destacados=["Menor riesgo de luxación y mayor rango de movilidad", "Superficie interna pulida: menos desgaste", "Revestimiento autocentrante"]),
  dict(slug="mobilelink", key=None, nombre="MOBILELINK", bajada="Sistema de cotilo no cementado", linea="Cadera", marca="Waldemar Link", img=None,
       visor3d=True, clips=ML_CLIPS, stills=ML_STILLS,
       desc=["Cotilo hemisférico no cementado de titanio con superficie porosa para la fijación biológica. Base del sistema modular MobileLink, que admite insertos estándar y de doble movilidad."],
       specs=[["Tipo", "Cotilo acetabular"], ["Fijación", "No cementado"], ["Press-fit", "1,6 mm integrado"], ["Adaptador opcional", "Neutro, +4 mm offset, 10° y 20° de inclinación"]],
       destacados=["Press-fit integrado para estabilidad primaria", "Orificios para tornillos de fijación opcional", "Compatible con insertos de doble movilidad"]),
  dict(slug="bimobile", key=None, nombre="BIMOBILE CEMENTADO", bajada="Sistema de cotilo cementado de doble movilidad", linea="Cadera", marca="Waldemar Link", img=None,
       desc=["Cotilo cementado de doble movilidad. Sus revestimientos de polietileno son los mismos que aloja el inserto de doble movilidad del sistema MobileLink."],
       specs=[["Tipo", "Cotilo acetabular"], ["Fijación", "Cementado"], ["Configuración", "Doble movilidad"]],
       destacados=["Doble movilidad con fijación cementada", "Revestimientos compatibles con el sistema MobileLink"]),
  dict(slug="crown-cup", key="crown", linea="Cadera", marca="Advita Ortho (Novation®)", img="assets/crown-cup.webp",
       specs=[["Tipo", "Cotilo acetabular"], ["Fijación", "No cementado"], ["Material", "Titanio, diseño hemisférico"], ["Revestimientos", "XLE: polietileno altamente reticulado con vitamina E"]],
       destacados=["Amplia gama de opciones acetabulares", "Estabilidad inicial para la fijación biológica", "Bajo desgaste con resistencia mecánica"]),
  dict(slug="element", key="element", linea="Cadera", marca="Advita Ortho (Novation®)", img="assets/element.webp",
       specs=[["Tipo", "Vástago femoral"], ["Fijación", "No cementado"], ["Filosofía", "Conservación de hueso"]],
       destacados=["Más de 25 años de uso clínico", "Diseño que conserva hueso"]),
  dict(slug="lcu", key=None, nombre="LCU CEMENTADO Y NO CEMENTADO", bajada="Sistema de vástagos cementados y no cementados", linea="Cadera", marca="Waldemar Link", img=None,
       clips=[CL("lcu_intro", "Vástago LCU")], stills=[ST("lcu_render", "Vástago LCU")],
       desc=["Sistema de vástagos femorales de LINK disponible en versión cementada y no cementada, con un mismo instrumental para ambas técnicas."],
       specs=[["Tipo", "Vástago femoral"], ["Fijación", "Cementado o no cementado"]],
       destacados=["Una sola plataforma para ambas fijaciones", "Instrumental común"]),
  dict(slug="lubinus-cup", key="lubinus-cup", linea="Cadera", marca="Waldemar Link", img="assets/lubinus-cup.webp",
       specs=[["Tipo", "Cotilo acetabular"], ["Fijación", "Cementado"], ["Material", "UHMWPE"], ["Versiones", "Autorretentivo y estándar"]],
       destacados=["Cotilo cementado de polietileno", "Estabilidad directa en el revestimiento de cemento"]),
  dict(slug="lubinus-spii", key="lubinus-spii-revision", linea="Cadera", marca="Waldemar Link", img="assets/lubinus-spii.webp",
       stills=[ST("lubinus_render", "Vástago Lubinus"), ST("lubinus_spii", "Lubinus SP II")], vistas=[VW("lubinus-spii_lado", "Perfil")],
       specs=[["Tipo", "Vástago de revisión"], ["Fijación", "Cementado"], ["Cono", "12/14 mm"], ["Longitudes", "200 · 250 · 300 mm"], ["Ángulo CCD", "126°"], ["Lados", "Derecho e izquierdo (anatómico)"]],
       destacados=["40 años de uso clínico", "Supervivencia de hasta 92,3 % a 23 años", "Diseño adaptado a la forma anatómica del fémur"]),
  dict(slug="mp-link", key="mp-link", linea="Cadera", marca="Waldemar Link", img="assets/mp-link.webp",
       specs=[["Tipo", "Vástago modular de revisión"], ["Fijación", "Distal, no cementado (alternativa cementada)"]],
       destacados=["Flexibilidad y seguridad intraoperatoria", "Reconstrucción modular"]),
  # ---- RODILLA
  dict(slug="endomodel-modular", key="endomodel-m-rotational-o-hinged-knee", linea="Rodilla", marca="Waldemar Link", img="assets/endomodel-mod.webp",
       clips=EM_CLIPS, stills=EM_STILLS,
       specs=[["Tipo", "Prótesis modular abisagrada, constreñida, rotatoria"], ["Flexión", "Hasta 142°"], ["Vástagos", "Cementados y no cementados, 50 a 280 mm"], ["Puntas", "Tapas de UHMWPE en forma de estrella"]],
       destacados=["Principio de baja fricción con rotación fisiológica", "Transmisión amortiguada de la fuerza", "Segmentos especiales para revisión y tumores"]),
  dict(slug="endomodel-hinged", key="endomodel-m-rotational-o-hinged-knee-antialergica", linea="Rodilla", marca="Waldemar Link", img="assets/endomodel-hinged.webp",
       clips=EM_CLIPS, stills=EM_STILLS,
       specs=[["Tipo", "Prótesis modular abisagrada, constreñida, bisagra simple"], ["Flexión", "Hasta 165°, sin rotación"]],
       destacados=["Principio de baja fricción", "Bisagra simple para máxima constricción"]),
  dict(slug="endomodel-standard", key="endomodel", linea="Rodilla", marca="Waldemar Link", img="assets/endomodel-std.webp",
       clips=EM_CLIPS, stills=EM_STILLS,
       specs=[["Tipo", "Prótesis abisagrada, constreñida, rotatoria"], ["Uso", "Artroplastias primarias y de revisión"]],
       destacados=["Más de 40 años de uso clínico", "Prótesis rotaria o de bisagra"]),
  dict(slug="optetrak-cc", key="optetrak-contr-condilar", linea="Rodilla", marca="Advita Ortho (Optetrak®)", img="assets/optetrak-cc.webp",
       specs=[["Tipo", "Prótesis de revisión de rodilla"], ["Diseño", "Constreñido condilar"]],
       destacados=["Cartera de implantes e instrumentos de revisión", "Resultados reproducibles"]),
  dict(slug="optetrak-hiflex", key="optetrak-hi-flex", linea="Rodilla", marca="Advita Ortho (Optetrak®)", img="assets/optetrak-hiflex.webp",
       specs=[["Tipo", "Prótesis primaria de rodilla"], ["Diseño", "Alta flexión, patentado"]],
       destacados=["Basado en el éxito clínico del sistema Optetrak"]),
  dict(slug="optetrak-logic", key="optetrak-logic", linea="Rodilla", marca="Advita Ortho (Optetrak®)", img="assets/optetrak-logic.webp",
       vistas=[VW("optetrak-logic_atras", "Vista posterior")],
       specs=[["Tipo", "Prótesis primaria de rodilla"], ["Instrumental", "LPI, de bajo perfil"], ["Resección ósea", "30 % menos que un cajón tradicional (PS)"], ["Congruencia fémoro-tibial", "0,96"]],
       destacados=["Estrés por contacto mínimo", "Deslizamiento rotuliano optimizado", "Preparación de la escotadura más sencilla y reproducible"]),
  dict(slug="uni-sled", key="uni-sled", linea="Rodilla", marca="Waldemar Link", img="assets/uni-sled.webp",
       specs=[["Tipo", "Prótesis unicompartimental"], ["Primer implante", "1969"], ["Diseño actual", "Sin cambios desde 1981"], ["Supervivencia", "80 % a 25 años · 97 % a 12 años"]],
       destacados=["Longevidad demostrada", "Máxima conservación de hueso y tejidos blandos"]),
  # ---- CEMENTOS
  dict(slug="copal", key="copal-gc", linea="Cementos", marca="Heraeus Medical", img="assets/copal.webp",
       specs=[["Tipo", "Cemento óseo con antibiótico"], ["Antibióticos", "Gentamicina + clindamicina"]],
       destacados=["Amplio espectro de actividad", "Indicado en revisiones con riesgo de infección"]),
  dict(slug="palacos-mv", key="palacos-mv-y-mvg", linea="Cementos", marca="Heraeus Medical", img="assets/palacos-mv.webp",
       specs=[["Tipo", "Cemento óseo"], ["Viscosidad", "Media"], ["Versiones", "MV y MV+G (con gentamicina)"]],
       destacados=["Profilaxis antibiótica con gentamicina"]),
  dict(slug="palacos-r", key="palacos-r", linea="Cementos", marca="Heraeus Medical", img="assets/palacos-r.webp",
       specs=[["Tipo", "Cemento óseo"], ["Viscosidad", "Alta"]],
       destacados=["Materias primas de alta calidad constante", "Fórmula probada"]),
  dict(slug="palamix-gun", key="palamix-pistola-para-cemento", linea="Cementos", marca="Heraeus Medical", img="assets/palamix-gun.webp",
       clips=PX_CLIPS, stills=[ST("palamix_kit", "Sistema PALAMIX")], vistas=[VW("palamix-gun_atras", "Vista posterior")],
       specs=[["Tipo", "Pistola para cemento"], ["Uso", "Con cartuchos del sistema de mezcla al vacío PALAMIX"]],
       destacados=["Aplicación segura y sin esfuerzo", "Cemento expulsado con elevada presión"]),
  dict(slug="palamix-uno", key="palamix-uno-o-duo", linea="Cementos", marca="Heraeus Medical", img="assets/palamix-uno.webp",
       clips=PX_CLIPS, stills=[ST("palamix_kit", "Sistema PALAMIX")],
       specs=[["Tipo", "Sistema de mezcla al vacío"], ["Versiones", "UNO y DUO"]],
       destacados=["Técnica de cementación moderna", "Mezcla en cartucho al vacío"]),
]

M3D = {'mobilelink-dual-mobility': ('cotilo', {'dobleMovilidad': True, 'agujeros': 3}), 'mobilelink': ('cotilo', {'dobleMovilidad': False, 'agujeros': 3}), 'bimobile': ('cotilo', {'dobleMovilidad': True, 'cementado': True, 'agujeros': 0}), 'crown-cup': ('cotilo', {'dobleMovilidad': False, 'agujeros': 4}), 'lubinus-cup': ('cotilo', {'dobleMovilidad': False, 'cementado': True, 'agujeros': 0}), 'element': ('vastago', {'revestido': True, 'largo': 2.7}), 'lcu': ('vastago', {'revestido': True, 'largo': 3.0}), 'lubinus-spii': ('vastago', {'cementado': True, 'revestido': False, 'largo': 3.2}), 'mp-link': ('vastago', {'modular': True, 'revestido': False, 'largo': 2.6}), 'endomodel-modular': ('rodilla', {'bisagra': True, 'vastagos': True}), 'endomodel-hinged': ('rodilla', {'bisagra': True, 'vastagos': True}), 'endomodel-standard': ('rodilla', {'bisagra': True, 'vastagos': True}), 'optetrak-cc': ('rodilla', {'bisagra': False, 'vastagos': True}), 'optetrak-hiflex': ('rodilla', {'bisagra': False, 'vastagos': False}), 'optetrak-logic': ('rodilla', {'bisagra': False, 'vastagos': False}), 'uni-sled': ('rodilla', {'unicompartimental': True}), 'copal': ('cemento', {'tipo': 'sobre', 'antibiotico': True}), 'palacos-mv': ('cemento', {'tipo': 'sobre', 'antibiotico': True}), 'palacos-r': ('cemento', {'tipo': 'sobre', 'antibiotico': False}), 'palamix-gun': ('cemento', {'tipo': 'pistola'}), 'palamix-uno': ('cemento', {'tipo': 'cartucho'})}

OUT = {}
for p in P:
    j = J.get(p["key"]) if p.get("key") else None
    nombre = limpio(j["h1"]) if j and j.get("h1") else p.get("nombre")
    bajada = limpio(j["short"]) if j and j.get("short") else p.get("bajada", "")
    desc = parrafos(j.get("long")) if j and j.get("long") else p.get("desc", [])
    OUT[p["slug"]] = {
        "slug": p["slug"], "nombre": nombre, "bajada": bajada, "linea": p["linea"], "marca": p["marca"],
        "img": p.get("img"), "desc": desc, "specs": p.get("specs", []), "destacados": p.get("destacados", []),
        "visor3d": p["slug"] in M3D, "modelo3d": M3D.get(p["slug"], [None, {}])[0],
        "config3d": M3D.get(p["slug"], [None, {}])[1],
        "clips": p.get("clips", []), "stills": p.get("stills", []),
        "vistas": p.get("vistas", []), "url": (j or {}).get("url"),
    }

os.makedirs(os.path.join(SRC, "js"), exist_ok=True)
with open(os.path.join(SRC, "js", "productos.js"), "w", encoding="utf-8") as f:
    f.write("// Generado por build_productos.py — no editar a mano\n")
    f.write("window.PRODUCTOS = " + json.dumps(OUT, ensure_ascii=False, indent=1) + ";\n")
    f.write("window.ORDEN = " + json.dumps([p["slug"] for p in P]) + ";\n")

faltan = [s for s, v in OUT.items() if not v["img"]]
print("productos:", len(OUT), "| sin foto:", faltan)
print("con visor 3D:", sum(1 for v in OUT.values() if v["visor3d"]), "de", len(OUT))
for s_, v in OUT.items():
    if not v["visor3d"]: print("  SIN 3D:", s_)
print("con video:", [s for s, v in OUT.items() if v["clips"]])
