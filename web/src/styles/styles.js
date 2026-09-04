import {
  BLUEPRINT_AMBIENT_INTENSITY,
  BLUEPRINT_LIGHT_COLORS,
  BLUEPRINT_LINE_COLOR,
  BLUEPRINT_PALETTE,
  CELSHADE_CYLINDER_RESOLUTION,
  CELSHADE_LINE_COLOR,
  CELSHADE_OBJECT_SHADING,
  DEFAULT_AMBIENT_INTENSITY,
  DEFAULT_CYLINDER_RESOLUTION,
  DEFAULT_LIGHT_COLORS,
  DEFAULT_OBJECT_SHADING,
  DEFAULT_PALETTE,
  GRAYSCALE_LIGHT_COLORS,
} from "../scene/palettes.js";

/**
 * One entry per switchable style — each references the shared palette/
 * shading data above so no style can drift out of sync with the others on
 * anything but its own listed overrides (mirrors render_scene.py's
 * build_room_and_object()/add_fitted_lights() override-dict pattern).
 *
 * `featureEdges`: null (no outline overlay), "full" (room + cylinder —
 * blueprint) or "cylinderOnly" (celshade). `cylinderResolution` picks
 * which of the two precomputed cylinder meshes (styleManager.js) is shown.
 *
 * Hand-drawn/sketchbook (the Python side's 4th style variant) is
 * deliberately not ported here — see README's "Live viewer" section.
 */
export const STYLES = {
  default: {
    label: "Default",
    palette: DEFAULT_PALETTE,
    objectShading: DEFAULT_OBJECT_SHADING,
    cylinderResolution: DEFAULT_CYLINDER_RESOLUTION,
    lightColors: DEFAULT_LIGHT_COLORS,
    ambientIntensity: DEFAULT_AMBIENT_INTENSITY,
    edgeColor: "#ffffff",
    featureEdges: null,
  },
  blueprint: {
    label: "Blueprint",
    palette: BLUEPRINT_PALETTE,
    objectShading: DEFAULT_OBJECT_SHADING,
    cylinderResolution: DEFAULT_CYLINDER_RESOLUTION,
    lightColors: BLUEPRINT_LIGHT_COLORS,
    ambientIntensity: BLUEPRINT_AMBIENT_INTENSITY,
    edgeColor: BLUEPRINT_LINE_COLOR,
    featureEdges: "full",
    featureEdgeColor: BLUEPRINT_LINE_COLOR,
  },
  celshade: {
    label: "Cel-shade",
    palette: DEFAULT_PALETTE,
    objectShading: CELSHADE_OBJECT_SHADING,
    cylinderResolution: CELSHADE_CYLINDER_RESOLUTION,
    lightColors: DEFAULT_LIGHT_COLORS,
    ambientIntensity: DEFAULT_AMBIENT_INTENSITY,
    edgeColor: "#ffffff",
    featureEdges: "cylinderOnly",
    featureEdgeColor: CELSHADE_LINE_COLOR,
  },
  grayscale: {
    label: "Grayscale",
    palette: DEFAULT_PALETTE,
    objectShading: DEFAULT_OBJECT_SHADING,
    cylinderResolution: DEFAULT_CYLINDER_RESOLUTION,
    lightColors: GRAYSCALE_LIGHT_COLORS,
    ambientIntensity: DEFAULT_AMBIENT_INTENSITY,
    edgeColor: "#ffffff",
    featureEdges: null,
  },
};

export const DEFAULT_STYLE_NAME = "default";
