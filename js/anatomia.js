// Contexto anatómico simplificado: dónde va colocado cada implante.
// Hueso translúcido para que el implante siga siendo el protagonista.
import * as THREE from 'three';

export function materialHueso() {
  return new THREE.MeshPhysicalMaterial({
    color: 0xEFE6D2, roughness: 0.82, metalness: 0,
    transparent: true, opacity: 0.42, depthWrite: false,
    clearcoat: 0.25, envMapIntensity: 0.7, side: THREE.DoubleSide,
  });
}

// deforma una esfera con ruido suave para que no parezca una pelota
function irregular(geo, amp = 0.06, freq = 2.2) {
  const p = geo.attributes.position;
  const v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    const n = Math.sin(v.x * freq) * Math.cos(v.y * freq * 1.3) * Math.sin(v.z * freq * 0.8);
    v.multiplyScalar(1 + n * amp);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  p.needsUpdate = true; geo.computeVertexNormals();
  return geo;
}

// ---------------------------------------------------------------- PELVIS
// Hemipelvis con el acetábulo mirando al mismo lado que la boca del cotilo (+Y local).
export function pelvis(mat) {
  const g = new THREE.Group();

  // cuerpo del ilíaco: placa ancha e irregular
  const ala = new THREE.Mesh(irregular(new THREE.SphereGeometry(2.5, 48, 32), 0.10, 1.6), mat);
  ala.scale.set(1, 1.15, 0.34);
  ala.position.set(-0.35, 1.75, 0);
  ala.rotation.z = -0.30;

  // masa periacetabular que rodea la cavidad
  const cuenco = new THREE.Mesh(irregular(new THREE.SphereGeometry(1.62, 56, 36), 0.05, 2.4), mat);
  cuenco.scale.set(1, 0.92, 1);

  // isquion y pubis: dos ramas que bajan
  const isquion = new THREE.Mesh(irregular(new THREE.CapsuleGeometry(0.42, 1.9, 8, 24), 0.08, 2), mat);
  isquion.position.set(0.45, -1.85, -0.25); isquion.rotation.z = 0.30;
  const pubis = new THREE.Mesh(irregular(new THREE.CapsuleGeometry(0.34, 1.7, 8, 24), 0.08, 2), mat);
  pubis.position.set(-1.35, -1.35, 0.35); pubis.rotation.z = -1.05;

  g.add(ala, cuenco, isquion, pubis);
  return { grupo: g, piezas: [ala, cuenco, isquion, pubis] };
}

// ---------------------------------------------------------------- FÉMUR PROXIMAL
// Canal medular alineado con el eje del vástago (-Y local).
export function femurProximal(mat) {
  const g = new THREE.Group();

  const diafisis = new THREE.Mesh(irregular(new THREE.CylinderGeometry(0.62, 0.55, 5.2, 40, 6), 0.035, 1.4), mat);
  diafisis.position.y = -1.9;

  const metafisis = new THREE.Mesh(irregular(new THREE.SphereGeometry(0.95, 40, 28), 0.07, 2), mat);
  metafisis.scale.set(1, 1.25, 0.9); metafisis.position.y = 0.55;

  // trocánter mayor
  const trocanter = new THREE.Mesh(irregular(new THREE.SphereGeometry(0.62, 32, 24), 0.09, 2.4), mat);
  trocanter.scale.set(0.85, 1.15, 0.85); trocanter.position.set(0.72, 1.0, 0);

  // cuello y cabeza originales, en gris muy tenue (referencia de lo que se reemplaza)
  const matRef = mat.clone(); matRef.opacity = 0.16;
  const cuelloNat = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.46, 1.15, 28), matRef);
  cuelloNat.position.set(-0.56, 1.42, 0); cuelloNat.rotation.z = 0.72;
  const cabezaNat = new THREE.Mesh(new THREE.SphereGeometry(0.62, 40, 28), matRef);
  cabezaNat.position.set(-0.98, 1.92, 0);

  g.add(diafisis, metafisis, trocanter, cuelloNat, cabezaNat);
  return { grupo: g, piezas: [diafisis, metafisis, trocanter], referencia: [cuelloNat, cabezaNat] };
}

// ---------------------------------------------------------------- RODILLA
export function femurTibia(mat) {
  const g = new THREE.Group();

  const femur = new THREE.Mesh(irregular(new THREE.CylinderGeometry(0.58, 0.80, 4.4, 40, 6), 0.04, 1.5), mat);
  femur.position.y = 2.85;
  const metaFem = new THREE.Mesh(irregular(new THREE.SphereGeometry(1.02, 40, 28), 0.06, 2), mat);
  metaFem.scale.set(1.10, 0.80, 0.95); metaFem.position.y = 0.95;

  const tibia = new THREE.Mesh(irregular(new THREE.CylinderGeometry(0.82, 0.52, 4.2, 40, 6), 0.04, 1.5), mat);
  tibia.position.y = -2.60;
  const metaTib = new THREE.Mesh(irregular(new THREE.SphereGeometry(0.98, 40, 28), 0.06, 2), mat);
  metaTib.scale.set(1.10, 0.62, 0.95); metaTib.position.y = -0.72;

  // peroné
  const perone = new THREE.Mesh(irregular(new THREE.CylinderGeometry(0.20, 0.16, 3.6, 24, 4), 0.05, 2), mat);
  perone.position.set(0.92, -2.35, -0.28);

  // rótula, por delante
  const rotula = new THREE.Mesh(irregular(new THREE.SphereGeometry(0.52, 32, 24), 0.08, 2.5), mat);
  rotula.scale.set(0.85, 1.05, 0.42); rotula.position.set(0, 0.62, 1.05);

  g.add(femur, metaFem, tibia, metaTib, perone, rotula);
  return { grupo: g, piezas: [femur, metaFem, tibia, metaTib, perone, rotula] };
}

// ---------------------------------------------------------------- MESA QUIRÚRGICA
// Contexto para los cementos: campo estéril, no anatomía.
export function campo(mat) {
  const g = new THREE.Group();
  const m2 = mat.clone(); m2.color = new THREE.Color(0xBFE3E6); m2.opacity = 0.32;
  const paño = new THREE.Mesh(new THREE.BoxGeometry(7.2, 0.08, 4.6), m2);
  paño.position.y = -0.06;
  g.add(paño);
  return { grupo: g, piezas: [paño] };
}


// ---------------------------------------------------------------- SILUETA DEL CUERPO
// Figura humana muy tenue para ubicar la zona del implante dentro del paciente.
// zona: 'cadera' | 'rodilla'  ·  devuelve la silueta ya escalada y posicionada.
export function cuerpo(zona = 'cadera') {
  const mat = new THREE.MeshStandardMaterial({
    color: 0xBFD8DC, roughness: 0.9, metalness: 0,
    transparent: true, opacity: 0.13, depthWrite: false, side: THREE.DoubleSide,
  });
  const g = new THREE.Group();
  const add = (mesh, x, y, z, rz = 0) => { mesh.position.set(x, y, z); mesh.rotation.z = rz; g.add(mesh); return mesh; };

  const cabeza = add(new THREE.Mesh(new THREE.SphereGeometry(0.62, 28, 20), mat), 0, 7.15, 0);
  cabeza.scale.set(0.86, 1, 0.86);
  add(new THREE.Mesh(new THREE.CapsuleGeometry(0.24, 0.36, 6, 18), mat), 0, 6.42, 0);
  const torso = add(new THREE.Mesh(new THREE.CapsuleGeometry(1.02, 1.9, 8, 28), mat), 0, 4.85, 0);
  torso.scale.set(1, 1, 0.62);
  const pelvisS = add(new THREE.Mesh(new THREE.CapsuleGeometry(0.95, 0.5, 8, 26), mat), 0, 3.05, 0);
  pelvisS.scale.set(1.05, 1, 0.66);
  for (const lx of [-1, 1]) {
    add(new THREE.Mesh(new THREE.CapsuleGeometry(0.27, 1.9, 6, 18), mat), lx * 1.25, 4.9, 0, lx * 0.16);
    add(new THREE.Mesh(new THREE.CapsuleGeometry(0.22, 1.7, 6, 18), mat), lx * 1.62, 3.05, 0, lx * 0.10);
    add(new THREE.Mesh(new THREE.CapsuleGeometry(0.46, 2.15, 8, 22), mat), lx * 0.52, 1.30, 0, lx * 0.05);
    add(new THREE.Mesh(new THREE.CapsuleGeometry(0.36, 2.05, 8, 22), mat), lx * 0.60, -1.35, 0);
    add(new THREE.Mesh(new THREE.CapsuleGeometry(0.24, 0.5, 6, 16), mat), lx * 0.62, -2.85, 0.22);
  }

  // anillo que marca la zona intervenida
  const marca = new THREE.Mesh(
    new THREE.TorusGeometry(0.95, 0.035, 10, 60),
    new THREE.MeshBasicMaterial({ color: 0x0095A1, transparent: true, opacity: 0.55 }));
  marca.rotation.x = Math.PI / 2;
  marca.position.set(zona === 'rodilla' ? 0.55 : 0.85, zona === 'rodilla' ? 0.05 : 2.75, 0);
  g.add(marca);

  return { grupo: g, piezas: g.children.slice(), marca };
}

export const ANATOMIAS = { pelvis, femurProximal, femurTibia, campo };

