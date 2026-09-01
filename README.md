# Swiss Protech — Rediseño web

Propuesta de rediseño del sitio de **Swiss Protech S.A.** ([swipro.com.ar](https://swipro.com.ar)),
importador y representante exclusivo en Argentina de implantes ortopédicos de origen
alemán y norteamericano.

El sitio está en la raíz del repo: se abre directo desde la URL del deploy, o abriendo
`index.html` en cualquier navegador. HTML, CSS y JS puros: no necesita servidor de aplicación.

## Páginas

| Archivo | Página | Qué tiene |
|---|---|---|
| `index.html` | Home | Hero vertical: título y el video institucional. Después credenciales, las tres líneas, el proceso, representaciones, sedes y portal médico |
| `productos.html` | Catálogo | Los 21 productos con filtro cruzado por línea y por marca |
| `proceso.html` | Nuestro proceso | Sección nueva: las cinco etapas de trazabilidad, de depósito a quirófano |
| `producto.html` | Ficha de producto | Los 21 productos (`?p=slug`), con visor 3D, galería del fabricante y especificaciones |
| `contacto.html` | Contacto | Selector de país y de tipo de público (médico / obra social / paciente), con formulario real que arma la consulta y la abre por WhatsApp |
| `institucional.html` | Institucional | Trayectoria, hitos y las dos sedes |
| `representaciones.html` | Representaciones | Link, Advita y Heraeus, con los productos de cada uno |
| `educacion.html` | Educación médica | Técnicas quirúrgicas, fichas y webinars |
| `multimedia.html` | Multimedia | Videos oficiales de los fabricantes |
| `privacidad.html` | Privacidad | Política según la Ley 25.326 |

Todo responsive: probado a 390, 768 y 1440 px, sin desborde horizontal, con menú
desplegable en celular y botones de 48 px o más.

## Video institucional

`media/swiss-protech.mp4` — 1 min 2 s, 720p, con cama musical, en el hero del home con
póster y carga diferida (`preload="none"`): la página carga liviana y el video
se baja recién al tocar play. Montado en Remotion a partir del material oficial
de los fabricantes.

Orden: apertura con la corredora (7 s), **Rodilla**, Cadera, Cementos,
Trazabilidad y cierre de marca. Rodilla va primero para que el video entre por
la misma imagen que el visitante ya está viendo en el póster.

En el hero corre solo un bucle mudo de 6 s (`media/swiss-protech-loop.mp4`:
2 s de la corredora y después el implante) y el botón cambia a la pieza
completa, con audio.

El audio se normaliza a **−18 LUFS en el encode**, no en Remotion: la cama de
origen es muy baja y sin ese paso queda a −36 LUFS, es decir inaudible.

- Montaje: `videos-remotion/src/swipro/SwissProtechFilm.tsx` (composición `SwissProtechFilm`)
- Segmentos ya cortados: `media/film/` · fuentes: `media/video/raw/`
- Master 1080p: `media/swiss-protech-1080-master.mp4`

```
# recortar de nuevo un segmento y volver a montar
cd videos-remotion
rm -rf node_modules/.cache          # webpack cachea mal y rompe el bundle
npx remotion render src/index.ts SwissProtechFilm out/SwissProtechFilm.mp4 --codec=h264 --crf=18
```

## Armazón compartido

`shell.py` es la fuente única de la barra superior, el CTA de cierre, el pie, los
datos de contacto y el JS de animaciones. Los tres builders lo consumen: si
cambia un teléfono o una sede, se cambia ahí y se reconstruye todo.

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

Ver **[PENDIENTES.md](PENDIENTES.md)**. Nada de eso bloquea la publicación: el
sitio no tiene marcadores `[COMPLETAR]` visibles ni enlaces muertos.

## Cómo se regenera

Los `.dc.html` son las maquetas fuente (un archivo por pantalla). El script
`build_site.py` las convierte en las páginas estáticas de la raíz: resuelve los
estilos, arma la navegación, agrega el menú de celular, las reglas responsive y el
JavaScript de los filtros, el visor 3D y el selector de contacto.

```
python -u build_productos.py    # js/productos.js, el catálogo
python -u build_paginas.py      # institucional, representaciones, educación, multimedia,
                                # privacidad, sitemap.xml y robots.txt
python -u build_site.py         # index, productos, proceso, contacto y la ficha
```

`build_site.py` copia los `.html` a la raíz, inyecta el armazón en
`producto.html` (que se mantiene a mano) y deja en `site/` una copia completa
lista para subir: las 10 páginas más `assets/`, `js/`, `vendor/`, `media/`,
`sitemap.xml` y `robots.txt`. Al terminar avisa si quedó alguna referencia rota.
Es idempotente: se puede correr las veces que haga falta.

**Qué se publica:** el contenido de `site/`. La raíz del repo sirve para
desarrollar; `site/` es lo que va al hosting.

---

Diseño y desarrollo: [Algoritmia](https://algoritmiadesarrollos.com.ar) · +54 9 3476 24-5523
