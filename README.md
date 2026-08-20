# Swiss Protech — Rediseño web

Propuesta de rediseño del sitio de **Swiss Protech S.A.** ([swipro.com.ar](https://swipro.com.ar)),
importador y representante exclusivo en Argentina de implantes ortopédicos de origen
alemán y norteamericano.

El sitio está en la raíz del repo: se abre directo desde la URL del deploy, o abriendo
`index.html` en cualquier navegador. HTML y CSS puros, sin build ni dependencias.

## Páginas

| Archivo | Página | Qué tiene |
|---|---|---|
| `index.html` | Home | Hero con carrusel 3D de implantes, credenciales, las tres líneas, el proceso, representaciones, cobertura nacional y portal médico |
| `productos.html` | Catálogo | Los 21 productos con filtro por línea (todos / cadera / rodilla / cementos) |
| `proceso.html` | Nuestro proceso | Sección nueva: las cinco etapas de trazabilidad, de depósito a quirófano |
| `producto.html` | Ficha de producto | MobileLink Dual Mobility, con visor 3D que rota arrastrando o con los botones |
| `contacto.html` | Contacto | Selector de país y de tipo de público (médico / obra social / paciente), con formulario y sedes que cambian según la elección |

Todo responsive: probado a 390, 768 y 1440 px, sin desborde horizontal, con menú
desplegable en celular y botones de 48 px o más.

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
  el sitio actual; en el catálogo figuran con un marcador "foto a solicitar".
- **Medidas por producto:** la ficha las tiene como `[COMPLETAR CON DATOS DEL FABRICANTE]`.

## Cómo se regenera

Los `.dc.html` son las maquetas fuente (un archivo por pantalla). El script
`build_site.py` las convierte en las páginas estáticas de la raíz: resuelve los
estilos, arma la navegación, agrega el menú de celular, las reglas responsive y el
JavaScript de los filtros, el visor 3D y el selector de contacto.

```
python -u build_site.py
```

Escribe todo en `site/`; después se copian los `.html` a la raíz.

---

Diseño y desarrollo: [Algoritmia](https://algoritmiadesarrollos.com.ar) · +54 9 3476 24-5523
