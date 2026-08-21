// Visor 3D interactivo — cotilo de doble movilidad (representación técnica)
// Three.js r165. Rotación libre, zoom, vista explotada, corte y puntos de interés.
import * as THREE from 'three';
import { OrbitControls } from '../vendor/OrbitControls.js';
import { RoomEnvironment } from '../vendor/RoomEnvironment.js';

const TEAL = new THREE.Color(0x0095A1);
const TEAL_CLARO = new THREE.Color(0x5BC2C9);

// ------------------------------------------------------------ texturas
function texturaPorosa(size = 1024) {
  const c = document.createElement('canvas'); c.width = c.height = size;
  const g = c.getContext('2d');
  g.fillStyle = '#C3C7CA'; g.fillRect(0, 0, size, size);
  const b = document.createElement('canvas'); b.width = b.height = size;
  const gb = b.getContext('2d');
  gb.fillStyle = '#808080'; gb.fillRect(0, 0, size, size);
  for (let i = 0; i < 26000; i++) {
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

function materiales() {
  const { map, bump } = texturaPorosa();
  return {
    poroso: new THREE.MeshStandardMaterial({ color: 0xD3D7DA, map, bumpMap: bump, bumpScale: 0.02, roughness: 0.95, metalness: 0.45 }),
    pulido: new THREE.MeshPhysicalMaterial({ color: 0xE4E7EA, metalness: 1, roughness: 0.14, envMapIntensity: 1.25 }),
    pulidoInt: new THREE.MeshPhysicalMaterial({ color: 0xDADDE0, metalness: 1, roughness: 0.10, envMapIntensity: 1.35, side: THREE.BackSide }),
    poli: new THREE.MeshPhysicalMaterial({ color: 0xF2D9E4, roughness: 0.30, metalness: 0, clearcoat: 0.55, clearcoatRoughness: 0.22, envMapIntensity: 0.9 }),
    poliInt: new THREE.MeshPhysicalMaterial({ color: 0xEBC9D7, roughness: 0.22, metalness: 0, clearcoat: 0.6, side: THREE.BackSide }),
    cabeza: new THREE.MeshPhysicalMaterial({ color: 0xDCDFE3, metalness: 1, roughness: 0.05, envMapIntensity: 1.4 }),
    cuello: new THREE.MeshStandardMaterial({ color: 0xB4B9BD, roughness: 0.5, metalness: 0.75 }),
    agujero: new THREE.MeshStandardMaterial({ color: 0x33383C, roughness: 0.55, metalness: 0.8 }),
  };
}

const hemi = (r, seg = 128) => new THREE.SphereGeometry(r, seg, seg / 2, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2);

// ------------------------------------------------------------ modelo
function construirCotilo(m) {
  const raiz = new THREE.Group();
  const casquete = new THREE.Group(), inserto = new THREE.Group(), cabeza = new THREE.Group();
  raiz.add(casquete, inserto, cabeza);

  const ext = new THREE.Mesh(hemi(1.0), m.poroso); ext.castShadow = true;
  const int = new THREE.Mesh(hemi(0.88), m.pulidoInt);
  const aro = new THREE.Mesh(new THREE.RingGeometry(0.88, 1.0, 160), m.pulido); aro.rotation.x = -Math.PI / 2;
  const banda = new THREE.Mesh(new THREE.CylinderGeometry(1.002, 1.002, 0.075, 160, 1, true), m.pulido); banda.position.y = -0.037;
  casquete.add(ext, int, aro, banda);

  const agujeros = [], bordes = [];
  const posAgujero = [[0.62, 0.0], [0.62, 1.15], [0.62, -1.15]];
  const normalAgujero = [];
  for (const [pol, az] of posAgujero) {
    const n = new THREE.Vector3(Math.sin(pol) * Math.cos(az), -Math.cos(pol), Math.sin(pol) * Math.sin(az));
    normalAgujero.push(n.clone());
    const cil = new THREE.Mesh(new THREE.CylinderGeometry(0.082, 0.082, 0.16, 40), m.agujero);
    cil.position.copy(n).multiplyScalar(0.925);
    cil.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), n);
    const borde = new THREE.Mesh(new THREE.TorusGeometry(0.086, 0.011, 12, 48), m.pulido);
    borde.position.copy(n).multiplyScalar(1.0);
    borde.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), n);
    casquete.add(cil, borde); agujeros.push(cil); bordes.push(borde);
  }

  const insExt = new THREE.Mesh(hemi(0.862), m.poli); insExt.castShadow = true;
  const insInt = new THREE.Mesh(hemi(0.64), m.poliInt);
  const insAro = new THREE.Mesh(new THREE.RingGeometry(0.64, 0.862, 160), m.poli); insAro.rotation.x = -Math.PI / 2;
  inserto.add(insExt, insInt, insAro);

  const esfera = new THREE.Mesh(new THREE.SphereGeometry(0.60, 96, 64), m.cabeza); esfera.castShadow = true;
  const cuello = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.21, 0.62, 48), m.cuello);
  cuello.position.y = 0.58; cuello.castShadow = true;
  cabeza.add(esfera, cuello);

  const tapa = (geo, mat) => { const t = new THREE.Mesh(geo, mat.clone()); t.rotation.y = Math.PI / 2; t.material.side = THREE.DoubleSide; t.visible = false; return t; };
  const tCasq = tapa(new THREE.RingGeometry(0.88, 1.0, 96, 1, Math.PI, Math.PI), m.pulido);
  const tIns = tapa(new THREE.RingGeometry(0.64, 0.862, 96, 1, Math.PI, Math.PI), m.poli);
  const tCab = tapa(new THREE.CircleGeometry(0.60, 96), m.cabeza);
  const tCue = tapa(new THREE.PlaneGeometry(0.36, 0.62), m.cuello); tCue.position.y = 0.58;
  casquete.add(tCasq); inserto.add(tIns); cabeza.add(tCab, tCue);
  const tapas = [tCasq, tIns, tCab, tCue];

  inserto.position.y = 0.02; cabeza.position.y = 0.04;
  raiz.rotation.z = -0.62; raiz.rotation.y = 0.25;

  return { raiz, casquete, inserto, cabeza, ext, int, aro, banda, insExt, insInt, insAro, esfera, cuello, agujeros, bordes, normalAgujero, tapas };
}

// ------------------------------------------------------------ puntos de interés
// camLocal: dirección de cámara en el espacio local del modelo (la boca mira a +Y)
function definirPuntos(M) {
  return [
    { titulo: 'Casquete de titanio poroso',
      texto: 'Superficie porosa para la fijación biológica sin cemento. El hueso crece dentro de la estructura y asegura el implante a largo plazo.',
      obj: M.casquete, pos: new THREE.Vector3(0.30, -0.86, 0.40),
      focos: [M.ext], camLocal: new THREE.Vector3(0.42, -0.50, 0.76), margen: 1.75, modo: 'normal' },

    { titulo: 'Aro pulido con press-fit integrado',
      texto: 'El diseño incorpora un press-fit de 1,6 mm para la estabilidad primaria inmediata al impactar el cotilo en el acetábulo.',
      obj: M.casquete, pos: new THREE.Vector3(0.98, -0.03, 0.22),
      focos: [M.aro, M.banda], camLocal: new THREE.Vector3(0.60, 0.20, 0.77), margen: 1.55, modo: 'normal' },

    { titulo: 'Superficie interna pulida',
      texto: 'Minimiza el desgaste del inserto de doble movilidad y prolonga la vida útil del implante. Se muestra el corte para ver el interior.',
      obj: M.casquete, pos: new THREE.Vector3(-0.34, -0.50, 0.62),
      focos: [M.int], camLocal: new THREE.Vector3(0.10, 0.62, 0.78), margen: 1.25, modo: 'corte' },

    { titulo: 'Inserto de doble movilidad (EndoDur)',
      texto: 'Convierte el MobileLink en un sistema modular de movilidad dual y aloja los revestimientos de polietileno del sistema BiMobile.',
      obj: M.inserto, pos: new THREE.Vector3(0.70, -0.16, 0.42),
      focos: [M.insExt, M.insAro, M.insInt], camLocal: new THREE.Vector3(0.48, 0.44, 0.76), margen: 2.10, modo: 'explotar' },

    { titulo: 'Cabeza femoral de doble articulación',
      texto: 'La cabeza articula dentro del revestimiento y el revestimiento dentro del cotilo: mayor rango de movilidad y menor riesgo de luxación.',
      obj: M.cabeza, pos: new THREE.Vector3(0.44, 0.16, 0.38),
      focos: [M.esfera, M.cuello], camLocal: new THREE.Vector3(0.42, 0.40, 0.81), margen: 1.85, modo: 'explotar' },

    { titulo: 'Orificios para tornillos',
      texto: 'Permiten fijación adicional con tornillos cuando la calidad ósea lo requiere. Se cierran con tapones cuando no se utilizan.',
      obj: M.casquete, pos: M.normalAgujero[0].clone().multiplyScalar(1.02),
      focos: [...M.agujeros, ...M.bordes],
      camLocal: M.normalAgujero[0].clone().add(new THREE.Vector3(0, 0.55, 0.25)).normalize(), margen: 2.30, modo: 'normal' },
  ];
}

// ------------------------------------------------------------ util
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
function tween(ms, fn, done) {
  const t0 = performance.now();
  const paso = () => { const k = Math.min(1, (performance.now() - t0) / ms); fn(ease(k)); if (k < 1) requestAnimationFrame(paso); else if (done) done(); };
  requestAnimationFrame(paso);
}

// ------------------------------------------------------------ montaje
export function montarVisor({ host, capaPuntos, panelTitulo, panelTexto, botones = {}, hero = false, alListo, alCambiar }) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) { return null; }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.localClippingEnabled = true;
  renderer.domElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;touch-action:none;cursor:grab;';
  host.appendChild(renderer.domElement);
  renderer.domElement.addEventListener('pointerdown', () => renderer.domElement.style.cursor = 'grabbing');
  window.addEventListener('pointerup', () => renderer.domElement.style.cursor = 'grab');

  const escena = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  escena.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

  const cam = new THREE.PerspectiveCamera(30, 1, 0.1, 60);
  const CAM0 = new THREE.Vector3(2.9, 1.6, 3.4);
  cam.position.copy(CAM0);

  escena.add(new THREE.HemisphereLight(0xffffff, 0xd9e3e6, 0.55));
  const sol = new THREE.DirectionalLight(0xffffff, 1.5); sol.position.set(3, 6, 2.5); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); sol.shadow.radius = 6; sol.shadow.bias = -0.0004;
  Object.assign(sol.shadow.camera, { left: -3.5, right: 3.5, top: 3.5, bottom: -3.5, near: 1, far: 16 });
  const relleno = new THREE.DirectionalLight(0xe8f4f6, 0.5); relleno.position.set(-4, 2, -3);
  escena.add(sol, relleno);

  const piso = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.ShadowMaterial({ opacity: 0.17 }));
  piso.rotation.x = -Math.PI / 2; piso.position.y = -1.25; piso.receiveShadow = true; escena.add(piso);

  const m = materiales();
  const M = construirCotilo(m);
  escena.add(M.raiz);

  const ctl = new OrbitControls(cam, renderer.domElement);
  ctl.enableDamping = true; ctl.dampingFactor = 0.07; ctl.enablePan = false;
  ctl.minDistance = 3.0; ctl.maxDistance = 13; ctl.minPolarAngle = 0.22; ctl.maxPolarAngle = 1.62;
  ctl.target.set(0, 0.05, 0); ctl.autoRotate = true; ctl.autoRotateSpeed = hero ? 1.0 : 0.8;

  let autoPermitido = true, reanudar = null, animandoCam = false;
  ctl.addEventListener('start', () => { ctl.autoRotate = false; clearTimeout(reanudar); animandoCam = false; host.classList.add('tocado'); });
  ctl.addEventListener('end', () => { clearTimeout(reanudar); reanudar = setTimeout(() => { if (autoPermitido) ctl.autoRotate = true; }, 5000); });

  // ---------------------------------------------------------- materiales de estado
  // cada malla guarda: normal / foco (resaltada) / fantasma (atenuada)
  const piezas = [];
  M.raiz.traverse(o => {
    if (!o.isMesh || M.tapas.includes(o)) return;
    const base = o.material;
    const foco = base.clone();
    foco.color = base.color.clone().lerp(TEAL, 0.78);
    if (foco.emissive) { foco.emissive = TEAL_CLARO.clone(); foco.emissiveIntensity = 0.5; }
    if ('metalness' in foco) foco.metalness = Math.min(foco.metalness, 0.22);
    if ('roughness' in foco) foco.roughness = 0.5;
    foco.transparent = false; foco.opacity = 1; foco.depthWrite = true;
    const fantasma = base.clone();
    fantasma.transparent = true; fantasma.opacity = 0.30; fantasma.depthWrite = false;
    fantasma.color = base.color.clone().lerp(new THREE.Color(0xE9EDEF), 0.55);
    if ('envMapIntensity' in fantasma) fantasma.envMapIntensity = 0.45;
    if (fantasma.emissive) fantasma.emissive = new THREE.Color(0x000000);
    piezas.push({ mesh: o, base, foco, fantasma });
  });
  const porMesh = new Map(piezas.map(p => [p.mesh, p]));

  let enfocadas = null;   // Set de mallas resaltadas, o null
  function aplicarEstado() {
    for (const p of piezas) {
      let mat = p.base;
      if (enfocadas) mat = enfocadas.has(p.mesh) ? p.foco : p.fantasma;
      if (p.mesh.material !== mat) {
        mat.clippingPlanes = p.mesh.material.clippingPlanes;
        mat.clipShadows = true;
        p.mesh.material = mat;
      }
      p.mesh.castShadow = !enfocadas || enfocadas.has(p.mesh);
    }
  }
  function enfocar(meshes) {
    enfocadas = meshes && meshes.length ? new Set(meshes) : null;
    aplicarEstado();
  }

  const PUNTOS = definirPuntos(M);

  // ---------------------------------------------------------- marcadores en pantalla
  const puntos = hero ? [] : PUNTOS.map((p, i) => {
    const el = document.createElement('button');
    el.type = 'button'; el.className = 'hs'; el.setAttribute('aria-label', p.titulo);
    el.innerHTML = `<span class="hs-n">${i + 1}</span>`;
    if (capaPuntos) capaPuntos.appendChild(el);
    el.addEventListener('click', e => { e.stopPropagation(); activar(i); });
    return { ...p, el, world: new THREE.Vector3() };
  });

  // ---------------------------------------------------------- estados de la escena
  let explotado = false, corte = false, activo = -1;

  function setExplotar(on, ms = 850) {
    if (explotado === on) return;
    explotado = on;
    const a0 = M.inserto.position.y, b0 = M.cabeza.position.y;
    const a1 = on ? 1.05 : 0.02, b1 = on ? 2.1 : 0.04;
    tween(ms, k => { M.inserto.position.y = a0 + (a1 - a0) * k; M.cabeza.position.y = b0 + (b1 - b0) * k; });
    if (botones.explotar) botones.explotar.classList.toggle('on', on);
  }

  const planoLocal = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
  const plano = new THREE.Plane();
  function setCorte(on) {
    if (corte === on) return;
    corte = on;
    for (const p of piezas) {
      for (const mat of [p.base, p.foco, p.fantasma]) { mat.clippingPlanes = on ? [plano] : null; mat.clipShadows = true; mat.needsUpdate = true; }
    }
    M.tapas.forEach(t => { t.visible = on; });
    if (botones.corte) botones.corte.classList.toggle('on', on);
  }

  function setAuto(on) {
    autoPermitido = on; ctl.autoRotate = on;
    if (botones.auto) botones.auto.classList.toggle('on', on);
  }

  // ---------------------------------------------------------- activar un punto
  const qTmp = new THREE.Quaternion();
  function activar(i) {
    const p = PUNTOS[i]; if (!p) return;
    activo = i;
    puntos.forEach((q, k) => q.el.classList.toggle('on', k === i));
    if (capaPuntos && capaPuntos.parentElement) {
      const lista = document.querySelectorAll('.hs-item');
      lista.forEach((el, k) => el.classList.toggle('on', k === i));
    }
    if (panelTitulo) panelTitulo.textContent = p.titulo;
    if (panelTexto) panelTexto.textContent = p.texto;

    setCorte(p.modo === 'corte');
    enfocar(p.focos);
    if (alCambiar) alCambiar(i, p);

    // medir la pieza EN SU POSICION FINAL para encuadrarla bien
    const yIns = M.inserto.position.y, yCab = M.cabeza.position.y;
    const abierto = p.modo === 'explotar';
    M.inserto.position.y = abierto ? 1.05 : 0.02;
    M.cabeza.position.y = abierto ? 2.1 : 0.04;
    M.raiz.updateMatrixWorld(true);
    const caja = new THREE.Box3();
    for (const f of p.focos) caja.expandByObject(f);
    const esfera = caja.getBoundingSphere(new THREE.Sphere());
    M.inserto.position.y = yIns; M.cabeza.position.y = yCab;   // volver y animar
    setExplotar(abierto, 700);

    // cámara: dirección local del punto llevada al mundo
    M.raiz.getWorldQuaternion(qTmp);
    const dir = p.camLocal.clone().normalize().applyQuaternion(qTmp).normalize();
    if (dir.y < 0.12) { dir.y = 0.12; dir.normalize(); }        // nunca por debajo del piso

    const fov = THREE.MathUtils.degToRad(cam.fov);
    const aspecto = Math.max(0.6, cam.aspect);
    const fovH = 2 * Math.atan(Math.tan(fov / 2) * aspecto);
    const radio = Math.max(0.35, esfera.radius) * (p.margen || 1.8);
    const dist = THREE.MathUtils.clamp(radio / Math.sin(Math.min(fov, fovH) / 2), 3.2, 12);
    const mira = esfera.center.clone();
    const destino = mira.clone().add(dir.multiplyScalar(dist));
    const origen = cam.position.clone(), miraOrigen = ctl.target.clone();
    ctl.autoRotate = false; clearTimeout(reanudar); animandoCam = true;
    tween(800, k => { if (animandoCam) { cam.position.lerpVectors(origen, destino, k); ctl.target.lerpVectors(miraOrigen, mira, k); } }, () => {
      animandoCam = false;
      reanudar = setTimeout(() => { if (autoPermitido) ctl.autoRotate = true; }, 9000);
    });
  }

  function reiniciar() {
    activo = -1;
    puntos.forEach(q => q.el.classList.remove('on'));
    document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on'));
    setCorte(false); setExplotar(false); enfocar(null);
    if (panelTitulo) panelTitulo.textContent = 'Tocá un punto del modelo';
    if (panelTexto) panelTexto.textContent = 'Cada número señala una parte del sistema. Arrastrá para girar, usá la rueda o pellizcá para acercar.';
    const origen = cam.position.clone(), miraOrigen = ctl.target.clone();
    const mira0 = new THREE.Vector3(0, 0.05, 0);
    animandoCam = true;
    tween(700, k => { if (animandoCam) { cam.position.lerpVectors(origen, CAM0, k); ctl.target.lerpVectors(miraOrigen, mira0, k); } }, () => { animandoCam = false; });
    setAuto(true);
    if (alCambiar) alCambiar(-1, null);
  }

  // clic en el fondo = deseleccionar
  renderer.domElement.addEventListener('dblclick', () => { if (activo >= 0) reiniciar(); });

  if (botones.explotar) botones.explotar.addEventListener('click', () => { enfocar(null); activo = -1; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setExplotar(!explotado); });
  if (botones.corte) botones.corte.addEventListener('click', () => { enfocar(null); activo = -1; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setCorte(!corte); });
  if (botones.auto) botones.auto.addEventListener('click', () => setAuto(!autoPermitido));
  if (botones.reset) botones.reset.addEventListener('click', reiniciar);
  if (botones.siguiente) botones.siguiente.addEventListener('click', () => activar((activo + 1) % PUNTOS.length));

  // ---------------------------------------------------------- tamaño
  function ajustar() {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
  }
  new ResizeObserver(ajustar).observe(host); ajustar();

  // ---------------------------------------------------------- bucle
  const tmp = new THREE.Vector3(), dir2 = new THREE.Vector3(), centro = new THREE.Vector3(), haciaCam = new THREE.Vector3();
  let visible = true, t = 0;
  new IntersectionObserver(e => { visible = e[0].isIntersecting; }, { threshold: 0.02 }).observe(host);

  function cuadro() {
    requestAnimationFrame(cuadro);
    if (!visible) return;
    t += 0.016;
    ctl.update();
    if (corte) { M.raiz.updateMatrixWorld(); plano.copy(planoLocal).applyMatrix4(M.raiz.matrixWorld); }
    // pulso del resaltado
    if (enfocadas) {
      const k = 0.45 + Math.sin(t * 3.1) * 0.22;
      for (const p of piezas) if (enfocadas.has(p.mesh) && p.foco.emissive) p.foco.emissiveIntensity = k;
    }
    renderer.render(escena, cam);

    if (!puntos.length) return;
    const w = host.clientWidth, h = host.clientHeight;
    for (const p of puntos) {
      p.obj.updateWorldMatrix(true, false);
      p.obj.localToWorld(tmp.copy(p.pos));
      p.obj.getWorldPosition(centro);
      dir2.copy(tmp).sub(centro).normalize();
      haciaCam.copy(cam.position).sub(tmp).normalize();
      const cara = dir2.dot(haciaCam);
      tmp.project(cam);
      const x = (tmp.x * 0.5 + 0.5) * w, y = (-tmp.y * 0.5 + 0.5) * h;
      p.el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
      const detras = tmp.z > 1 || cara < -0.2;
      const esActivo = puntos[activo] === p;
      let op;
      if (esActivo) op = 1;                                  // el elegido siempre se ve
      else if (activo >= 0) op = detras ? 0 : 0.22;          // los demas se apagan
      else op = detras ? 0 : (cara < 0.05 ? 0.4 : 1);
      p.el.style.opacity = String(op);
      p.el.style.pointerEvents = op < 0.3 ? 'none' : 'auto';
      p.el.style.zIndex = esActivo ? '4' : '2';
    }
  }
  cuadro();
  if (alListo) alListo();
  return { activar, reiniciar, setExplotar, setCorte, setAuto, puntos: PUNTOS, total: PUNTOS.length };
}
