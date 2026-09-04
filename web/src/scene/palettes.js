// Ported from src/render_scene.py's DEFAULT_* dicts and the style-variant
// scripts' BLUEPRINT_*/CELSHADE_* overrides (render_scene_blueprint.py,
// render_scene_celshade.py). One source of truth per style, reused by
// styles/styles.js.

export const DEFAULT_PALETTE = {
  background: "#eef1f5",
  floor: "#d9d4c6",
  wallBack: "#e6e2d6",
  wallSide: "#cec9ba",
  object: "#f2f0ea",
};

// VTK's ambient/diffuse/specular are per-material Phong coefficients — the
// closest three.js analog is MeshPhongMaterial's own params plus a low
// AmbientLight standing in for the ambient term (see scene/room.js).
export const DEFAULT_SURFACE_SHADING = { specular: "#050505", shininess: 6 };
export const DEFAULT_OBJECT_SHADING = { specular: "#666666", shininess: 22 };

export const DEFAULT_LIGHT_COLORS = {
  floor: "#ffb54d", // amber
  wallBack: "#5b9bd5", // blue
  wallSide: "#e8637f", // rose
};

export const GRAYSCALE_LIGHT_COLORS = {
  floor: "#ffffff",
  wallBack: "#d9d9d9",
  wallSide: "#b3b3b3",
};

export const BLUEPRINT_PALETTE = {
  background: "#071b33",
  floor: "#2f6fd0",
  wallBack: "#3878da",
  wallSide: "#2a63bf",
  object: "#eaf4ff",
};

export const BLUEPRINT_LIGHT_COLORS = {
  floor: "#eaf4ff",
  wallBack: "#eaf4ff",
  wallSide: "#eaf4ff",
};

export const BLUEPRINT_LINE_COLOR = "#eaf4ff";

// No specular highlight, flat per-facet shading is the point (see
// styles/styles.js — celshade also swaps in a low-poly cylinder geometry).
export const CELSHADE_OBJECT_SHADING = { specular: "#000000", shininess: 1 };
export const CELSHADE_CYLINDER_RESOLUTION = 14;
export const CELSHADE_LINE_COLOR = "#141414";

export const DEFAULT_CYLINDER_RESOLUTION = 96;

// Scene-wide AmbientLight intensity standing in for VTK's per-material
// ambient coefficient (see lights.js) — kept per-style since blueprint's
// deep-navy palette needs a bit more of it to stay readable against its
// near-black unlit background (render_scene_blueprint.py's own
// BLUEPRINT_SURFACE_SHADING raises ambient/diffuse for the same reason,
// though three.js's Phong material has no per-material ambient knob to
// mirror that with directly — this is the scene-wide analog).
export const DEFAULT_AMBIENT_INTENSITY = 0.18;
export const BLUEPRINT_AMBIENT_INTENSITY = 0.4;
