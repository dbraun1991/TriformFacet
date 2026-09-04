import * as THREE from "three";
import { CYL_CENTER, HEIGHT, LIGHT_PADDING, ROOM } from "./constants.js";
import { DEFAULT_LIGHT_COLORS } from "./palettes.js";

/**
 * Half-angle (DEGREES — matches render_scene.py's return convention;
 * convert to radians at the SpotLight call site) for a spotlight's
 * circular footprint to land inscribed within a rectangular target surface
 * spanning [0,extentA] x [0,extentB], aimed at (centerA,centerB), from
 * `distance` away, shrunk by `padding`. Ported verbatim from
 * render_scene.py's fit_cone_half_angle().
 */
export function fitConeHalfAngle(distance, centerA, extentA, centerB, extentB, padding = 0) {
  const margin = Math.min(centerA, extentA - centerA, centerB, extentB - centerB) - padding;
  return THREE.MathUtils.radToDeg(Math.atan(margin / distance));
}

// Same 5x-room-size pull-back render_scene.py uses for near-parallel light
// — re-validate against three.js's own shadow-map behavior during the
// tuning pass (commit 3) rather than assuming VTK's 5x/10x cliff carries
// over; see README's "Differences from the Python renderer".
const FAR = 5 * ROOM;

/**
 * Adds the three inscribed-footprint spotlights + shadow mapping to
 * `scene` — mirrors render_scene.py's add_fitted_lights(). Returns
 * {floor, wallBack, wallSide} so styles/styleManager.js can recolor them
 * live.
 */
export function addFittedLights(scene, renderer, colors = DEFAULT_LIGHT_COLORS) {
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;

  function makeLight(position, color, coneHalfAngleDeg) {
    const light = new THREE.SpotLight(
      color,
      3, // intensity — not numerically portable from VTK's units, tuned by eye
      0, // distance=0, decay=0 below: no falloff, matches attenuation_values=(1,0,0)
      THREE.MathUtils.degToRad(coneHalfAngleDeg),
      0, // penumbra=0 — flat falloff inside the cone, matches VTK's exponent=0
      0, // decay
    );
    light.position.set(...position);
    light.target.position.set(...CYL_CENTER);
    light.castShadow = true;
    light.shadow.mapSize.set(2048, 2048);
    // Tight frustum around this light's own throw distance — see README
    // for the tuning-pass notes.
    light.shadow.camera.near = FAR - 20;
    light.shadow.camera.far = FAR + 5;
    light.shadow.bias = -0.0004;
    light.shadow.normalBias = 0.05;
    scene.add(light);
    scene.add(light.target);
    return light;
  }

  const floor = makeLight(
    [CYL_CENTER[0], CYL_CENTER[1], FAR],
    colors.floor,
    fitConeHalfAngle(FAR, CYL_CENTER[0], ROOM, CYL_CENTER[1], ROOM, LIGHT_PADDING),
  );
  const wallBack = makeLight(
    [CYL_CENTER[0], FAR, CYL_CENTER[2]],
    colors.wallBack,
    fitConeHalfAngle(FAR, CYL_CENTER[0], ROOM, CYL_CENTER[2], HEIGHT, LIGHT_PADDING),
  );
  const wallSide = makeLight(
    [FAR, CYL_CENTER[1], CYL_CENTER[2]],
    colors.wallSide,
    fitConeHalfAngle(FAR, CYL_CENTER[1], ROOM, CYL_CENTER[2], HEIGHT, LIGHT_PADDING),
  );

  // Small ambient term standing in for VTK's per-material ambient
  // coefficient (see palettes.js) — otherwise unlit areas go fully black,
  // unlike the Python renderer's per-material ambient=0.12.
  const ambient = new THREE.AmbientLight(0xffffff, 1.6);
  scene.add(ambient);

  return { floor, wallBack, wallSide, ambient };
}
