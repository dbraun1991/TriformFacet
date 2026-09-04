import * as THREE from "three";
import { CYL_CENTER } from "../scene/constants.js";
import { addFeatureEdges } from "../scene/featureEdges.js";
import { buildCylinderMesh } from "../scene/room.js";
import { DEFAULT_STYLE_NAME, STYLES } from "./styles.js";

// Weight of each light's color folded into the cylinder's emissive term —
// see the comment at its use site below for why this exists at all. Small:
// the wedgeCylinder.js winding fix (addQuad's reversed triangle order) is
// what actually makes the object read as reflecting all three light
// colors now — this is just a minor fill for the small sliver that's
// still genuinely unlit by design (the bottom cut face's outward -z side,
// which no light points toward).
const OBJECT_FILL_WEIGHT = 0.08;

/** Average of the three light colors, scaled by `weight` — a flat,
 * angle-independent self-tint approximating how much of each light's hue
 * the object "picks up" regardless of local surface orientation. */
function blendLightColors(lightColors, weight) {
  const blend = new THREE.Color(0, 0, 0);
  for (const hex of Object.values(lightColors)) {
    blend.add(new THREE.Color(hex));
  }
  return blend.multiplyScalar(weight / 3);
}

/**
 * Live style switching over one persistent scene graph — mutates existing
 * objects (material colors, light colors, ambient intensity, line
 * visibility/color) rather than disposing/rebuilding per switch, with one
 * deliberate exception: cel-shade's cylinder is a genuinely different
 * tessellation (14 low-poly flat-shaded facets vs. the default 96 smooth
 * ones), so both cylinder meshes are built once up front and toggled by
 * `.visible` rather than rebuilt on every switch.
 *
 * Feature-edge line sets (blueprint's full-scene outline, cel-shade's
 * cylinder-only outline) are likewise precomputed once here — their
 * topology depends only on a fixed threshold angle, not on runtime style
 * state — and switching only flips which set is visible.
 */
export function createStyleManager(scene, renderer, { meshes, lights, edgeLines }) {
  const { floor, wallBack, wallSide, cylinder: defaultCylinder } = meshes;

  const celshadeCylinder = buildCylinderMesh(
    STYLES.celshade.cylinderResolution,
    STYLES.celshade.palette.object,
    STYLES.celshade.objectShading,
  );
  celshadeCylinder.position.set(...CYL_CENTER);
  celshadeCylinder.visible = false;
  scene.add(celshadeCylinder);

  const fullEdges = addFeatureEdges(
    scene,
    renderer,
    [floor, wallBack, wallSide, defaultCylinder],
    { thresholdAngle: 30, lineWidth: 2.5 },
  );
  fullEdges.visible = false;

  const cylinderOnlyEdges = addFeatureEdges(scene, renderer, [celshadeCylinder], {
    thresholdAngle: 15,
    lineWidth: 2.5,
  });
  cylinderOnlyEdges.visible = false;

  let current = null;

  function applyStyle(styleName) {
    const style = STYLES[styleName];
    if (!style) throw new Error(`Unknown style: ${styleName}`);
    current = styleName;

    scene.background.set(style.palette.background);
    floor.material.color.set(style.palette.floor);
    wallBack.material.color.set(style.palette.wallBack);
    wallSide.material.color.set(style.palette.wallSide);

    const useDefaultCylinder = style.cylinderResolution === defaultCylinder.userData.resolution;
    defaultCylinder.visible = useDefaultCylinder;
    celshadeCylinder.visible = !useDefaultCylinder;
    const activeCylinder = useDefaultCylinder ? defaultCylinder : celshadeCylinder;
    activeCylinder.material.color.set(style.palette.object);
    // Small flat emissive fill for the one sliver that's genuinely unlit
    // by design (the bottom cut face's outward -z side — no light points
    // that way). The real "reflects each light's color" behavior comes
    // from correct geometry (wedgeCylinder.js's addQuad winding fix), not
    // from this — earlier investigation wrongly attributed the taper
    // reading as flat black to Lambertian grazing-incidence falloff and
    // added this at a much higher weight before the actual bug (inverted
    // triangle winding triggering three.js's DoubleSide back-face normal
    // auto-flip, silently negating otherwise-correct custom normals) was
    // found; see ADR 0033/0034 for the full story. Also tried, and
    // doesn't work: three.js Layers to restrict a fill light to one mesh
    // — light/object layer matching only gates against the camera's
    // layers, not per-receiving-object (confirmed live: enabling it
    // washed the whole room, not just the object).
    activeCylinder.material.emissive.copy(blendLightColors(style.lightColors, OBJECT_FILL_WEIGHT));

    lights.floor.color.set(style.lightColors.floor);
    lights.wallBack.color.set(style.lightColors.wallBack);
    lights.wallSide.color.set(style.lightColors.wallSide);
    lights.ambient.intensity = style.ambientIntensity;

    edgeLines.material.color.set(style.edgeColor);

    fullEdges.visible = style.featureEdges === "full";
    if (fullEdges.visible) fullEdges.material.color.set(style.featureEdgeColor);

    cylinderOnlyEdges.visible = style.featureEdges === "cylinderOnly";
    if (cylinderOnlyEdges.visible) cylinderOnlyEdges.material.color.set(style.featureEdgeColor);
  }

  applyStyle(DEFAULT_STYLE_NAME);

  return {
    applyStyle,
    getCurrentStyle: () => current,
    // Line2/LineMaterial track the viewport's pixel size — exposed so the
    // caller's resize handler can keep them in sync (see main.js).
    lineMaterials: [fullEdges.material, cylinderOnlyEdges.material],
  };
}
