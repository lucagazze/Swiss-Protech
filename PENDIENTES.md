# Pendientes — lo que necesitamos de Swiss Protech

El sitio está terminado y publicable tal como está: no hay ningún `[COMPLETAR]`
visible, ningún enlace muerto y ningún dato inventado. Lo que sigue son mejoras
que dependen de información que sólo puede dar la empresa.

---

## 1. Confirmar antes de publicar

| Dato | Qué hay hoy | Por qué |
|---|---|---|
| **WhatsApp** | `+54 9 11 3593 5241` | Derivado del teléfono publicado (11 3593 5241). El sitio viejo tiene el widget pero no muestra el número. **Hay que probar que el número reciba.** Se cambia en `shell.py` → `WA_NUMERO`. |
| **Correo de contacto** | no hay | El sitio viejo no publica ninguno. Si tienen uno comercial conviene sumarlo: hoy el único canal escrito es WhatsApp. |
| **Formulario AFIP F960** | oculto | Necesita el CUIT para armar el link de Data Fiscal. Se carga en `shell.py` → `AFIP_URL` y el ítem aparece solo en el pie. |

## 2. Cobertura geográfica

Saqué del sitio el "17 provincias con cobertura activa" y la lista de provincias:
no está respaldado por ninguna fuente y además mezclaba CABA y Rosario como si
fueran provincias. Hoy el sitio dice lo verificable: **dos sedes propias, Buenos
Aires y Rosario**.

Si la empresa confirma a qué provincias llega con logística propia, se vuelve a
poner el dato con el número real.

## 3. Chile y Uruguay

Confirmado por Mariano (audios del 18-08 y del 16-09): **tienen sede en Chile y
en Uruguay**, y quieren que se vea en Institucional. El sitio ya lo muestra en
el home (banda de datos y bloque "Presencia regional"), en Institucional (los
tres países) y en el pie.

Confirmado también (16-09): **operan con el mismo nombre, Swiss Protech**, y no
hace falta publicar la dirección.

Lo único que falta son **los teléfonos de Chile y de Uruguay**. Hoy el sitio
muestra números de ejemplo en ceros (`+56 9 0000 0000` y `+598 00 000 000`),
sin enlace para marcar. Se cambian en `shell.py` → `TEL_CL` y `TEL_UY`, se pone
`TEL_PAISES_PROVISORIO = False` y se reconstruye.

## 3b. Reunión del 17-09 (Mariano con el cliente)

Hecho:
- **"Más de 25 años"** en todo el sitio y en el video (confirmado por el cliente).
- **LinkSymphoKnee** sumado al catálogo (rodilla, Waldemar Link), con foto oficial de Link.
- **Medical Practice** sumado en Representaciones como la otra marca de la empresa, en Bariloche.

Falta:
- **Sitio web y logo de Medical Practice.** Con la URL se carga en `shell.py` → `MEDICAL_PRACTICE_URL` y aparece el botón.
- **Las tres prótesis "viejas" que hay que sacar.** No quedó claro cuáles son.
  Lo mejor es que el cliente mande **la lista completa corregida de una vez**.
  El catálogo se edita en un solo lugar (`build_productos.py`): tarjetas, filtros,
  contadores y textos ("22 productos", "ocho de rodilla"…) se ajustan solos.

## 4. Fotos que faltan

Tres productos del catálogo no tienen foto en ningún lado y aparecen con el
cartel "FOTO A PEDIDO":

- MobileLink
- Bimobile Cementado
- LCU Cementado y No Cementado

La ficha de cada uno funciona igual (texto, especificaciones y modelo 3D). Con la
foto se cae el cartel solo: se guarda en `assets/<slug>.webp` y se agrega la ruta
en `build_productos.py`.

## 5. Medidas por producto

Las fichas tienen tipo, fijación, material y configuración, pero no las medidas
disponibles de cada sistema. Es lo primero que pregunta un traumatólogo. Si el
fabricante manda las tablas, van en `build_productos.py` → `specs`.

## 6. Contenido propio (recomendado, no bloqueante)

Todas las imágenes del sitio son material oficial de los fabricantes (Waldemar
Link y Heraeus), acreditado como tal. Lo que más levantaría el sitio:

- **Fotos del depósito, del control y del instrumental.** La página "Nuestro
  proceso" es el diferencial de la empresa y hoy se cuenta sólo con texto e
  iconos. Con cinco fotos reales de las cinco etapas pasa a ser lo más fuerte
  del sitio.
- **Calendario de webinars**, para que la sección deje de ser una promesa.
- **Portal médico.** Hoy "Ingresar" y "Registro médico" llevan a Educación
  médica, que explica cómo se pide el acceso. Si en algún momento hay login real,
  se apunta ahí.


## 7. Video institucional — permiso de los fabricantes

El home tiene una pieza de 1 min 2 s (`media/swiss-protech.mp4`) montada con el
material audiovisual oficial de **Waldemar Link** y **Heraeus Medical**, con
rótulos, capítulos y cierre de marca propios. El crédito a los fabricantes ya no
aparece en pantalla: sus logos siguen visibles en el material, que es la
atribución que queda.

**Antes de publicarlo hay que confirmar con Swiss Protech que los acuerdos de
representación cubren el uso de ese material en una pieza de marca propia.** Es
lo habitual en un distribuidor exclusivo, pero es una autorización que sólo puede
dar la empresa. Si algún fabricante no lo permite, se recorta ese capítulo y el
film se vuelve a armar: las fuentes quedan en `media/video/raw/` y el montaje en
`videos-remotion/src/swipro/SwissProtechFilm.tsx`.

**Música:** la cama que sumé al montaje es `control-total/audio/music-bed.mp3`,
la misma que Algoritmia usa en sus propias piezas y en Control Total. Antes de
publicar hay que verificar que su licencia cubra el uso en un proyecto de otro
cliente: muchas licencias de bibliotecas son por proyecto o por canal. Si no lo
cubre, se compra una pista y se cambia en una línea de
`SwissProtechFilm.tsx`.

---

## Lo que quedó fuera de alcance

- **Modelos 3D por producto.** Los productos usan cuatro modelos
  paramétricos (cotilo, vástago, rodilla, cemento) que se configuran por
  producto: cambian agujeros, doble movilidad, cementado, largo, bisagra. Son
  representativos, no son escaneos de cada pieza. Modelar cada sistema reales
  es un proyecto aparte.
- **Traducción a otro idioma.** No estaba en el presupuesto.
- **Producción de fotos y video en las instalaciones.** No estaba en el
  presupuesto.
