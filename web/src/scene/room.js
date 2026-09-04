import * as THREE from "three";
import { CYL_CENTER, CYL_LENGTH, CYL_RADIUS, HEIGHT, ROOM } from "./constants.js";
import { buildWedgeCylinderGeometry } from "./wedgeCylinder.js";
import {
  DEFAULT_CYLINDER_RESOLUTION,
  DEFAULT_OBJECT_SHADING,
  DEFAULT_PALETTE,
  DEFAULT_SURFACE_SHADING,
} from "./palettes.js";

/** Explicit quad from four corners — ported from render_scene.py's quad(). */
function buildQuad(p0, p1, p2, p3) {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array([...p0, ...p1, ...p2, ...p3]);
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setIndex([0, 1, 2, 0, 2, 3]);
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Adds the room (floor + two walls) and the floating wedge cylinder to
 * `scene` — everything except lighting, mirroring
 * render_scene.py's build_room_and_object(). Returns the four meshes so a
 * caller (styles/styleManager.js) can swap materials/geometry live.
 */
export function buildRoomAndObject(
  scene,
  {
    palette = DEFAULT_PALETTE,
    surfaceShading = DEFAULT_SURFACE_SHADING,
    objectShading = DEFAULT_OBJECT_SHADING,
    cylinderResolution = DEFAULT_CYLINDER_RESOLUTION,
  } = {},
) {
  // DoubleSide: buildQuad()'s fixed corner winding doesn't happen to face
  // the establishing-shot camera consistently across all three planes
  // (floor/wall_back point opposite ways along their shared axis) — rather
  // than hand-tuning per-quad winding, render both sides, same pragmatic
  // choice as the wedge cylinder (wedgeCylinder.js).
  const surfaceMaterial = (color) =>
    new THREE.MeshPhongMaterial({ color, side: THREE.DoubleSide, ...surfaceShading });

  const floor = new THREE.Mesh(
    buildQuad([0, 0, 0], [ROOM, 0, 0], [ROOM, ROOM, 0], [0, ROOM, 0]),
    surfaceMaterial(palette.floor),
  );
  const wallBack = new THREE.Mesh(
    buildQuad([0, 0, 0], [ROOM, 0, 0], [ROOM, 0, HEIGHT], [0, 0, HEIGHT]),
    surfaceMaterial(palette.wallBack),
  );
  const wallSide = new THREE.Mesh(
    buildQuad([0, 0, 0], [0, ROOM, 0], [0, ROOM, HEIGHT], [0, 0, HEIGHT]),
    surfaceMaterial(palette.wallSide),
  );
  for (const mesh of [floor, wallBack, wallSide]) {
    mesh.receiveShadow = true;
    scene.add(mesh);
  }

  const cylinder = new THREE.Mesh(
    buildWedgeCylinderGeometry(CYL_RADIUS, CYL_LENGTH, cylinderResolution),
    new THREE.MeshPhongMaterial({
      color: palette.object,
      side: THREE.DoubleSide, // see wedgeCylinder.js — winding isn't guaranteed outward everywhere
      flatShading: cylinderResolution < DEFAULT_CYLINDER_RESOLUTION,
      ...objectShading,
    }),
  );
  cylinder.position.set(...CYL_CENTER);
  cylinder.castShadow = true;
  cylinder.receiveShadow = true;
  scene.add(cylinder);

  return { floor, wallBack, wallSide, cylinder };
}
