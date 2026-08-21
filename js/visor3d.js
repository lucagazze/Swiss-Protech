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
  // luz principal casi cenital: la sombra cae debajo de la pieza y se lee como apoyo,
  // no como una mancha suelta al costado
  const sol = new THREE.DirectionalLight(0xffffff, 1.5); sol.position.set(3.2, 11, 2.6); sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048); sol.shadow.radius = 5; sol.shadow.bias = -0.0004;
  Object.assign(sol.shadow.camera, { left: -6, right: 6, top: 6, bottom: -6, near: 0.5, far: 30 });
  const relleno = new THREE.DirectionalLight(0xe8f4f6, 0.5); relleno.position.set(-4, 2, -3);
  escena.add(sol, relleno);

  const piso = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.10 }));
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
      // escala anatomica real: un cotilo mide ~5 cm y una persona ~170 cm
      const CM_IMPLANTE = { pelvis: 5, femurProximal: 15, femurTibia: 16 };
      const ALTURA_PERSONA_CM = 170;
      M.raiz.updateMatrixWorld(true);
      const cajaImp = new THREE.Box3();
      M.raiz.traverse(o => { if (o.isMesh && !anatPiezas.includes(o)) cajaImp.expandByObject(o); });
      const esfImp = cajaImp.getBoundingSphere(new THREE.Sphere());
      const cajaSil = new THREE.Box3().setFromObject(silueta);
      const altoSil = Math.max(0.001, cajaSil.max.y - cajaSil.min.y);
      const cmImp = CM_IMPLANTE[M.anatomia] || 10;
      const altoPersona = (esfImp.radius * 2) * (ALTURA_PERSONA_CM / cmImp);
      const escSil = altoPersona / altoSil;
      silueta.scale.setScalar(escSil);
      silueta.position.copy(esfImp.center);      // la zona marcada calza con el implante
      // el anillo no crece con la persona: queda ajustado al implante
      // el anillo mide siempre lo mismo en el paciente (~25 cm), no crece con la pieza
      if (c.marca) c.marca.scale.setScalar((altoPersona * 0.075) / (0.95 * escSil));
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
  const fov0 = THREE.MathUtils.degToRad(30);
  const fovH0 = 2 * Math.atan(Math.tan(fov0 / 2) * Math.max(0.6, host.clientWidth / Math.max(1, host.clientHeight)));
  const distTot = esfTot.radius / Math.sin(Math.min(fov0, fovH0) / 2) * 1.06;
  CAM0.set(0.58, 0.30, 0.86).normalize().multiplyScalar(distTot).add(MIRA0);
  cam.position.copy(CAM0);
  // el piso se apoya en la base del modelo
  piso.position.y = cajaTot.min.y - 0.12;
  // la sombra se ajusta al tamaño real del modelo: ni recortada en los grandes
  // ni difusa de más en los chicos
  const rSol = Math.max(2.2, esfTot.radius * 1.7);
  Object.assign(sol.shadow.camera, { left: -rSol, right: rSol, top: rSol, bottom: -rSol, near: 0.5, far: rSol * 6 });
  sol.shadow.camera.updateProjectionMatrix();
  sol.position.copy(esfTot.center).add(new THREE.Vector3(rSol * 0.36, rSol * 2.4, rSol * 0.30));
  sol.target.position.copy(esfTot.center); escena.add(sol.target);

  const ctl = new OrbitControls(cam, renderer.domElement);
  ctl.enableDamping = true; ctl.dampingFactor = 0.07; ctl.enablePan = false;
  ctl.minDistance = distTot * 0.32; ctl.maxDistance = distTot * 2.6; ctl.minPolarAngle = 0; ctl.maxPolarAngle = Math.PI;
  ctl.target.copy(MIRA0); ctl.autoRotate = true; ctl.autoRotateSpeed = hero ? 1.0 : 0.8;

  let autoPermitido = true, reanudar = null, camTok = 0;
  ctl.addEventListener('start', () => { ctl.autoRotate = false; clearTimeout(reanudar); camTok++; host.classList.add('tocado'); });
  ctl.addEventListener('end', () => { clearTimeout(reanudar); reanudar = setTimeout(() => { if (autoPermitido) ctl.autoRotate = true; }, 5000); });

  // ------------------------------------------------ movimiento de camara (unico)
  // Interpola en ORBITA, no en linea recta: la direccion se slerpea y la distancia
  // avanza en progresion geometrica. Asi el acercamiento es siempre monotono y no
  // se produce el efecto de "se aleja y despues vuelve".
  // El token cancela cualquier movimiento anterior: nunca hay dos tweens escribiendo
  // la camara al mismo tiempo.
  const _off = new THREE.Vector3(), _dir = new THREE.Vector3(), _qa = new THREE.Quaternion(),
        _qb = new THREE.Quaternion(), _qk = new THREE.Quaternion();
  function moverCamara(miraDestino, distDestino, ms = 820, dirDestino = null, alTerminar = null) {
    const tok = ++camTok;
    const miraO = ctl.target.clone();
    _off.copy(cam.position).sub(miraO);
    const d0 = Math.max(1e-4, _off.length());
    const dir0 = _off.clone().divideScalar(d0);
    const dir1 = dirDestino ? dirDestino.clone().normalize() : dir0;
    _qa.identity(); _qb.setFromUnitVectors(dir0, dir1);
    const mira = miraDestino.clone();
    const d1 = THREE.MathUtils.clamp(distDestino, ctl.minDistance, ctl.maxDistance);
    const autoAntes = ctl.autoRotate;
    ctl.autoRotate = false;                       // que el giro no pelee con el tween
    if (ms <= 0) {
      ctl.target.copy(mira); cam.position.copy(mira).add(dir1.clone().multiplyScalar(d1));
      ctl.autoRotate = autoAntes; if (alTerminar) alTerminar(); return;
    }
    tween(ms, k => {
      if (camTok !== tok) return;                 // lo cancelo otro movimiento
      _qk.slerpQuaternions(_qa, _qb, k);
      _dir.copy(dir0).applyQuaternion(_qk);
      ctl.target.lerpVectors(miraO, mira, k);
      cam.position.copy(ctl.target).addScaledVector(_dir, d0 * Math.pow(d1 / d0, k));
    }, () => {
      if (camTok !== tok) return;
      ctl.autoRotate = autoAntes && autoPermitido;
      if (alTerminar) alTerminar();
    });
  }
  // distancia de camara necesaria para que entre una esfera de radio dado
  function distParaRadio(radio) {
    const fov = THREE.MathUtils.degToRad(cam.fov);
    const fovH = 2 * Math.atan(Math.tan(fov / 2) * Math.max(0.6, cam.aspect));
    return radio / Math.sin(Math.min(fov, fovH) / 2);
  }

  // ---------------------------------------------------------- materiales de estado
  // cada malla guarda: normal / foco (resaltada) / fantasma (atenuada)
  const piezas = [];
  M.raiz.traverse(o => {
    if (!o.isMesh || M.tapas.includes(o)) return;
    const base = o.material;
    const foco = base.clone();
    foco.color = base.color.clone().lerp(TEAL, 0.46);
    if (foco.emissive) { foco.emissive = TEAL.clone(); foco.emissiveIntensity = 0.30; }
    if ('metalness' in foco) foco.metalness = Math.max(0.42, Math.min(foco.metalness, 0.72));
    if ('roughness' in foco) foco.roughness = Math.min(foco.roughness, 0.62);
    foco.transparent = false; foco.opacity = 1; foco.depthWrite = true;
    const fantasma = base.clone();
    fantasma.transparent = true; fantasma.opacity = 0.30; fantasma.depthWrite = false;
    fantasma.color = base.color.clone().lerp(new THREE.Color(0xE9EDEF), 0.55);
    if ('envMapIntensity' in fantasma) fantasma.envMapIntensity = 0.45;
    if (fantasma.emissive) fantasma.emissive = new THREE.Color(0x000000);
    piezas.push({ mesh: o, base, foco, fantasma, side: base.side });
  });
  const porMesh = new Map(piezas.map(p => [p.mesh, p]));
  // solo el implante, sin el hueso: sirve para destacarlo dentro del contexto anatomico
  const mallasImplante = piezas.filter(p => !anatPiezas.includes(p.mesh)).map(p => p.mesh);

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
  // mallas que la camara sigue mientras se las esta mirando (null = nada)
  let seguido = null;

  // ---------------------------------------------------------- movimiento
  let enMov = false, faseMov = 0;
  function setMovimiento(on) {
    if (!M.animar) return;
    enMov = on;
    seguido = null;
    if (botones.movimiento) botones.movimiento.classList.toggle('on', on);
    if (on) {
      enfocar(null); activo = -1;
      puntos.forEach(q => q.el.classList.remove('on'));
      document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on'));
      setCorte(false); setExplotar(false, 400);
      ctl.autoRotate = false; clearTimeout(reanudar);
      faseMov = 0;
      // encuadrar el recorrido completo, no solo la posicion de reposo
      M.animar(0.5); M.raiz.updateMatrixWorld(true);
      const caja = new THREE.Box3();
      M.raiz.traverse(o => { if (o.isMesh && o.visible && !anatPiezas.includes(o)) caja.expandByObject(o); });
      M.animar(0); M.raiz.updateMatrixWorld(true);
      const c2 = new THREE.Box3();
      M.raiz.traverse(o => { if (o.isMesh && o.visible && !anatPiezas.includes(o)) c2.expandByObject(o); });
      caja.union(c2);
      const esf = caja.getBoundingSphere(new THREE.Sphere());
      const d = distParaRadio(esf.radius) * 1.12;
      ctl.maxDistance = Math.max(ctl.maxDistance, d * 1.6);
      moverCamara(esf.center, d, 720);
    } else {
      M.animar(null);
      encuadrarRadio(esfTot.radius * 1.06, 520);
    }
    if (alCambiar) alCambiar(on ? -4 : -1, on ? { titulo: 'En movimiento', texto: M.movimiento || '' } : null, '');
  }

  let kExplo = 0;
  function setExplotar(on, ms = 850) {
    if (explotado === on) return;
    explotado = on;
    const k0 = kExplo, k1 = on ? 1 : 0;
    tween(ms, t => { kExplo = k0 + (k1 - k0) * t; M.explotar(kExplo); });
    if (botones.explotar) botones.explotar.classList.toggle('on', on);
    if (on && enMov) setMovimiento(false);
  }

  const planoLocal = new THREE.Plane(new THREE.Vector3(-1, 0, 0), 0);
  const plano = new THREE.Plane();
  function setCorte(on) {
    if (corte === on) return;
    corte = on;
    for (const p of piezas) {
      for (const mat of [p.base, p.foco, p.fantasma]) {
        mat.clippingPlanes = on ? [plano] : null;
        mat.clipShadows = true;
        // al cortar se ven las caras internas: el solido no queda hueco
        mat.side = on ? THREE.DoubleSide : p.side;
        mat.needsUpdate = true;
      }
    }
    if (M.tapas) M.tapas.forEach(t => { t.visible = on; });
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
  // El producto es SIEMPRE el centro de la vista: la mira no se mueve del implante,
  // solo cambia cuanto entorno entra alrededor.
  function encuadrarRadio(radio, ms = 820) {
    const d = distParaRadio(radio);
    ctl.minDistance = Math.min(distTot * 0.32, d * 0.12);
    ctl.maxDistance = Math.max(d * 2.4, distTot * 2.6);
    cam.far = Math.max(80, d * 6); cam.updateProjectionMatrix();
    moverCamara(MIRA0, d, ms);
  }
  // encuadra el modelo tal como va a quedar con un factor de apertura dado,
  // para que la vista explotada entre entera en pantalla
  function encuadrarModelo(kDestino, ms = 700) {
    const kPrev = kExplo;
    M.explotar(kDestino); M.raiz.updateMatrixWorld(true);
    const caja = new THREE.Box3();
    M.raiz.traverse(o => { if (o.isMesh && o.visible && !anatPiezas.includes(o)) caja.expandByObject(o); });
    M.explotar(kPrev); M.raiz.updateMatrixWorld(true);
    if (caja.isEmpty()) return;
    const esf = caja.getBoundingSphere(new THREE.Sphere());
    const d = distParaRadio(esf.radius * 1.08);
    ctl.minDistance = Math.min(ctl.minDistance, d * 0.14);
    ctl.maxDistance = Math.max(ctl.maxDistance, d * 2.2);
    moverCamara(esf.center, d, ms);
  }
  // que tan lejos llega un objeto medido DESDE el centro del producto
  function radioDesdeProducto(obj) {
    if (!obj) return esfTot.radius;
    obj.updateMatrixWorld(true);
    const c = new THREE.Box3().setFromObject(obj);
    if (c.isEmpty()) return esfTot.radius;
    let r = 0; const v = new THREE.Vector3();
    for (const x of [c.min.x, c.max.x]) for (const y of [c.min.y, c.max.y]) for (const z of [c.min.z, c.max.z]) {
      r = Math.max(r, v.set(x, y, z).distanceTo(MIRA0));
    }
    return Math.max(r, esfTot.radius);
  }
  function setContexto(k) {
    if (!anat && k !== 'solo') k = 'solo';
    contexto = k;
    seguido = null;
    if (anat) anat.visible = (k === 'hueso' || k === 'cuerpo');
    if (silueta) silueta.visible = (k === 'cuerpo');
    // el plano de sombra vive a la escala del implante: dentro del cuerpo queda
    // un manchon suelto en medio del paciente, asi que se apaga
    piso.visible = (k === 'solo');
    marcarContexto();
    if (k !== 'solo') {
      enfocar(mallasImplante); activo = -1;   // el implante en color, el hueso atenuado
      puntos.forEach(q => q.el.classList.remove('on'));
      document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on'));
      setExplotar(false); setCorte(false);
      // en el cuerpo entra la persona entera; en el hueso, solo el segmento oseo.
      // en los dos casos la mira sigue siendo el implante, asi el zoom lo acerca a el.
      const radio = k === 'cuerpo'
        ? (silueta ? radioDesdeProducto(silueta) * 1.02 : radioDesdeProducto(anat) * 2.3)
        : radioDesdeProducto(anat) * 1.08;
      encuadrarRadio(radio);
    } else {
      encuadrarRadio(esfTot.radius * 1.06);
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
    clearTimeout(reanudar);
    dirZoom.copy(cam.position).sub(ctl.target);
    const d1 = dirZoom.length() * factor;
    moverCamara(ctl.target.clone(), d1, 320, null, () => {
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

    if (enMov) setMovimiento(false);
    if (contexto !== 'solo') { contexto = 'solo'; if (anat) anat.visible = false; if (silueta) silueta.visible = false; marcarContexto(); }
    setCorte(p.modo === 'corte');
    enfocar(p.focos);
    if (alCambiar) alCambiar(i, p, i + 1);

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
    

    const radio = Math.max(0.35, esfera.radius) * (p.margen || 1.8) * 0.82;
    const dist = distParaRadio(radio);
    const mira = esfera.center.clone();
    mira.y += esfera.radius * 0.16;   // deja aire arriba para la tarjeta de texto
    clearTimeout(reanudar);
    seguido = null;
    moverCamara(mira, dist, 800, dir, () => {
      // a partir de acá la cámara queda pegada a la pieza que se está mirando:
      // si la pieza se mueve (vista explotada, movimiento), la sigue
      seguido = p.focos.filter(Boolean);
      reanudar = setTimeout(() => { if (autoPermitido) ctl.autoRotate = true; }, 9000);
    });
  }

  function reiniciar() {
    activo = -1;
    puntos.forEach(q => q.el.classList.remove('on'));
    document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on'));
    setCorte(false); setExplotar(false); enfocar(null);
    if (enMov) setMovimiento(false);
    if (contexto !== 'solo') { contexto = 'solo'; if (anat) anat.visible = false; if (silueta) silueta.visible = false; marcarContexto(); }
    if (panelTitulo) panelTitulo.textContent = 'Tocá un punto del modelo';
    if (panelTexto) panelTexto.textContent = 'Cada número señala una parte del sistema. Arrastrá para girar, usá la rueda o pellizcá para acercar.';
    seguido = null;
    moverCamara(MIRA0, CAM0.distanceTo(MIRA0), 700, CAM0.clone().sub(MIRA0));
    setAuto(true);
    if (alCambiar) alCambiar(-1, null);
  }

  // clic en el fondo = salir del punto de interés. Un arrastre para girar NO cuenta como clic.
  (function () {
    const el = renderer.domElement;
    let px = 0, py = 0, pt = 0, valido = false;
    el.addEventListener('pointerdown', e => { px = e.clientX; py = e.clientY; pt = performance.now(); valido = true; });
    el.addEventListener('pointercancel', () => { valido = false; });
    el.addEventListener('pointerup', e => {
      if (!valido) return;
      valido = false;
      const movido = Math.hypot(e.clientX - px, e.clientY - py);
      if (movido > 6 || performance.now() - pt > 500) return;   // fue un giro, no un clic
      if (activo >= 0 || enMov || contexto !== 'solo' || explotado || corte) reiniciar();
    });
  })();

  if (botones.explotar) botones.explotar.addEventListener('click', () => { enfocar(null); activo = -1; seguido = null; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setExplotar(!explotado); encuadrarModelo(explotado ? 1 : 0); });
  if (botones.corte) botones.corte.addEventListener('click', () => { enfocar(null); activo = -1; seguido = null; puntos.forEach(q => q.el.classList.remove('on')); document.querySelectorAll('.hs-item').forEach(el => el.classList.remove('on')); setCorte(!corte); });
  if (botones.auto) botones.auto.addEventListener('click', () => setAuto(!autoPermitido));
  if (botones.reset) botones.reset.addEventListener('click', reiniciar);
  if (botones.movimiento) {
    if (!M.animar) botones.movimiento.style.display = 'none';
    else botones.movimiento.addEventListener('click', () => setMovimiento(!enMov));
  }
  // sin contexto anatomico el grupo entero desaparece (cementos, instrumental)
  if (botones.contexto && !anat && botones.contexto.solo) {
    const g = botones.contexto.solo.closest('.v-grupo');
    if (g) g.style.display = 'none';
  }
  if (botones.contexto) {
    for (const k of ['solo', 'hueso', 'cuerpo']) {
      const b = botones.contexto[k];
      if (!b) continue;
      if (!anat && k !== 'solo') { b.style.display = 'none'; continue; }
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
  const cajaSeg = new THREE.Box3(), esfSeg = new THREE.Sphere(), miraSeg = new THREE.Vector3();
  let visible = true, t = 0, tPrev = performance.now();
  new IntersectionObserver(e => { visible = e[0].isIntersecting; }, { threshold: 0.02 }).observe(host);

  function cuadro() {
    requestAnimationFrame(cuadro);
    const ahora = performance.now();
    const dt = Math.min(0.05, (ahora - tPrev) / 1000);   // en segundos, independiente del framerate
    tPrev = ahora;
    if (!visible) return;
    t += dt;
    if (enMov && M.animar) { faseMov = (faseMov + dt * 0.25) % 1; M.animar(faseMov); }
    // la camara acompana a la pieza que se esta mirando si esta se mueve
    if (seguido && seguido.length) {
      cajaSeg.makeEmpty();
      for (const f of seguido) cajaSeg.expandByObject(f);
      if (!cajaSeg.isEmpty()) {
        cajaSeg.getBoundingSphere(esfSeg);
        miraSeg.copy(esfSeg.center); miraSeg.y += esfSeg.radius * 0.16;
        if (ctl.target.distanceToSquared(miraSeg) > 1e-6) ctl.target.lerp(miraSeg, Math.min(1, dt * 6));
      }
    }
    ctl.update();
    if (corte) { M.raiz.updateMatrixWorld(); plano.copy(planoLocal).applyMatrix4(M.raiz.matrixWorld); }
    // pulso del resaltado
    if (enfocadas) {
      const k = 0.26 + Math.sin(t * 3.1) * 0.13;
      for (const p of piezas) if (enfocadas.has(p.mesh) && p.foco.emissive) p.foco.emissiveIntensity = k;
    }
    renderer.render(escena, cam);

    if (!puntos.length) return;
    const w = host.clientWidth, h = host.clientHeight;
    if (contexto !== 'solo') {   // en hueso/cuerpo los numeros solo estorban
      for (const p of puntos) { p.el.style.opacity = '0'; p.el.style.pointerEvents = 'none'; }
      return;
    }
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
      const fueraDeCuadro = tmp.z > 1;                       // detras de la camara: no se puede proyectar
      const atras = cara < -0.02;                            // del otro lado de la pieza
      const esActivo = puntos[activo] === p;
      // los del otro lado NO se ocultan: se ven a traves, en hueco, y se pueden tocar igual
      let op;
      if (fueraDeCuadro) op = 0;
      else if (esActivo) op = 1;                             // el elegido siempre se ve entero
      else if (activo >= 0) op = atras ? 0.42 : 0.62;
      else op = atras ? 0.5 : 1;
      p.el.style.opacity = String(op);
      p.el.style.pointerEvents = op < 0.05 ? 'none' : 'auto';
      p.el.style.zIndex = esActivo ? '6' : (atras ? '3' : '4');
      p.el.classList.toggle('atras', atras && !esActivo);
    }
  }
  cuadro();
  if (alListo) alListo();
  const api = { activar, reiniciar, setExplotar, setCorte, setAuto, zoom, setContexto, setMovimiento, hayMovimiento: !!M.animar, puntos: PUNTOS, total: PUNTOS.length };
  // enganche de diagnostico: permite medir la camara desde las pruebas automaticas
  api._d = { cam, ctl, escena, M, piso, get anat() { return anat; }, get silueta() { return silueta; }, get contexto() { return contexto; }, THREE };
  if (typeof window !== 'undefined' && !hero) window.__v3d = api;
  return api;
}
