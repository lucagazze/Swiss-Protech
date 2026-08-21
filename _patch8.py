# -*- coding: utf-8 -*-
"""1) los cementos no llevan contexto anatomico
   2) cada producto tiene rasgos propios: vastagos y rodillas dejan de repetirse"""
import io

# ================================================================ modelos.js
p = "js/modelos.js"
s = io.open(p, encoding="utf-8").read()

# --- 1) cementos sin anatomia
s = s.replace("return { raiz, tapas, puntos, explotar, anatomia: 'campo' };",
              "return { raiz, tapas, puntos, explotar, anatomia: null };")

# --- 2) VASTAGO: perfil, collar, estrias y curvatura segun el producto
viejo = """  // perfil del vastago: ancho arriba (metafisis), afinado abajo (diafisis)
  const perfil = [];
  const pasos = 26;
  for (let i = 0; i <= pasos; i++) {
    const t = i / pasos;
    const y = 0.55 - t * largo;
    const r = 0.30 * Math.pow(1 - t, 0.62) + 0.055;
    perfil.push(new THREE.Vector2(r, y));
  }
  const geoCuerpo = new THREE.LatheGeometry(perfil, 72);
  geoCuerpo.scale(1, 1, 0.62);                       // seccion ovalada, como el hueso"""
nuevo = """  // perfil del vastago: ancho arriba (metafisis), afinado abajo (diafisis)
  // afina = que tan rapido se adelgaza · aplana = seccion mas ovalada · curva = forma anatomica
  const afina = cfg.afina || 0.62, aplana = cfg.aplana || 0.62, curva = cfg.curva || 0;
  const perfil = [];
  const pasos = 30;
  for (let i = 0; i <= pasos; i++) {
    const t = i / pasos;
    const y = 0.55 - t * largo;
    const r = 0.30 * Math.pow(1 - t, afina) + (cfg.puntaFina ? 0.035 : 0.055);
    perfil.push(new THREE.Vector2(r, y));
  }
  const geoCuerpo = new THREE.LatheGeometry(perfil, 72);
  geoCuerpo.scale(1, 1, aplana);                     // seccion ovalada, como el hueso
  if (curva) {                                       // curvatura anatomica del canal femoral
    const pos = geoCuerpo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i), k = Math.max(0, (0.55 - y) / largo);
      pos.setX(i, pos.getX(i) + curva * k * k * largo * 0.5);
    }
    pos.needsUpdate = true; geoCuerpo.computeVertexNormals();
  }"""
assert viejo in s, "perfil del vastago"
s = s.replace(viejo, nuevo)

# collar de apoyo (Lubinus) y estrias longitudinales (LCU)
s = s.replace("  cuerpo.add(hombro, cono);",
"""  cuerpo.add(hombro, cono);

  // collar de apoyo sobre el corte del cuello (vastagos cementados anatomicos)
  let collar = null;
  if (cfg.collar) {
    collar = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.30, 0.075, 56), m.pulido);
    collar.scale.set(1, 1, aplana); collar.position.set(-0.05, 0.60, 0); collar.rotation.z = 0.16;
    collar.castShadow = true; cuerpo.add(collar);
  }
  // estrias longitudinales (mejoran la estabilidad rotacional)
  const estrias = [];
  if (cfg.estrias) {
    for (let i = 0; i < cfg.estrias; i++) {
      const a = (i / cfg.estrias) * Math.PI * 2;
      const e = new THREE.Mesh(new THREE.BoxGeometry(0.022, largo * 0.62, 0.055), m.mate);
      e.position.set(Math.cos(a) * 0.20, -0.30, Math.sin(a) * 0.20 * aplana);
      e.lookAt(0, -0.30, 0); cuerpo.add(e); estrias.push(e);
    }
  }""")

# puntos propios segun los rasgos
s = s.replace("""    { titulo: 'Hombro y apoyo metafisario',""",
"""""" + """    { titulo: cfg.collar ? 'Collar de apoyo' : (cfg.estrias ? 'Estrias antirrotacionales' : 'Hombro y apoyo metafisario'),""")
s = s.replace("""      texto: 'El hombro apoya sobre el corte del cuello femoral y transmite la carga al hueso proximal.',
      obj: cuerpo, pos: V(0.22, 0.62, 0.16), focos: [hombro], camLocal: V(0.48, 0.52, 0.71), margen: 2.4, modo: 'normal' },""",
"""      texto: cfg.collar
        ? 'El collar apoya directamente sobre el corte del cuello femoral: frena el hundimiento del vastago y reparte la carga al hueso proximal.'
        : (cfg.estrias
          ? 'Las estrias longitudinales muerden el hueso o el cemento y evitan que el vastago rote dentro del canal.'
          : 'El hombro apoya sobre el corte del cuello femoral y transmite la carga al hueso proximal.'),
      obj: cuerpo, pos: V(0.22, 0.55, 0.16), focos: cfg.collar ? [collar, hombro] : (estrias.length ? estrias : [hombro]),
      camLocal: V(0.48, 0.42, 0.77), margen: cfg.estrias ? 1.8 : 2.4, modo: 'normal' },""")

# --- 3) RODILLA: rasgos propios de cada sistema
s = s.replace("  const bisagra = !!cfg.bisagra, uni = !!cfg.unicompartimental;\n  const vastagos = cfg.vastagos !== false && !uni;",
"""  const bisagra = !!cfg.bisagra, uni = !!cfg.unicompartimental;
  const vastagos = cfg.vastagos !== false && !uni;
  const rotatoria = cfg.rotatoria !== false;          // bisagra que ademas rota
  const modular = !!cfg.modular;                       // segmentos intercambiables
  const altaFlexion = !!cfg.altaFlexion;               // condilo posterior mas largo
  const cajaRev = !!cfg.cajaRevision;                  // caja intercondilea de revision
  const largoVast = cfg.largoVastago || 1.35;""")

# condilo mas largo en alta flexion
s = s.replace("    const g = new THREE.TorusGeometry(0.52, 0.185, 20, 80, 4.05);\n    g.rotateZ(-2.86);",
              "    const g = new THREE.TorusGeometry(0.52, 0.185, 20, 80, altaFlexion ? 4.55 : 4.05);\n    g.rotateZ(altaFlexion ? -3.16 : -2.86);")

# caja de revision + pivote rotatorio
s = s.replace("  // ---- bisagra\n  let ejeBisagra = null;",
"""  // ---- caja intercondilea de revision
  let caja = null;
  if (cajaRev) {
    caja = new THREE.Mesh(new THREE.BoxGeometry(sep * 1.5, 0.52, 0.52), m.pulido);
    caja.position.set(0, 0.10, -0.06); caja.castShadow = true;
    femoral.add(caja);
  }
  // ---- pivote rotatorio (bisagra que ademas permite rotacion axial)
  let pivote = null;
  if (bisagra && rotatoria) {
    pivote = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.10, 0.62, 32), m.cuello);
    pivote.position.set(0, -0.42, 0); pivote.castShadow = true;
    tibial.add(pivote);
  }
  // ---- segmentos modulares del vastago
  const segmentos = [];
  if (modular) {
    for (let i = 0; i < 2; i++) {
      const an = new THREE.Mesh(new THREE.TorusGeometry(0.155, 0.028, 12, 44), m.cuello);
      an.rotation.x = Math.PI / 2; an.position.y = 0.92 + i * 0.42;
      femoral.add(an); segmentos.push(an);
    }
  }
  // ---- bisagra
  let ejeBisagra = null;""")

s = s.replace("    vastFem = new THREE.Mesh(new THREE.CylinderGeometry(0.135, 0.095, 1.35, 40), m.mate);\n    vastFem.position.y = 1.28;",
              "    vastFem = new THREE.Mesh(new THREE.CylinderGeometry(0.135, 0.095, largoVast, 40), m.mate);\n    vastFem.position.y = 0.60 + largoVast / 2;")

# puntos nuevos segun el rasgo
s = s.replace("""  if (bisagra) puntos.push({
    titulo: 'Eje de bisagra',
    texto: 'Vincula el componente femoral con el tibial: aporta la constriccion necesaria cuando los ligamentos no pueden sostener la rodilla.',""",
"""  if (cajaRev) puntos.push({
    titulo: 'Caja intercondilea de revision',
    texto: 'La caja aloja el poste alto del inserto y controla el desplazamiento y la angulacion cuando el hueso y los ligamentos ya estan comprometidos.',
    obj: femoral, pos: V(0, 0.10, 0.28), focos: [caja], camLocal: V(0.24, 0.40, 0.88), margen: 2.4, modo: 'normal' });
  if (pivote) puntos.push({
    titulo: 'Pivote rotatorio',
    texto: 'Ademas de flexionar, la protesis rota sobre este eje: reproduce la rotacion natural de la rodilla y descarga tension en la union con el hueso.',
    obj: tibial, pos: V(0, -0.42, 0.16), focos: [pivote], camLocal: V(0.42, 0.18, 0.89), margen: 2.6, modo: 'explotar' });
  if (segmentos.length) puntos.push({
    titulo: 'Segmentos modulares',
    texto: 'Los anillos marcan las uniones donde se agregan segmentos: permiten reconstruir la longitud perdida en revisiones y en cirugia oncologica.',
    obj: femoral, pos: V(0, 1.14, 0.18), focos: segmentos, camLocal: V(0.52, 0.24, 0.82), margen: 2.2, modo: 'explotar' });
  if (bisagra) puntos.push({
    titulo: rotatoria ? 'Eje de bisagra rotatoria' : 'Eje de bisagra simple',
    texto: rotatoria
      ? 'Vincula el componente femoral con el tibial y permite flexion mas rotacion: la constriccion necesaria sin bloquear el giro.'
      : 'Bisagra simple: solo permite la flexion, sin rotacion. Es la opcion de maxima constriccion cuando los ligamentos no sostienen la rodilla.',""")

# --- 4) CEMENTOS: los sobres se distinguen por color e identificacion
s = s.replace("    const franja = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.34, 0.104), cfg.antibiotico ? m.verde : m.cuello);",
"""    const colorFranja = cfg.color === 'azul' ? new THREE.MeshStandardMaterial({ color: 0x2E6FB7, roughness: 0.45 })
                      : cfg.color === 'naranja' ? new THREE.MeshStandardMaterial({ color: 0xD4762A, roughness: 0.45 })
                      : (cfg.antibiotico ? m.verde : m.cuello);
    const franja = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.34, 0.104), colorFranja);""")
s = s.replace("""    if (cfg.dobleAntibiotico) {}""", "")
s = s.replace("""    g1.add(sobre, selloTop, selloBot, franja);""",
"""    g1.add(sobre, selloTop, selloBot, franja);
    if (cfg.franja2) {                                  // segunda franja: dos antibioticos
      const f2 = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.16, 0.106), m.verde);
      f2.position.set(0, -0.05, 0.001); g1.add(f2);
    }
    if (cfg.viscosidad) {                               // marca de viscosidad
      const v = new THREE.Mesh(new THREE.BoxGeometry(cfg.viscosidad * 0.30, 0.09, 0.106), m.cuello);
      v.position.set(-0.45 + cfg.viscosidad * 0.15, -0.42, 0.001); g1.add(v);
    }""")
io.open(p, "w", encoding="utf-8").write(s)
print("modelos diferenciados")

# ================================================================ visor3d.js: ocultar contexto si no aplica
p = "js/visor3d.js"
s = io.open(p, encoding="utf-8").read()
s = s.replace("      if (!anat && k !== 'solo') { b.disabled = true; b.classList.add('off'); continue; }",
              "      if (!anat && k !== 'solo') { b.style.display = 'none'; continue; }")
s = s.replace("""  if (botones.contexto) {""",
"""  // si el producto no tiene contexto anatomico, el grupo entero desaparece
  if (botones.contexto && !anat && botones.contexto.solo) {
    const g = botones.contexto.solo.closest('.v-grupo');
    if (g) g.style.display = 'none';
  }
  if (botones.contexto) {""")
io.open(p, "w", encoding="utf-8").write(s)
print("contexto oculto donde no aplica")
