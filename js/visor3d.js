// Visor 3D interactivo — cotilo de doble movilidad (representación técnica)
// Three.js r165. Rotación libre, zoom, vista explotada, corte y puntos de interés.
import * as THREE from 'three';
import { OrbitControls } from '../vendor/OrbitControls.js';
import { RoomEnvironment } from '../vendor/RoomEnvironment.js';
import { CONSTRUCTORES, materiales } from './modelos.js';
import { ANATOMIAS, materialHueso, cuerpo as siluetaCuerpo } from './anatomia.js';

const TEAL = new THREE.Color(0x0095A1);
const TEAL_CLARO = new THREE.Color(0x5BC2C9);

// ------------------------------------------------------------ util
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
function tween(ms, fn, done) {
  const t0 = performance.now();
  const paso = () => { const k = Math.min(1, (performance.now() - t0) / ms); fn(ease(k)); if (k < 1) requestAnimationFrame(paso); else if (done) done(); };
  requestAnimationFrame(paso);
}

// ------------------------------------------------------------ montaje
export function montarVisor({ host, capaPuntos, panelTitulo, panelTexto, botones = {}, hero = false,
                             modelo = 'cotilo', config = {}, alListo, alCambiar }) {
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

  const cam = new THREE.PerspectiveCamera(30, 1, 0.1, 80);
  const CAM0 = new THREE.Vector3(2.9, 1.6, 3.4);
  const MIRA0 = new THREE.Vector3(0, 0.05, 0);
  cam.position.copy(CAM0);

  escena.add(new THREE.HemisphereLight(0xffffff, 0xd9e3e6, 0.55));
  const sol = new THREE.DirectionalLight(0xffffff, 1.5); sol.position.set(5, 9, 4); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); sol.shadow.radius = 6; sol.shadow.bias = -0.0004;
  Object.assign(sol.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 0.5, far: 30 });
  const relleno = new THREE.DirectionalLight(0xe8f4f6, 0.5); relleno.position.set(-4, 2, -3);
  escena.add(sol, relleno);

  const piso = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.17 }));
  piso.rotation.x = -Math.PI / 2; piso.position.y = -1.25; piso.receiveShadow = true; escena.add(piso);
  const m = materiales();

  const constructor = CONSTRUCTORES[modelo] || CONSTRUCTORES.cotilo;
  const M = constructor(m, config);
  escena.add(M.raiz);
  const PUNTOS = M.puntos;

  // contexto anatomico (oculto hasta que se pide)
  let anat = null, anatPiezas = [], silueta = null, zonaCuerpo = null;
  if (M.anatomia && ANATOMIAS[M.anatomia]) {
    const mh = materialHueso();
    const a = ANATOMIAS[M.anatomia](mh);
    anat = a.grupo; anatPiezas = a.piezas.concat(a.referencia || []);
    anat.visible = false;
    M.raiz.add(anat);

    zonaCuerpo = M.anatomia === 'femurTibia' ? 'rodilla' : 'cadera';
    if (M.anatomia !== 'campo') {
      const c = siluetaCuerpo(zonaCuerpo);
      silueta = c.grupo;
      // la silueta va en el espacio de la escena, no rotada con el implante
      // la silueta se escala y se calza para que su zona marcada coincida con el implante
      M.raiz.updateMatrixWorld(true);
      const cajaImp = new THREE.Box3().setFromObject(anat);
      const esfImp = cajaImp.getBoundingSphere(new THREE.Sphere());
      const escala = esfImp.radius / (M.anatomia === 'femurTibia' ? 2.6 : 1.9);
      silueta.scale.setScalar(escala);
      silueta.position.copy(esfImp.center);
      silueta.visible = false;
      escena.add(silueta);
      anatPiezas = anatPiezas.concat(c.piezas);
    }
  }

  // encuadre inicial segun el tamano real del modelo
  M.raiz.updateMatrixWorld(true);
  const cajaTot = new THREE.Box3();
  M.raiz.traverse(o => { if (o.isMesh && !anatPiezas.includes(o)) cajaTot.expandByObject(o); });
  const esfTot = cajaTot.getBoundingSphere(new THREE.Sphere());
  MIRA0.copy(esfTot.center);
  const distTot = esfTot.radius / Math.sin(THREE.MathUtils.degToRad(30) / 2) * 0.94;
  CAM0.set(0.58, 0.30, 0.86).normalize().multiplyScalar(distTot).add(MIRA0);
  cam.position.copy(CAM0);
  // el piso se apoya en la base del modelo
  piso.position.y = cajaTot.min.y - 0.12;

  const ctl = new OrbitControls(cam, renderer.domElement);
  ctl.enableDamping = true; ctl.dampingFactor = 0.07; ctl.enablePan = false;
  ctl.minDistance = distTot * 0.32; ctl.maxDistance = distTot * 2.6; ctl.minPolarAngle = 0; ctl.maxPolarAngle = Math.PI;
  ctl.target.copy(MIRA0); ctl.autoRotate = true; ctl.autoRotateSpeed = hero ? 1.0 : 0.8;

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

  let kExplo = 0;
  function setExplotar(on, ms = 850) {
    if (explotado === on) return;
    explotado = on;
    const k0 = kExplo, k1 = on ? 1 : 0;
    tween(ms, t => { kExplo = k0 + (k1 - k0) * t; M.explotar(kExplo); });
    if (botones.explotar) botones.explotar.classList.toggle('on', on);
  }

  const planoLocal = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
  const plano = new THREE.Plane();
  const hayCorte = M.tapas && M.tapas.length > 0;
  function setCorte(on) {
    if (!hayCorte) on = false;
    if (corte === on) return;
    corte = on;
    for (const p of piezas) {
      for (const mat of [p.base, p.foco, p.fantasma]) { mat.clippingPlanes = on ? [plano] : null; mat.clipShadows = true; mat.needsUpdate = true; }
    }
    M.tapas.forEach(t => { t.visible = on; });
    if (botones.corte) botones.corte.classList.toggle('on', on);
  }

  // ---------------------------------------------------------- contexto (3 estados)
  let contexto = 'solo';
  function marcarContexto() {
    const b = botones.contexto || {};
    for (const k of ['solo', 'hueso', 'cuerpo']) {
      if (b[k]) b[k].classList.toggle('on', contexto === k);
    }
  }
  function encuadrar(obj, holgura) {
    obj.updateMatrixWorld(true);
    const caja = new THREE.Box3().setFromObject(obj);
    const esf = caja.getBoundingSphere(new THREE.Sphere());
    const fov = THREE.MathUtils.degToRad(cam.fov);
    const fovH = 2 * Math.atan(Math.tan(fov / 2) * Math.max(0.6, cam.aspect));
    const d = esf.radius / Math.sin(Math.min(fov, fovH) / 2) * holgura;
    ctl.maxDistance = Math.max(d * 2.2, distTot * 2.6);
    cam.far = Math.max(80, d * 4); cam.updateProjectionMatrix();
    const dir = cam.position.clone().sub(ctl.target).normalize();
    const origen = cam.position.clone(), miraO = ctl.target.clone();
    const mira = esf.center.clone(), destino = mira.clone().add(dir.multiplyScalar(d));
    animandoCam = true;
    tween(820, k => { if (animandoCam) { cam.position.lerpVectors(origen, destino, k); ctl.target.lerpVectors(miraO, mira, k); } },
      () => { animandoCam = false; });
  }
  function setContexto(k) {
    if (!anat && k !== 'solo') k = 'solo';
    contexto = k;
    if (anat) anat.visible = (k === 'hueso' || k === 'cuerpo');
    if (silueta) silueta.visible = (k === 'cuerpo');
    marcarContexto();
    if (k !== 'solo') {
      enfocar(null); activo = -1;
      puntos.forEach(q => q.el.classList.remove('on'));
      document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on'));
      setExplotar(false); setCorte(false);
      encuadrar(k === 'cuerpo' ? silueta : anat, k === 'cuerpo' ? 1.05 : 1.08);
    } else {
      encuadrar(M.raiz, 1.0);
    }
    if (alCambiar) alCambiar(k === 'solo' ? -1 : (k === 'hueso' ? -2 : -3), null);
  }

  function setAuto(on) {
    autoPermitido = on; ctl.autoRotate = on;
    if (botones.auto) botones.auto.classList.toggle('on', on);
  }

  // acercar / alejar con botones (mismo recorrido que la rueda)
  const dirZoom = new THREE.Vector3();
  function zoom(factor) {
    ctl.autoRotate = false; clearTimeout(reanudar); animandoCam = false;
    dirZoom.copy(cam.position).sub(ctl.target);
    const d0 = dirZoom.length();
    const d1 = THREE.MathUtils.clamp(d0 * factor, ctl.minDistance, ctl.maxDistance);
    const origen = cam.position.clone();
    const destino = ctl.target.clone().add(dirZoom.normalize().multiplyScalar(d1));
    animandoCam = true;
    tween(320, k => { if (animandoCam) cam.position.lerpVectors(origen, destino, k); }, () => {
      animandoCam = false;
      reanudar = setTimeout(() => { if (autoPermitido) ctl.autoRotate = true; }, 7000);
    });
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

    if (contexto !== 'solo') { contexto = 'solo'; if (anat) anat.visible = false; if (silueta) silueta.visible = false; marcarContexto(); }
    setCorte(p.modo === 'corte');
    enfocar(p.focos);
    if (alCambiar) alCambiar(i, p);

    // medir la pieza EN SU POSICION FINAL para encuadrarla bien
    const abierto = p.modo === 'explotar';
    const kPrevio = kExplo;
    M.explotar(abierto ? 1 : 0);
    M.raiz.updateMatrixWorld(true);
    const caja = new THREE.Box3();
    for (const f of p.focos) if (f) caja.expandByObject(f);
    const esfera = caja.getBoundingSphere(new THREE.Sphere());
    M.explotar(kPrevio);                                        // volver y animar
    setExplotar(abierto, 700);

    // cámara: dirección local del punto llevada al mundo
    M.raiz.getWorldQuaternion(qTmp);
    const dir = p.camLocal.clone().normalize().applyQuaternion(qTmp).normalize();
    

    const fov = THREE.MathUtils.degToRad(cam.fov);
    const aspecto = Math.max(0.6, cam.aspect);
    const fovH = 2 * Math.atan(Math.tan(fov / 2) * aspecto);
    const radio = Math.max(0.35, esfera.radius) * (p.margen || 1.8);
    const dist = THREE.MathUtils.clamp(radio / Math.sin(Math.min(fov, fovH) / 2), ctl.minDistance, ctl.maxDistance);
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
    if (contexto !== 'solo') { contexto = 'solo'; if (anat) anat.visible = false; if (silueta) silueta.visible = false; marcarContexto(); }
    if (panelTitulo) panelTitulo.textContent = 'Tocá un punto del modelo';
    if (panelTexto) panelTexto.textContent = 'Cada número señala una parte del sistema. Arrastrá para girar, usá la rueda o pellizcá para acercar.';
    const origen = cam.position.clone(), miraOrigen = ctl.target.clone();
    const mira0 = MIRA0.clone();
    animandoCam = true;
    tween(700, k => { if (animandoCam) { cam.position.lerpVectors(origen, CAM0, k); ctl.target.lerpVectors(miraOrigen, mira0, k); } }, () => { animandoCam = false; });
    setAuto(true);
    if (alCambiar) alCambiar(-1, null);
  }

  // clic en el fondo = deseleccionar
  renderer.domElement.addEventListener('dblclick', () => { if (activo >= 0) reiniciar(); });

  if (botones.explotar) botones.explotar.addEventListener('click', () => { enfocar(null); activo = -1; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setExplotar(!explotado); });
  if (botones.corte && !hayCorte) botones.corte.style.display = 'none';
  if (botones.corte) botones.corte.addEventListener('click', () => { enfocar(null); activo = -1; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setCorte(!corte); });
  if (botones.auto) botones.auto.addEventListener('click', () => setAuto(!autoPermitido));
  if (botones.reset) botones.reset.addEventListener('click', reiniciar);
  if (botones.contexto) {
    for (const k of ['solo', 'hueso', 'cuerpo']) {
      const b = botones.contexto[k];
      if (!b) continue;
      if (!anat && k !== 'solo') { b.disabled = true; b.classList.add('off'); continue; }
      b.addEventListener('click', () => setContexto(k));
    }
    marcarContexto();
  }
  if (botones.zoomMas) botones.zoomMas.addEventListener('click', () => zoom(0.72));
  if (botones.zoomMenos) botones.zoomMenos.addEventListener('click', () => zoom(1.38));
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
  return { activar, reiniciar, setExplotar, setCorte, setAuto, zoom, setContexto, hayAnatomia: !!anat, puntos: PUNTOS, total: PUNTOS.length };
}
