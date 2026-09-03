"""Blueprint/technical-drawing style variant of `render_scene.py`'s wide
establishing shot: same geometry, camera, and shadow-mapped lighting rig
(via `build_room_and_object()` / `add_fitted_lights()`), just restyled —
ink-white linework on a deep blueprint-blue ground instead of the default's
warm neutral palette and amber/blue/rose lights.

Two things do the actual work, both reused rather than invented:

- A single uniform light color (`BLUEPRINT_LIGHT_COLORS`, via the same
  `colors=` override `add_fitted_lights()` already gained for the
  grayscale icon variant, ADR 0027) instead of three different hues. The
  three flat room surfaces have (by construction, ADR 0005) uniform
  incidence angle, so real per-pixel Phong shading naturally comes out as
  two flat tones per surface — lit vs. shadowed — with no third hue
  distinguishing which light did it (the whole point of the colored
  default) and no shading gradient either, exactly the flat, graphic read
  a blueprint wants.
- `add_feature_edges()` (new in `render_scene.py`) draws each mesh's
  boundary/crease edges as bright unlit lines on top — the room's four
  quad edges plus the wedge cylinder's circular rim and two taper
  creases — giving the object a crisp technical-illustration outline
  instead of relying on shading gradient alone to read as 3D.

The three shadow shapes (rectangle/circle/triangle) are still real shadow
map output, not redrawn/faked — same shadow rig as every other variant.
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

BLUEPRINT_PALETTE = {
    "background": "#071b33",  # near-black void outside the room silhouette
    "floor": "#2f6fd0",
    "wall_back": "#3878da",
    "wall_side": "#2a63bf",
    "object": "#eaf4ff",
}

# Default ambient (0.12) crushes this dark palette's unlit areas to
# near-black (see build_room_and_object's docstring) — raised so the
# unlit room still reads as a flat, visible blue instead of vanishing into
# the background void.
BLUEPRINT_SURFACE_SHADING = dict(ambient=0.55, diffuse=0.55)

# One color for all three lights, deliberately not amber/blue/rose (or the
# grayscale variant's three different grays) — a blueprint's "which light
# did this" signal comes from the linework/shape alone, not from hue or
# lightness. Flat lit/shadowed two-tone per surface (see module docstring).
BLUEPRINT_LIGHT_COLORS = {
    "floor": "#eaf4ff", "wall_back": "#eaf4ff", "wall_side": "#eaf4ff",
}

BLUEPRINT_LINE_COLOR = "#eaf4ff"


def build_scene_blueprint(plotter):
    meshes = build_room_and_object(
        plotter, palette=BLUEPRINT_PALETTE, surface_shading=BLUEPRINT_SURFACE_SHADING,
    )
    add_fitted_lights(plotter, colors=BLUEPRINT_LIGHT_COLORS)
    add_edge_highlight_lines(plotter, color=BLUEPRINT_LINE_COLOR)
    add_feature_edges(plotter, meshes, color=BLUEPRINT_LINE_COLOR, line_width=2.5)


if __name__ == "__main__":
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 1200), lighting="none")
    build_scene_blueprint(plotter)

    # Same camera as render_scene.py's default look — a style variant, not
    # a recomposition.
    plotter.camera.position = SCENE_CAMERA_POSITION
    plotter.camera.focal_point = SCENE_CAMERA_FOCAL_POINT
    plotter.camera.up = SCENE_CAMERA_UP
    plotter.camera.view_angle = SCENE_CAMERA_VIEW_ANGLE

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDERS_DIR / "scene_blueprint.png"
    plotter.screenshot(str(out_path))
    print(f"wrote {out_path}")
