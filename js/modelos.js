// Geometría paramétrica de los productos de Swiss Protech.
// Cada constructor devuelve { raiz, piezas, tapas, puntos, explotar }.
// puntos: { titulo, texto, obj, pos, focos, camLocal, margen, modo }
//   modo: 'normal' | 'corte' | 'explotar'
import * as THREE from 'three';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const hemi = (r, seg = 128) => new THREE.SphereGeometry(r, seg, seg / 2, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2);

// ---------------------------------------------------------------- texturas
function texturaPorosa(size = 1024) {
  const c = document.createElement('canvas'); c.width = c.height = size;
  const g = c.getContext('2d');
  g.fillStyle = '#C3C7CA'; g.fillRect(0, 0, size, size);
  const b = document.createElement('canvas'); b.width = b.height = size;
  const gb = b.getContext('2d');
  gb.fillStyle = '#808080'; gb.fillRect(0, 0, size, size);
  for (let i = 0; i < 24000; i++) {
    const x = Math.random() * size, y = Math.random() * size, r = 0.8 + Math.random() * 2.6;
    const v = 150 + Math.floor(Math.random() * 80);
    g.fillStyle = `rgb(${v},${v + 3},${v + 5})`; g.beginPath(); g.arc(x, y, r, 0, 6.283); g.fill();
    const h = 60 + Math.floor(Math.random() * 150);
    gb.fillStyle = `rgb(${h},${h},${h})`; gb.beginPath(); gb.arc(x, y, r, 0, 6.283); gb.fill();
  }
  const map = new THREE.CanvasTexture(c), bump = new THREE.CanvasTexture(b);
  for (const t of [map, bump]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(3, 1.6); t.anisotropy = 8; }
  map.colorSpace = THREE.SRGBColorSpace;
  return { map, bump };
}

export function materiales() {
  const { map, bump } = texturaPorosa();
  return {
    poroso:    new THREE.MeshStandardMaterial({ color: 0xD3D7DA, map, bumpMap: bump, bumpScale: 0.02, roughness: 0.95, metalness: 0.45 }),
    pulido:    new THREE.MeshPhysicalMaterial({ color: 0xE4E7EA, metalness: 1, roughness: 0.14, envMapIntensity: 1.25 }),
    pulidoInt: new THREE.MeshPhysicalMaterial({ color: 0xDADDE0, metalness: 1, roughness: 0.10, envMapIntensity: 1.35, side: THREE.BackSide }),
    mate:      new THREE.MeshStandardMaterial({ color: 0xC9CED2, roughness: 0.55, metalness: 0.85 }),
    poli:      new THREE.MeshPhysicalMaterial({ color: 0xF2D9E4, roughness: 0.30, metalness: 0, clearcoat: 0.55, clearcoatRoughness: 0.22, envMapIntensity: 0.9 }),
    poliInt:   new THREE.MeshPhysicalMaterial({ color: 0xEBC9D7, roughness: 0.22, metalness: 0, clearcoat: 0.6, side: THREE.BackSide }),
    poliBlancoInt: new THREE.MeshPhysicalMaterial({ color: 0xF2F2EF, roughness: 0.32, metalness: 0, clearcoat: 0.45, side: THREE.BackSide }),
    poliBlanco:new THREE.MeshPhysicalMaterial({ color: 0xFAFAF8, roughness: 0.34, metalness: 0, clearcoat: 0.5, envMapIntensity: 0.85 }),
    cabeza:    new THREE.MeshPhysicalMaterial({ color: 0xDCDFE3, metalness: 1, roughness: 0.05, envMapIntensity: 1.4 }),
    cuello:    new THREE.MeshStandardMaterial({ color: 0xB4B9BD, roughness: 0.5, metalness: 0.75 }),
    agujero:   new THREE.MeshStandardMaterial({ color: 0x33383C, roughness: 0.55, metalness: 0.8 }),
    cemento:   new THREE.MeshStandardMaterial({ color: 0xF7F5F0, roughness: 0.85, metalness: 0 }),
    sobre:     new THREE.MeshStandardMaterial({ color: 0xEDEFEF, roughness: 0.42, metalness: 0.35 }),
    verde:     new THREE.MeshStandardMaterial({ color: 0x3FA46A, roughness: 0.45, metalness: 0.05 }),
    plastico:  new THREE.MeshPhysicalMaterial({ color: 0xE6EAEC, roughness: 0.25, metalness: 0, transmission: 0.55, thickness: 0.4, envMapIntensity: 1 }),
    oscuro:    new THREE.MeshStandardMaterial({ color: 0x3A4046, roughness: 0.45, metalness: 0.6 }),
    porosoOsc: new THREE.MeshStandardMaterial({ color: 0x585D62, map, bumpMap: bump, bumpScale: 0.035, roughness: 1.0, metalness: 0.55 }),
  };
}

const tapaPlano = (geo, mat, y = 0) => {
  const t = new THREE.Mesh(geo, mat.clone());
  t.rotation.y = Math.PI / 2; t.material.side = THREE.DoubleSide; t.visible = false; t.position.y = y;
  return t;
};

// ================================================================ COTILO
// cfg: {
//   tipo: 'poroso' (MobileLink) | 'corona' (Crown Cup) | 'polietileno' (Lubinus Cup)
//   dobleMovilidad, agujeros, achatado
// }
export function cotilo(m, cfg = {}) {
  const tipo = cfg.tipo || 'poroso';
  const corona = tipo === 'corona';
  const pe = tipo === 'polietileno';
  const dob = !!cfg.dobleMovilidad;
  const nAgujeros = cfg.agujeros === undefined ? (corona ? 4 : 3) : cfg.agujeros;
  const rAgujero = corona ? 0.20 : 0.082;
  const achata = cfg.achatado || (pe ? 0.80 : 1);

  const matExt = pe ? m.poliBlanco : (corona ? m.porosoOsc : m.poroso);
  const matAro = pe ? m.pulido : (corona ? m.mate : m.pulido);
  const matInt = pe ? m.poliBlancoInt : m.pulidoInt;

  const raiz = new THREE.Group();
  const casquete = new THREE.Group(), inserto = new THREE.Group(), cabeza = new THREE.Group();
  raiz.add(casquete, cabeza); if (dob) raiz.add(inserto);

  const ext = new THREE.Mesh(hemi(1.0), matExt); ext.castShadow = true;
  const int = new THREE.Mesh(hemi(0.86), matInt);
  const aro = new THREE.Mesh(new THREE.RingGeometry(0.86, 1.0, 160), matAro); aro.rotation.x = -Math.PI / 2;
  const banda = new THREE.Mesh(new THREE.CylinderGeometry(1.004, 1.004, pe ? 0.10 : 0.075, 160, 1, true), matAro);
  banda.position.y = -(pe ? 0.05 : 0.037);
  casquete.add(ext, int, aro, banda);
  if (achata !== 1) casquete.scale.y = achata;

  // dientes del borde (Crown Cup) o muescas verticales (Lubinus Cup)
  const relieve = [];
  if (corona || pe) {
    const n = corona ? 16 : 14;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const d = corona
        ? new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.30, 0.12), m.mate)
        : new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.34, 0.13), m.poliBlanco);
      d.position.set(Math.cos(a) * 0.98, corona ? 0.06 : -0.10, Math.sin(a) * 0.98);
      d.lookAt(0, d.position.y, 0);
      d.castShadow = true;
      casquete.add(d); relieve.push(d);
    }
  }

  // orificios para tornillos
  const agujeros = [], bordes = [], normales = [];
  const azBase = corona ? [0, 1.57, 3.14, 4.71] : [0, 1.15, -1.15, 2.4];
  const az = azBase.slice(0, nAgujeros);
  const pol = corona ? 0.42 : 0.62;
  for (const a of az) {
    const n = V(Math.sin(pol) * Math.cos(a), -Math.cos(pol), Math.sin(pol) * Math.sin(a));
    normales.push(n.clone());
    // el orificio se lee desde adentro: disco oscuro sobre la cara interna + anillo en la externa
    const cil = new THREE.Mesh(new THREE.CylinderGeometry(rAgujero, rAgujero * 0.86, 0.16, 40), m.agujero);
    cil.position.copy(n).multiplyScalar(0.90);
    cil.quaternion.setFromUnitVectors(V(0, 1, 0), n);
    const disco = new THREE.Mesh(new THREE.CircleGeometry(rAgujero, 44), m.agujero);
    disco.position.copy(n).multiplyScalar(0.853);
    disco.quaternion.setFromUnitVectors(V(0, 0, 1), n.clone().negate());
    const bo = new THREE.Mesh(new THREE.TorusGeometry(rAgujero * 1.04, rAgujero * 0.14, 12, 48), matAro);
    bo.position.copy(n).multiplyScalar(0.858);
    bo.quaternion.setFromUnitVectors(V(0, 0, 1), n);
    casquete.add(cil, disco, bo); agujeros.push(cil, disco); bordes.push(bo);
  }

  let insExt, insInt, insAro;
  if (dob) {
    insExt = new THREE.Mesh(hemi(0.845), m.poli); insExt.castShadow = true;
    insInt = new THREE.Mesh(hemi(0.63), m.poliInt);
    insAro = new THREE.Mesh(new THREE.RingGeometry(0.63, 0.845, 160), m.poli); insAro.rotation.x = -Math.PI / 2;
    inserto.add(insExt, insInt, insAro);
  }

  const rCab = dob ? 0.59 : 0.74;
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(rCab, 96, 64), m.cabeza); esfera.castShadow = true;
  const cuello = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.21, 0.62, 48), m.cuello);
  cuello.position.y = rCab - 0.02; cuello.castShadow = true;
  cabeza.add(esfera, cuello);

  const tapas = [
    tapaPlano(new THREE.RingGeometry(0.86, 1.0, 96, 1, Math.PI, Math.PI), matAro),
    tapaPlano(new THREE.CircleGeometry(rCab, 96), m.cabeza),
  ];
  casquete.add(tapas[0]); cabeza.add(tapas[1]);
  if (dob) { const t = tapaPlano(new THREE.RingGeometry(0.63, 0.845, 96, 1, Math.PI, Math.PI), m.poli); inserto.add(t); tapas.push(t); }

  inserto.position.y = 0.02; cabeza.position.y = 0.04;
  // en reposo se muestra solo el casquete, como en la foto de catalogo
  cabeza.visible = false; inserto.visible = false;
  raiz.rotation.x = 0.92; raiz.rotation.y = 0.45; raiz.rotation.z = 0.10;

  let enMovimiento = false;
  const explotar = k => {
    const on = k > 0.001 || enMovimiento;
    cabeza.visible = on; inserto.visible = on && dob;
    inserto.position.y = 0.02 + 1.03 * k;
    cabeza.position.y = 0.04 + 2.06 * k;
  };

  // en movimiento la cabeza queda alojada y barre el arco de flexion
  const animar = (t) => {
    enMovimiento = t !== null;
    if (t === null) { cabeza.visible = false; inserto.visible = false; cabeza.rotation.set(0, 0, 0); if (dob) inserto.rotation.set(0, 0, 0); return; }
    cabeza.visible = true; inserto.visible = dob;
    cabeza.position.y = 0.04; inserto.position.y = 0.02;
    const a = Math.sin(t * Math.PI * 2);
    cabeza.rotation.z = a * 0.62;                 // flexion-extension del femur
    cabeza.rotation.x = Math.sin(t * Math.PI * 4) * 0.16;
    if (dob) inserto.rotation.z = a * 0.22;       // el revestimiento acompana: doble movilidad
  };

  const TXT_EXT = {
    poroso: ['Casquete de titanio poroso', 'Superficie porosa para la fijacion biologica sin cemento. El hueso crece dentro de la estructura y asegura el implante a largo plazo.'],
    corona: ['Casquete con superficie rugosa', 'La textura rugosa de titanio maximiza la superficie de contacto con el hueso y promueve la fijacion biologica sin cemento.'],
    polietileno: ['Cotilo de polietileno UHMWPE', 'Cotilo cementado de polietileno de peso molecular ultra alto. La estabilidad se logra en el manto de cemento, sin necesidad de crecimiento oseo.'],
  }[tipo];
  const TXT_ARO = {
    poroso: ['Aro pulido con press-fit integrado', 'El diseno incorpora un press-fit de 1,6 mm para la estabilidad primaria inmediata al impactar el cotilo en el acetabulo.'],
    corona: ['Dientes perifericos de anclaje', 'Los dientes del borde muerden el hueso esponjoso al impactar el cotilo: dan estabilidad rotacional inmediata y evitan el micromovimiento.'],
    polietileno: ['Muescas antirrotacion y anillo radiopaco', 'Las muescas verticales se anclan en el cemento e impiden que el cotilo rote. El anillo metalico permite controlar la posicion en la radiografia.'],
  }[tipo];

  const puntos = [
    { titulo: TXT_EXT[0], texto: TXT_EXT[1], obj: casquete, pos: V(0.30, -0.86, 0.40), focos: [ext],
      camLocal: V(0.42, -0.50, 0.76), margen: 1.75, modo: 'normal' },
    { titulo: TXT_ARO[0], texto: TXT_ARO[1], obj: casquete, pos: V(0.98, -0.03, 0.22),
      focos: relieve.length ? [aro, banda].concat(relieve) : [aro, banda], camLocal: V(0.60, 0.20, 0.77), margen: 1.55, modo: 'normal' },
    { titulo: pe ? 'Superficie articular concava' : 'Superficie interna pulida',
      texto: pe
        ? 'La cara concava de polietileno recibe directamente la cabeza femoral. Su acabado define el desgaste a lo largo de los anos.'
        : 'Minimiza el desgaste del componente que articula dentro del cotilo y prolonga la vida util del implante. Se muestra el corte para ver el interior.',
      obj: casquete, pos: V(-0.34, -0.50, 0.62), focos: [int], camLocal: V(0.10, 0.62, 0.78), margen: 1.25, modo: 'corte' },
  ];
  if (dob) puntos.push({
    titulo: 'Inserto de doble movilidad',
    texto: 'Convierte el cotilo en un sistema modular de movilidad dual y aloja los revestimientos de polietileno del sistema BiMobile.',
    obj: inserto, pos: V(0.70, -0.16, 0.42), focos: [insExt, insAro, insInt], camLocal: V(0.48, 0.44, 0.76), margen: 2.10, modo: 'explotar' });
  puntos.push({
    titulo: dob ? 'Cabeza femoral de doble articulacion' : 'Cabeza femoral',
    texto: dob
      ? 'La cabeza articula dentro del revestimiento y el revestimiento dentro del cotilo: mayor rango de movilidad y menor riesgo de luxacion.'
      : 'La cabeza femoral articula directamente contra la superficie interna del cotilo.',
    obj: cabeza, pos: V(0.44, 0.16, 0.38), focos: [esfera, cuello], camLocal: V(0.42, 0.40, 0.81), margen: 1.85, modo: 'explotar' });
  if (nAgujeros) puntos.push({
    titulo: corona ? 'Orificios de fijacion con tornillos' : 'Orificios para tornillos',
    texto: corona
      ? 'Cuatro orificios amplios permiten atornillar el cotilo al hueso iliaco cuando la calidad osea o el defecto lo exigen.'
      : 'Permiten fijacion adicional con tornillos cuando la calidad osea lo requiere. Se cierran con tapones cuando no se utilizan.',
    obj: casquete, pos: normales[0].clone().multiplyScalar(1.02), focos: agujeros.concat(bordes),
    camLocal: normales[0].clone().add(V(0, 0.55, 0.25)).normalize(), margen: 2.30, modo: 'normal' });

  return { raiz, tapas, puntos, explotar, animar, anatomia: 'pelvis',
           movimiento: dob ? 'La cabeza articula dentro del revestimiento y el revestimiento dentro del cotilo: por eso el rango de movilidad es mayor.'
                           : 'La cabeza femoral barre el arco de flexion apoyada en la superficie interna del cotilo.' };
}

// ================================================================ VÁSTAGO FEMORAL
// cfg: { modular, cementado, revestido, largo }
export function vastago(m, cfg = {}) {
  const modular = !!cfg.modular, cementado = !!cfg.cementado, revestido = cfg.revestido !== false;
  const largo = cfg.largo || 2.9;

  const raiz = new THREE.Group();
  const pivot = new THREE.Group();          // gira alrededor del centro de la cabeza
  const cuerpo = new THREE.Group(), cabezaG = new THREE.Group();
  raiz.add(pivot, cabezaG); pivot.add(cuerpo);

  // perfil del vástago. afina = velocidad de adelgazamiento · aplana = sección ovalada
  const afina = cfg.afina || 0.62, aplana = cfg.aplana || 0.62, curva = cfg.curva || 0;
  const perfil = [];
  const pasos = 30;
  for (let i = 0; i <= pasos; i++) {
    const t = i / pasos;
    const y = 0.55 - t * largo;
    const r = 0.30 * Math.pow(1 - t, afina) + (cfg.puntaFina ? 0.032 : 0.055);
    perfil.push(new THREE.Vector2(r, y));
  }
  const geoCuerpo = new THREE.LatheGeometry(perfil, 72);
  geoCuerpo.scale(1, 1, aplana);                     // sección ovalada, como el hueso
  if (curva) {                                       // curvatura anatómica del canal femoral
    const pos = geoCuerpo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i), k = Math.max(0, (0.55 - y) / largo);
      pos.setX(i, pos.getX(i) + curva * k * k * largo * 0.5);
    }
    pos.needsUpdate = true; geoCuerpo.computeVertexNormals();
  }
  const matCuerpo = cementado ? m.pulido : (revestido ? m.poroso : m.mate);
  const eje = new THREE.Mesh(geoCuerpo, matCuerpo); eje.castShadow = true;
  cuerpo.add(eje);

  // hombro y cuello con el cono 12/14
  const hombro = new THREE.Mesh(new THREE.SphereGeometry(0.30, 48, 32, 0, Math.PI * 2, 0, Math.PI / 2), matCuerpo);
  hombro.position.y = 0.55; hombro.scale.set(1, 0.75, 0.62); hombro.castShadow = true;
  const cono = new THREE.Mesh(new THREE.CylinderGeometry(0.115, 0.155, 0.52, 40), m.cuello);
  cono.position.set(-0.30, 0.90, 0); cono.rotation.z = 0.72; cono.castShadow = true;
  cuerpo.add(hombro, cono);

  // collar de apoyo sobre el corte del cuello (vástagos anatómicos cementados)
  let collar = null;
  if (cfg.collar) {
    collar = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.30, 0.075, 56), m.pulido);
    collar.scale.set(1, 1, aplana); collar.position.set(-0.05, 0.58, 0); collar.rotation.z = 0.16;
    collar.castShadow = true; cuerpo.add(collar);
  }
  // estrías longitudinales: estabilidad rotacional dentro del canal
  const estrias = [];
  if (cfg.estrias) {
    for (let i = 0; i < cfg.estrias; i++) {
      const a = (i / cfg.estrias) * Math.PI * 2;
      const e = new THREE.Mesh(new THREE.BoxGeometry(0.024, largo * 0.60, 0.05), m.mate);
      e.position.set(Math.cos(a) * 0.205, -0.34, Math.sin(a) * 0.205 * aplana);
      e.lookAt(0, -0.34, 0); cuerpo.add(e); estrias.push(e);
    }
  }

  // franja porosa proximal (fijación biológica)
  let franja = null;
  if (revestido && !cementado) {
    const gf = new THREE.CylinderGeometry(0.305, 0.225, 0.85, 64, 1, true);
    gf.scale(1, 1, 0.62);
    franja = new THREE.Mesh(gf, m.poroso); franja.position.y = 0.14;
    cuerpo.add(franja);
    eje.material = m.mate;
  }

  // unión modular (cuerpo + vástago distal)
  let anillo = null, distal = null;
  const grupoDistal = new THREE.Group(); pivot.add(grupoDistal);
  if (modular) {
    anillo = new THREE.Mesh(new THREE.TorusGeometry(0.175, 0.030, 14, 60), m.cuello);
    anillo.rotation.x = Math.PI / 2; anillo.position.y = -0.95; anillo.scale.set(1, 0.62, 1);
    cuerpo.add(anillo);
    const gd = new THREE.CylinderGeometry(0.115, 0.075, largo * 0.55, 48);
    distal = new THREE.Mesh(gd, m.mate);
    distal.position.y = 0.55 - largo - largo * 0.22; distal.castShadow = true;
    // estrías del vástago distal
    for (let i = 0; i < 10; i++) {
      const e = new THREE.Mesh(new THREE.BoxGeometry(0.012, largo * 0.5, 0.03), m.cuello);
      const a = (i / 10) * Math.PI * 2;
      e.position.set(Math.cos(a) * 0.098, distal.position.y, Math.sin(a) * 0.098);
      e.lookAt(0, distal.position.y, 0);
      grupoDistal.add(e);
    }
    grupoDistal.add(distal);
  }

  const rCab = 0.34;
  const esfera = new THREE.Mesh(new THREE.SphereGeometry(rCab, 80, 56), m.cabeza);
  esfera.position.set(-0.52, 1.16, 0); esfera.castShadow = true;
  cabezaG.add(esfera);

  const tapas = [];
  raiz.rotation.y = 0.42; raiz.rotation.z = 0.16;
  raiz.position.y = 0.35;

  const CENTRO_CAB = V(-0.52, 1.16, 0);      // centro de rotacion de la articulacion
  pivot.position.copy(CENTRO_CAB);
  cuerpo.position.copy(CENTRO_CAB).multiplyScalar(-1);
  grupoDistal.position.copy(CENTRO_CAB).multiplyScalar(-1);
  const BASE_DIST = grupoDistal.position.y;

  const explotar = k => {
    cabezaG.position.set(-0.42 * k, 1.0 * k, 0);
    if (modular) grupoDistal.position.y = BASE_DIST - 1.15 * k;
  };
  // en movimiento el femur flexiona alrededor de la cabeza, que queda fija en el cotilo
  const animar = (t) => {
    if (t === null) { pivot.rotation.set(0, 0, 0); return; }
    const a = Math.sin(t * Math.PI * 2);
    pivot.rotation.z = a * 0.52;
    pivot.rotation.x = Math.sin(t * Math.PI * 4) * 0.14;
  };

  const puntos = [
    { titulo: 'Cono 12/14 para la cabeza',
      texto: 'El cono estandarizado permite elegir la cabeza y el offset en el momento de la cirugía, sin cambiar el vástago.',
      obj: cuerpo, pos: V(-0.42, 1.02, 0.18), focos: [cono], camLocal: V(-0.35, 0.55, 0.76), margen: 2.6, modo: 'normal' },
    { titulo: cementado ? 'Cuerpo pulido para cementar' : (revestido ? 'Franja proximal porosa' : 'Cuerpo del vástago'),
      texto: cementado
        ? 'La superficie pulida permite el micromovimiento controlado dentro del manto de cemento y distribuye la carga a lo largo del vástago.'
        : (revestido
          ? 'El recubrimiento poroso en la zona proximal busca la fijación biológica donde el hueso tiene mejor calidad.'
          : 'Cuerpo de sección ovalada que acompaña la anatomía del canal femoral y da estabilidad rotacional.'),
      obj: cuerpo, pos: V(0.30, 0.12, 0.20), focos: revestido && !cementado ? [franja] : [eje],
      camLocal: V(0.62, 0.24, 0.75), margen: 1.9, modo: 'normal' },
    { titulo: cfg.collar ? 'Collar de apoyo' : (cfg.estrias ? 'Estrías antirrotacionales' : 'Hombro y apoyo metafisario'),
      texto: cfg.collar
        ? 'El collar apoya directamente sobre el corte del cuello femoral: frena el hundimiento del vástago y reparte la carga al hueso proximal.'
        : (cfg.estrias
          ? 'Las estrías longitudinales muerden el hueso o el cemento e impiden que el vástago rote dentro del canal femoral.'
          : 'El hombro apoya sobre el corte del cuello femoral y transmite la carga al hueso proximal.'),
      obj: cuerpo, pos: V(0.22, 0.55, 0.16),
      focos: cfg.collar ? [collar, hombro] : (estrias.length ? estrias : [hombro]),
      camLocal: V(0.48, 0.42, 0.77), margen: cfg.estrias ? 1.8 : 2.4, modo: 'normal' },
    { titulo: 'Sección del vástago',
      texto: 'El corte muestra la sección ovalada del cuerpo: más ancha en sentido anteroposterior, para acompañar el canal femoral y resistir la rotación.',
      obj: cuerpo, pos: V(0.24, 0.02, 0.14), focos: [eje], camLocal: V(0.74, 0.24, 0.63), margen: 1.7, modo: 'corte' },
    { titulo: 'Cabeza femoral',
      texto: 'Articula contra el cotilo o su revestimiento. Se elige el diámetro y el offset según el caso.',
      obj: cabezaG, pos: V(-0.52, 1.16, 0.30), focos: [esfera], camLocal: V(-0.20, 0.46, 0.87), margen: 2.5, modo: 'explotar' },
  ];
  if (modular) puntos.push({
    titulo: 'Unión modular y vástago distal',
    texto: 'El cuerpo proximal y el vástago distal se ensamblan en cirugía: permite ajustar largo, versión y offset sobre el defecto óseo real.',
    obj: raiz, pos: V(0.0, -1.15, 0.22), focos: [anillo, distal], camLocal: V(0.42, 0.10, 0.90), margen: 1.9, modo: 'explotar' });

  return { raiz, tapas, puntos, explotar, animar, anatomia: 'femurProximal',
           movimiento: 'La cabeza queda fija dentro del cotilo y el femur gira a su alrededor: eso es la flexion y la extension de la cadera.' };
}

// ================================================================ RODILLA
// cfg: { bisagra, unicompartimental, vastagos }
export function rodilla(m, cfg = {}) {
  const bisagra = !!cfg.bisagra, uni = !!cfg.unicompartimental;
  const vastagos = cfg.vastagos !== false && !uni;
  const rotatoria = cfg.rotatoria !== false;      // bisagra que además rota
  const modular = !!cfg.modular;                  // segmentos intercambiables
  const altaFlexion = !!cfg.altaFlexion;          // cóndilo posterior más largo
  const cajaRev = !!cfg.cajaRevision;             // caja intercondílea de revisión
  const largoVast = cfg.largoVastago || 1.35;

  const raiz = new THREE.Group();
  const femoral = new THREE.Group(), inserto = new THREE.Group(), tibial = new THREE.Group();
  raiz.add(femoral, inserto, tibial);

  // ---- cóndilo: arco grueso (toro parcial) con sección ensanchada
  const ANCHO = uni ? 0.46 : 0.42;
  const condilo = (x) => {
    const g = new THREE.TorusGeometry(0.52, 0.185, 20, 80, altaFlexion ? 4.60 : 4.05);
    g.rotateZ(altaFlexion ? -3.20 : -2.86);                 // de posterior, por abajo, hasta anterior-superior
    g.scale(1, 1, ANCHO / 0.37);      // ensancha la sección medial-lateral
    g.rotateY(Math.PI / 2);           // el arco queda de perfil, el ancho sobre X
    const mesh = new THREE.Mesh(g, m.pulido);
    mesh.position.x = x; mesh.castShadow = true;
    return mesh;
  };
  const sep = uni ? 0 : 0.28;
  const condIzq = condilo(-sep); femoral.add(condIzq);
  let condDer = null;
  if (!uni) { condDer = condilo(sep); femoral.add(condDer); }

  // ---- puente anterior y tróclea (une los cóndilos por delante y arriba)
  let puente = null, troclea = null;
  if (!uni) {
    const gp = new THREE.BoxGeometry(sep * 2, 0.30, 0.34);
    puente = new THREE.Mesh(gp, m.pulido);
    puente.position.set(0, 0.36, 0.30); puente.castShadow = true;
    const gt = new THREE.CylinderGeometry(0.30, 0.30, sep * 2 + 0.30, 44, 1, false, 0, Math.PI);
    troclea = new THREE.Mesh(gt, m.pulido);
    troclea.rotation.z = Math.PI / 2; troclea.rotation.y = Math.PI;
    troclea.position.set(0, 0.30, 0.26); troclea.castShadow = true;
    femoral.add(puente, troclea);
  }

  // ---- inserto de polietileno: platillo con cuencas
  const rIns = uni ? 0.40 : 0.76;
  const platillo = new THREE.Mesh(new THREE.CylinderGeometry(rIns, rIns * 0.94, 0.19, 64), m.poliBlanco);
  platillo.scale.set(1, 1, 0.78); platillo.castShadow = true;
  inserto.add(platillo);
  const cuencas = [];
  for (const x of (uni ? [0] : [-sep, sep])) {
    const c = new THREE.Mesh(new THREE.SphereGeometry(0.27, 40, 24, 0, Math.PI * 2, 0, Math.PI / 2), m.poliBlanco);
    c.position.set(x, 0.095, 0); c.scale.set(1, 0.42, 0.86); c.rotation.x = Math.PI;
    inserto.add(c); cuencas.push(c);
  }
  let poste = null;
  if (!uni && !bisagra) {
    poste = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.34, 0.24), m.poliBlanco);
    poste.position.set(0, 0.22, 0); poste.castShadow = true;
    inserto.add(poste);
  }

  // ---- bandeja tibial y quilla
  const rBan = uni ? 0.42 : 0.78;
  const bandeja = new THREE.Mesh(new THREE.CylinderGeometry(rBan, rBan * 0.95, 0.13, 64), m.mate);
  bandeja.position.y = -0.16; bandeja.scale.set(1, 1, 0.78); bandeja.castShadow = true;
  const quilla = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.095, vastagos ? 1.5 : 0.48, 40), m.mate);
  quilla.position.y = -0.16 - (vastagos ? 0.82 : 0.30); quilla.castShadow = true;
  tibial.add(bandeja, quilla);

  // ---- caja intercondílea de revisión
  let caja = null;
  if (cajaRev) {
    caja = new THREE.Mesh(new THREE.BoxGeometry(sep * 1.5, 0.54, 0.50), m.pulido);
    caja.position.set(0, 0.12, -0.06); caja.castShadow = true;
    femoral.add(caja);
  }
  // ---- pivote rotatorio
  let pivote = null;
  if (bisagra && rotatoria) {
    pivote = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.10, 0.62, 32), m.cuello);
    pivote.position.set(0, -0.42, 0); pivote.castShadow = true;
    tibial.add(pivote);
  }
  // ---- segmentos modulares
  const segmentos = [];
  if (modular) {
    for (let i = 0; i < 2; i++) {
      const an = new THREE.Mesh(new THREE.TorusGeometry(0.155, 0.03, 12, 44), m.cuello);
      an.rotation.x = Math.PI / 2; an.position.y = 0.90 + i * 0.46;
      femoral.add(an); segmentos.push(an);
    }
  }
  // ---- bisagra
  let ejeBisagra = null;
  if (bisagra) {
    ejeBisagra = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, sep * 2 + 0.36, 32), m.cuello);
    ejeBisagra.rotation.z = Math.PI / 2; ejeBisagra.position.set(0, -0.04, -0.04); ejeBisagra.castShadow = true;
    femoral.add(ejeBisagra);
  }
  // ---- vástago femoral
  let vastFem = null;
  if (vastagos) {
    vastFem = new THREE.Mesh(new THREE.CylinderGeometry(0.135, 0.095, largoVast, 40), m.mate);
    vastFem.position.y = 0.58 + largoVast / 2; vastFem.castShadow = true;
    femoral.add(vastFem);
  }

  femoral.position.y = 0.46;
  inserto.position.y = -0.02;
  tibial.position.y = -0.02;
  raiz.rotation.y = 0.58; raiz.rotation.x = 0.04;

  const explotar = k => {
    femoral.position.y = 0.46 + 1.45 * k;
    inserto.position.y = -0.02 + 0.62 * k;
  };
  // en movimiento el femur flexiona sobre el inserto: el origen del grupo femoral
  // coincide con el centro del arco de los condilos, que es el eje real de giro
  const animar = (t) => {
    if (t === null) { femoral.rotation.set(0, 0, 0); return; }
    const f = (1 - Math.cos(t * Math.PI * 2)) / 2;       // 0 -> 1 -> 0, suave
    femoral.rotation.x = -f * (uni ? 1.75 : (altaFlexion ? 2.55 : 2.20));
  };

  const tapas = [];
  const puntos = [
    { titulo: uni ? 'Componente femoral unicompartimental' : 'Cóndilos femorales',
      texto: uni
        ? 'Reemplaza únicamente el cóndilo afectado y conserva el resto de la articulación, los ligamentos y el hueso sano.'
        : 'Los cóndilos pulidos reproducen la curvatura del fémur para que la flexión sea progresiva y estable en todo el recorrido.',
      obj: femoral, pos: V(-sep, -0.34, 0.30), focos: uni ? [condIzq] : [condIzq, condDer],
      camLocal: V(0.30, 0.16, 0.94), margen: 1.85, modo: 'normal' },
    { titulo: 'Inserto de polietileno',
      texto: 'Es la superficie de deslizamiento entre el fémur y la tibia. Su congruencia con el cóndilo define el desgaste y la estabilidad.',
      obj: inserto, pos: V(0, 0.12, 0.46), focos: [platillo, ...cuencas],
      camLocal: V(0.32, 0.42, 0.85), margen: 2.0, modo: 'explotar' },
    { titulo: 'Seccion del inserto',
      texto: 'El corte deja ver el espesor del polietileno y la profundidad de las cuencas: es lo que define la congruencia con el condilo y el desgaste.',
      obj: inserto, pos: V(0, 0.06, 0.20), focos: [platillo].concat(cuencas), camLocal: V(0.78, 0.30, 0.55), margen: 1.7, modo: 'corte' },
    { titulo: 'Bandeja tibial y quilla',
      texto: 'Se fija sobre el corte de la tibia. La quilla central da estabilidad rotacional y transmite la carga al hueso.',
      obj: tibial, pos: V(0, -0.16, 0.50), focos: [bandeja, quilla],
      camLocal: V(0.34, 0.02, 0.94), margen: 1.75, modo: 'normal' },
  ];
  if (!uni && troclea) puntos.push({
    titulo: 'Tróclea y escotadura',
    texto: 'El canal troclear guía el deslizamiento de la rótula; el puente central estabiliza el movimiento anteroposterior.',
    obj: femoral, pos: V(0, 0.32, 0.52), focos: [troclea, puente],
    camLocal: V(0.16, 0.42, 0.89), margen: 2.3, modo: 'normal' });
  if (poste) puntos.push({
    titulo: 'Poste estabilizador',
    texto: 'Sustituye la función del ligamento cruzado posterior: controla el desplazamiento hacia atrás del fémur en flexión.',
    obj: inserto, pos: V(0, 0.30, 0.18), focos: [poste],
    camLocal: V(0.20, 0.46, 0.86), margen: 3.0, modo: 'explotar' });
  if (cajaRev) puntos.push({
    titulo: 'Caja intercondílea de revisión',
    texto: 'La caja aloja el poste alto del inserto y controla el desplazamiento y la angulación cuando el hueso y los ligamentos ya están comprometidos.',
    obj: femoral, pos: V(0, 0.12, 0.26), focos: [caja], camLocal: V(0.24, 0.40, 0.88), margen: 2.4, modo: 'normal' });
  if (pivote) puntos.push({
    titulo: 'Pivote rotatorio',
    texto: 'Además de flexionar, la prótesis rota sobre este eje: reproduce la rotación natural de la rodilla y descarga tensión en la unión con el hueso.',
    obj: tibial, pos: V(0, -0.42, 0.16), focos: [pivote], camLocal: V(0.42, 0.18, 0.89), margen: 2.6, modo: 'explotar' });
  if (segmentos.length) puntos.push({
    titulo: 'Segmentos modulares',
    texto: 'Los anillos marcan las uniones donde se agregan segmentos: permiten reconstruir la longitud perdida en revisiones y en cirugía oncológica.',
    obj: femoral, pos: V(0, 1.14, 0.18), focos: segmentos, camLocal: V(0.52, 0.24, 0.82), margen: 2.2, modo: 'explotar' });
  if (altaFlexion) puntos.push({
    titulo: 'Cóndilo de alta flexión',
    texto: 'El cóndilo se prolonga hacia atrás para mantener el contacto en flexiones profundas, sin que el borde del inserto reciba toda la carga.',
    obj: femoral, pos: V(-sep, -0.40, -0.30), focos: uni ? [condIzq] : [condIzq, condDer],
    camLocal: V(0.30, 0.10, -0.94), margen: 1.9, modo: 'normal' });
  puntos.push({
    titulo: 'Sección del inserto',
    texto: 'El corte deja ver el espesor del polietileno y la profundidad de las cuencas: es lo que define la congruencia con el cóndilo y el desgaste.',
    obj: inserto, pos: V(0, 0.06, 0.20), focos: [platillo].concat(cuencas),
    camLocal: V(0.78, 0.30, 0.55), margen: 1.7, modo: 'corte' });
  if (bisagra) puntos.push({
    titulo: rotatoria ? 'Eje de bisagra rotatoria' : 'Eje de bisagra simple',
    texto: rotatoria
      ? 'Vincula el componente femoral con el tibial y permite flexión más rotación: la constricción necesaria sin bloquear el giro.'
      : 'Bisagra simple: solo permite la flexión, sin rotación. Es la opción de máxima constricción cuando los ligamentos no sostienen la rodilla.',
    obj: femoral, pos: V(0, -0.04, -0.22), focos: [ejeBisagra],
    camLocal: V(0.30, 0.22, -0.93), margen: 2.6, modo: 'explotar' });
  if (vastagos && vastFem) puntos.push({
    titulo: 'Vástagos de extensión',
    texto: 'Los vástagos femoral y tibial reparten la carga sobre una zona más amplia del hueso: son los que hacen posible la revisión.',
    obj: raiz, pos: V(0, 1.5, 0.20), focos: [vastFem, quilla],
    camLocal: V(0.44, 0.20, 0.87), margen: 1.6, modo: 'explotar' });

  return { raiz, tapas, puntos, explotar, animar, anatomia: 'femurTibia',
           movimiento: uni
             ? 'El condilo se desliza sobre el inserto conservando el resto de la articulacion y los ligamentos.'
             : (altaFlexion
               ? 'El condilo prolongado mantiene el contacto con el inserto incluso en flexiones profundas, por encima de los 130 grados.'
               : 'Los condilos ruedan y se deslizan sobre el inserto de polietileno: asi la protesis reproduce la flexion de la rodilla.') };
}

// ================================================================ CEMENTOS Y MEZCLA
// cfg: { tipo: 'sobre' | 'cartucho' | 'pistola', antibiotico }
export function cemento(m, cfg = {}) {
  const tipo = cfg.tipo || 'sobre';
  const raiz = new THREE.Group();
  const tapas = [];
  let puntos = [], explotar = () => {};

  if (tipo === 'sobre') {
    const g1 = new THREE.Group(), g2 = new THREE.Group();
    raiz.add(g1, g2);
    // sobre de polvo
    const sobre = new THREE.Mesh(new THREE.BoxGeometry(1.35, 1.65, 0.10), m.sobre);
    const selloTop = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.14, 0.055), m.mate); selloTop.position.y = 0.86;
    const selloBot = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.14, 0.055), m.mate); selloBot.position.y = -0.86;
    const colorFranja = cfg.color === 'azul' ? new THREE.MeshStandardMaterial({ color: 0x2E6FB7, roughness: 0.45 })
                      : cfg.color === 'naranja' ? new THREE.MeshStandardMaterial({ color: 0xD4762A, roughness: 0.45 })
                      : (cfg.antibiotico ? m.verde : m.cuello);
    const franja = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.34, 0.104), colorFranja);
    franja.position.set(0, 0.30, 0.001);
    sobre.castShadow = true;
    g1.add(sobre, selloTop, selloBot, franja);
    if (cfg.franja2) {                              // segunda franja: dos antibióticos
      const f2 = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.16, 0.106), m.verde);
      f2.position.set(0, -0.06, 0.001); g1.add(f2);
    }
    if (cfg.viscosidad) {                           // marca de viscosidad
      const v = new THREE.Mesh(new THREE.BoxGeometry(cfg.viscosidad * 0.28, 0.09, 0.106), m.cuello);
      v.position.set(-0.48 + cfg.viscosidad * 0.14, -0.44, 0.001); g1.add(v);
    }
    g1.position.x = -0.78; g1.rotation.y = 0.30;
    // ampolla de monómero
    const vidrio = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 1.30, 48), m.plastico);
    const cuelloA = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.20, 0.34, 32), m.plastico); cuelloA.position.y = 0.80;
    const liquido = new THREE.Mesh(new THREE.CylinderGeometry(0.225, 0.225, 1.05, 40), m.cemento); liquido.position.y = -0.10;
    vidrio.castShadow = true;
    g2.add(vidrio, cuelloA, liquido);
    g2.position.x = 0.86; g2.rotation.y = -0.22;

    raiz.rotation.y = 0.12;
    explotar = k => { g1.position.x = -0.78 - 0.55 * k; g2.position.x = 0.86 + 0.55 * k; };
    puntos = [
      { titulo: 'Polvo de polimetilmetacrilato',
        texto: 'El componente sólido del cemento óseo. La calidad y constancia de la materia prima determinan el comportamiento en el quirófano.',
        obj: g1, pos: V(0, 0.10, 0.10), focos: [sobre], camLocal: V(-0.35, 0.28, 0.89), margen: 1.9, modo: 'normal' },
      { titulo: cfg.antibiotico ? 'Antibiótico incorporado' : 'Identificación del envase',
        texto: cfg.antibiotico
          ? 'El antibiótico va mezclado en el polvo y se libera de forma local en el sitio del implante, para la profilaxis o el tratamiento de la infección.'
          : 'La franja identifica la fórmula y la viscosidad del cemento dentro de la familia PALACOS.',
        obj: g1, pos: V(0, 0.30, 0.10), focos: [franja], camLocal: V(-0.20, 0.32, 0.92), margen: 2.6, modo: 'normal' },
      { titulo: 'Contenido del envase',
        texto: 'El corte muestra el polvo dentro del sobre sellado: la dosis viene lista para mezclarse con el monómero, sin pesar ni fraccionar.',
        obj: g1, pos: V(0, 0, 0.06), focos: [sobre, franja], camLocal: V(0.62, 0.24, 0.75), margen: 1.6, modo: 'corte' },
      { titulo: 'Monómero líquido',
        texto: 'La ampolla contiene el líquido que, al mezclarse con el polvo, inicia la polimerización y define el tiempo de trabajo.',
        obj: g2, pos: V(0, 0.05, 0.30), focos: [vidrio, liquido, cuelloA], camLocal: V(0.40, 0.26, 0.88), margen: 2.0, modo: 'explotar' },
    ];
  }

  if (tipo === 'cartucho') {
    const cuerpoG = new THREE.Group(), tapaG = new THREE.Group();
    raiz.add(cuerpoG, tapaG);
    const tubo = new THREE.Mesh(new THREE.CylinderGeometry(0.46, 0.46, 1.9, 64, 1, true), m.plastico);
    const fondo = new THREE.Mesh(new THREE.CircleGeometry(0.46, 64), m.plastico); fondo.rotation.x = Math.PI / 2; fondo.position.y = -0.95;
    const masa = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 1.05, 48), m.cemento); masa.position.y = -0.35;
    tubo.castShadow = true;
    cuerpoG.add(tubo, fondo, masa);
    const tapa = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.52, 0.26, 64), m.verde); tapa.position.y = 1.02;
    const varilla = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 1.7, 24), m.verde); varilla.position.y = 1.9;
    const paleta = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.05, 0.16), m.verde); paleta.position.y = 2.72;
    const boquilla = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.17, 0.42, 32), m.verde); boquilla.position.y = 1.32;
    tapa.castShadow = true;
    tapaG.add(tapa, varilla, paleta, boquilla);
    const manguera = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.045, 12, 48, Math.PI * 1.1), m.plastico);
    manguera.position.set(0.62, 0.95, 0); manguera.rotation.set(0, 0, -0.5);
    raiz.add(manguera);

    raiz.rotation.y = 0.35; raiz.position.y = -0.35;
    explotar = k => { tapaG.position.y = 1.25 * k; };
    puntos = [
      { titulo: 'Cartucho de mezcla',
        texto: 'El polvo y el monómero se mezclan dentro del mismo cartucho con el que después se aplica: no hay trasvase ni contacto con el aire.',
        obj: cuerpoG, pos: V(0, -0.20, 0.46), focos: [tubo, masa, fondo], camLocal: V(0.42, 0.16, 0.89), margen: 1.8, modo: 'normal' },
      { titulo: 'Mezclador al vacío',
        texto: 'La varilla con paleta integrada mezcla mientras el vacío extrae el aire: menos porosidad y un cemento mecánicamente más resistente.',
        obj: tapaG, pos: V(0, 1.6, 0.20), focos: [varilla, paleta, tapa], camLocal: V(0.35, 0.30, 0.89), margen: 1.9, modo: 'explotar' },
      { titulo: 'Boquilla de aplicación',
        texto: 'Una vez mezclado, se coloca la boquilla y el mismo cartucho pasa a la pistola para aplicar el cemento.',
        obj: tapaG, pos: V(0, 1.32, 0.20), focos: [boquilla], camLocal: V(0.30, 0.35, 0.89), margen: 3.0, modo: 'explotar' },
      { titulo: 'Conexión de vacío',
        texto: 'La manguera conecta la bomba de vacío al cartucho durante toda la mezcla.',
        obj: raiz, pos: V(0.62, 0.95, 0.30), focos: [manguera], camLocal: V(0.55, 0.28, 0.79), margen: 2.8, modo: 'normal' },
    ];
  }

  if (tipo === 'pistola') {
    const cuerpoG = new THREE.Group(), cartuchoG = new THREE.Group();
    raiz.add(cuerpoG, cartuchoG);
    const marco = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.16, 0.20), m.oscuro); marco.position.y = -0.42; marco.castShadow = true;
    const cabezal = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.30, 0.20, 40), m.oscuro);
    cabezal.rotation.z = Math.PI / 2; cabezal.position.x = 1.22;
    const culata = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.62, 0.24), m.oscuro); culata.position.set(-1.16, -0.10, 0);
    const empuje = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 1.9, 24), m.cuello);
    empuje.rotation.z = Math.PI / 2; empuje.position.set(-0.55, -0.05, 0);
    const gatillo = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.60, 0.16), m.oscuro);
    gatillo.position.set(-0.72, -0.82, 0); gatillo.rotation.z = 0.30; gatillo.castShadow = true;
    const mango = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.80, 0.20), m.oscuro);
    mango.position.set(-1.12, -0.88, 0); mango.rotation.z = -0.12; mango.castShadow = true;
    cuerpoG.add(marco, cabezal, culata, empuje, gatillo, mango);

    const cart = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 1.55, 48), m.plastico);
    cart.rotation.z = Math.PI / 2; cart.position.set(0.42, -0.05, 0); cart.castShadow = true;
    const masa = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.30, 1.0, 40), m.cemento);
    masa.rotation.z = Math.PI / 2; masa.position.set(0.42, -0.05, 0);
    const boq = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.16, 0.46, 32), m.verde);
    boq.rotation.z = -Math.PI / 2; boq.position.set(1.42, -0.05, 0);
    cartuchoG.add(cart, masa, boq);

    raiz.rotation.y = 0.30; raiz.rotation.z = 0.06;
    explotar = k => { cartuchoG.position.y = 1.25 * k; };
    puntos = [
      { titulo: 'Cuerpo y gatillo',
        texto: 'El mecanismo multiplica la fuerza de la mano: el cemento sale con presión alta y de forma continua, sin esfuerzo del cirujano.',
        obj: cuerpoG, pos: V(-0.72, -0.72, 0.20), focos: [gatillo, mango, culata], camLocal: V(-0.28, 0.24, 0.93), margen: 2.0, modo: 'normal' },
      { titulo: 'Vástago de empuje',
        texto: 'Avanza dentro del cartucho y desplaza el cemento hacia la boquilla de manera controlada.',
        obj: cuerpoG, pos: V(-0.55, -0.05, 0.16), focos: [empuje, marco], camLocal: V(0.05, 0.34, 0.94), margen: 1.9, modo: 'normal' },
      { titulo: 'Cartucho PALAMIX',
        texto: 'Se carga el mismo cartucho en el que se mezcló el cemento: no hay trasvase entre la mezcla y la aplicación.',
        obj: cartuchoG, pos: V(0.42, 0.20, 0.34), focos: [cart, masa], camLocal: V(0.20, 0.42, 0.88), margen: 2.0, modo: 'explotar' },
      { titulo: 'Boquilla',
        texto: 'Dirige el cemento al canal femoral o al acetábulo, en retroceso y sin dejar aire atrapado.',
        obj: cartuchoG, pos: V(1.42, 0.05, 0.20), focos: [boq], camLocal: V(0.42, 0.30, 0.85), margen: 3.0, modo: 'explotar' },
    ];
  }

  return { raiz, tapas, puntos, explotar, anatomia: null };
}

export const CONSTRUCTORES = { cotilo, vastago, rodilla, cemento };
