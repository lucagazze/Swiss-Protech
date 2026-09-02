# Pendientes — lo que necesitamos de Swiss Protech

El sitio está terminado y publicable tal como está: no hay ningún `[COMPLETAR]`
visible, ningún enlace muerto y ningún dato inventado. Lo que sigue son mejoras
que dependen de información que sólo puede dar la empresa.

---

## 1. Confirmar antes de publicar

| Dato | Qué hay hoy | Por qué |
|---|---|---|
| **Años de trayectoria** | **"más de 20"** | Es lo que dice hoy swipro.com.ar textual. La página institucional del sitio viejo decía 25. Si son 25, se cambia `TRAYECTORIA` en `shell.py` y las tres menciones del home/institucional. |
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

Mariano mencionó que venden a Chile y Uruguay. El selector de país en Contacto
funciona, y para esos dos países dice la verdad: **la consulta la toma el equipo
comercial de Buenos Aires**. No inventé oficinas ni teléfonos locales.

Falta confirmar:
- ¿Hay sede física o representante local en alguno de los dos?
- ¿Teléfono o WhatsApp local?

Con eso, en `build_site.py` → `JS_CONTACTO` → objeto `P` se completan `cl` y `uy`.

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

- **Modelos 3D por producto.** Los 21 productos usan cuatro modelos
  paramétricos (cotilo, vástago, rodilla, cemento) que se configuran por
  producto: cambian agujeros, doble movilidad, cementado, largo, bisagra. Son
  representativos, no son escaneos de cada pieza. Modelar los 21 sistemas reales
  es un proyecto aparte.
- **Traducción a otro idioma.** No estaba en el presupuesto.
- **Producción de fotos y video en las instalaciones.** No estaba en el
  presupuesto.
