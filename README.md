# Swiss Protech — Rediseño web

Propuesta de rediseño del sitio de **Swiss Protech S.A.** ([swipro.com.ar](https://swipro.com.ar)),
importador y representante exclusivo en Argentina de implantes ortopédicos de origen
alemán y norteamericano.

## Ver el diseño

Abrí **`index.html`** en cualquier navegador, o entrá a la URL del deploy. Es un
archivo autónomo: trae las seis pantallas sobre un canvas con zoom y desplazamiento,
sin servidor ni dependencias. Cada pantalla se puede abrir a pantalla completa y
exportar como PNG o PDF desde la barra superior.

## Pantallas

| Archivo | Pantalla | Qué muestra |
|---|---|---|
| `Main.dc.html` | Home | Hero con carrusel 3D de implantes, credenciales, las tres líneas, el proceso, representaciones y cobertura nacional |
| `Productos.dc.html` | Catálogo | Los 21 productos con filtro por línea (cadera, rodilla, cementos) |
| `Proceso.dc.html` | Nuestro proceso | Sección nueva: las cinco etapas de trazabilidad, de depósito a quirófano |
| `Ficha.dc.html` | Ficha de producto | MobileLink Dual Mobility, con visor 3D de rotación y zoom |
| `Contacto.dc.html` | Contacto | Selector de país y de tipo de público (médico / financiador / paciente) |
| `Mobile.dc.html` | Home en celular | La misma home a 390 px, con barra de acción fija |

`canvas.json` define la posición de cada pantalla en el canvas y las notas al margen.

## Identidad

Todos los valores están levantados del sitio actual, no inventados:

| | |
|---|---|
| Tipografía | Montserrat (300 / 400 / 500 / 600 / 700 / 800) |
| Teal de marca | `#0095A1` |
| Teal claro | `#72C5C2` |
| Azul secundario | `#1E73BE` |
| Tinta | `#10222A` · texto `#222222` |
| Grises | `#69727D` · `#A7A9AC` |
| Fondo | `#F7F8F9` |

Las imágenes de `assets/` son las fotos originales de producto y los logotipos de
Swiss Protech, redimensionadas y optimizadas.

## Contenido

Los 21 productos están con el nombre y la descripción textual del sitio actual:

- **Cadera (9)** — Bimobile Cementado, Crown Cup, Element, LCU Cementado y No Cementado,
  Lubinus Cup, Lubinus SPII Revision, MobileLink, MobileLink Dual Mobility, MP Link
- **Rodilla (7)** — Endomodel Modular, Endomodel Hinged Modular, Endomodel Standard,
  Optetrak CC, Optetrak Hi-Flex, Optetrak Logic, Uni Sled
- **Cementos (5)** — Copal G+C, Palacos MV y MV+G, Palacos R, Palamix Pistola,
  Palamix Uno o Duo

Marcas representadas: **Waldemar Link** (Hamburgo, 1948), **Advita Ortho** y
**Heraeus Medical**.

## Pendiente de confirmar con el cliente

- **Trayectoria:** el home del sitio actual dice "más de 20 años" y la página
  institucional dice "más de 25". Acá se usó 25.
- **Chile y Uruguay:** el selector de país está armado, pero el sitio actual solo
  publica las dos sedes argentinas. Esos datos quedaron como `[COMPLETAR]`.
- **Tres fotos faltantes:** MobileLink, Bimobile Cementado y LCU no tienen imagen en
  el sitio actual; en el catálogo figuran como marcador "foto a solicitar".

## Formato

Los `.dc.html` son componentes de Claude Design: HTML estándar con un bloque
`<helmet>` para los estilos y una clase de lógica al pie. Se editan como HTML común.

---

Diseño: [Algoritmia](https://algoritmiadesarrollos.com.ar)
