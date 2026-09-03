"""Cel/toon-shading style variant of `render_scene.py`'s wide establishing
shot: same geometry, camera, and shadow-mapped lighting rig, restyled for a
graphic/comic-panel read — bold black ink outlines plus a visibly faceted
(not smoothly gradient-shaded) floating object.

VTK's default renderer here has no built-in quantized/banded "toon shader"
fragment stage exposed through PyVista's plotting API (that would need a
custom GLSL shader replacement, unsupported on this machine's headless
software-GL backend — see render_icon_highres.py's own note on that
backend's other limits). Approximated instead with tools already in the
pipeline:

- The room's three flat quads already render as two flat tones (lit vs.
  shadowed) under real shading, with no gradient across a flat plane at
  uniform light incidence (ADR 0005) — see render_scene_blueprint.py's own
  note on this. That's already the "banded," not gradient, look toon
  shading wants, with zero changes needed here.
- The wedge cylinder is the one *curved* surface, and smooth Phong shading
  on a curve is a continuous gradient — the opposite of toon banding. Fixed
  by turning smooth_shading off (flat, per-facet shading) and lowering its
  polygon resolution (`CELSHADE_CYLINDER_RESOLUTION`, both new
  `build_room_and_object()` parameters as of ADR 0029) — a low-poly,
  flat-shaded cylinder reads as a faceted, quantized surface instead of a
  smooth gradient, similar in spirit to (though not the same technique as)
  quantized-band toon shading.
- `add_feature_edges()` (ADR 0029), run on the cylinder only, draws bold
  black ink outlines around every facet edge — comic-panel linework is the
  single most recognizable toon cue. Deliberately *not* run on the room
  quads too: their boundary edges run through the room's unlit areas,
  which (unchanged from the default palette/shading here) are already
  near-black, same as every other variant so far — a black outline there
  would be invisible against them. The existing white
  `add_edge_highlight_lines()` corner lines stay white for exactly that
  reason (visible against dark, unlike ink-black); only the object, which
  sits against the much brighter lit shadow-circle regions, gets the
  black-outline treatment.

The three shadow shapes are still real shadow-map output, same rig as
every other variant — this only restyles surfaces and outlines, not
lighting/geometry.
"""

import pyvista as pv

from render_scene import (
    RENDERS_DIR,
    SCENE_CAMERA_FOCAL_POINT,
    SCENE_CAMERA_POSITION,
    SCENE_CAMERA_UP,
    SCENE_CAMERA_VIEW_ANGLE,
    add_edge_highlight_lines,
    add_feature_edges,
    add_fitted_lights,
    build_room_and_object,
)

# Low enough to read as visibly faceted (not just "less glossy") once flat
# shading is on — found empirically by rendering a few values; 96 (the
# default, smooth-shaded elsewhere) is imperceptibly faceted even flat, 8
# reads as a hard polygon rather than a tapered wedge. 14 keeps the wedge's
# taper/circle silhouette recognizable while still visibly bevelled.
CELSHADE_CYLINDER_RESOLUTION = 14

# No specular highlight (a toon surface doesn't gloss), no smooth
# interpolation (flat per-facet shading is the point) — otherwise the
# object's default shading.
CELSHADE_OBJECT_SHADING = dict(smooth_shading=False, specular=0.0, diffuse=0.85, ambient=0.18)

CELSHADE_LINE_COLOR = "#141414"


def build_scene_celshade(plotter):
    meshes = build_room_and_object(
        plotter,
        object_shading=CELSHADE_OBJECT_SHADING,
        cylinder_resolution=CELSHADE_CYLINDER_RESOLUTION,
    )
    add_fitted_lights(plotter)
    add_edge_highlight_lines(plotter)  # stays white — see module docstring
    # feature_angle lowered below the default 30°: with only
    # CELSHADE_CYLINDER_RESOLUTION facets, adjacent side-facet normals
    # differ by only ~360/resolution degrees (~26° here) — under the
    # default threshold, so most facet edges wouldn't register as
    # "features" at all without this.
    add_feature_edges(
        plotter, {"cylinder": meshes["cylinder"]},
        color=CELSHADE_LINE_COLOR, line_width=2.5, feature_angle=15.0,
    )


if __name__ == "__main__":
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 1200), lighting="none")
    build_scene_celshade(plotter)

    # Same camera as render_scene.py's default look — a style variant, not
    # a recomposition.
    plotter.camera.position = SCENE_CAMERA_POSITION
    plotter.camera.focal_point = SCENE_CAMERA_FOCAL_POINT
    plotter.camera.up = SCENE_CAMERA_UP
    plotter.camera.view_angle = SCENE_CAMERA_VIEW_ANGLE

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDERS_DIR / "scene_celshade.png"
    plotter.screenshot(str(out_path))
    print(f"wrote {out_path}")
