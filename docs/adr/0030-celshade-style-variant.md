# 0030 — Cel/toon-shading style variant

## Status

Accepted

## Context

Second of the three deferred alternate rendering styles (AGENTS.md Future
Work; ADR 0029 shipped the first, blueprint/technical-drawing).

Real cel/toon shading is a quantized-band fragment shader (2-3 discrete
lightness steps instead of a continuous gradient) plus bold silhouette
outlines. VTK/PyVista's plotting API doesn't expose a built-in toon
fragment stage — that needs a custom GLSL shader replacement
(`vtkOpenGLPolyDataMapper` shader replacement API), which is out of reach
on this machine's headless software-GL backend (the same backend that caps
render resolution at 8192px, ADR 0025) and would be brittle even if it
worked. Approximated the *look* instead of the literal technique, using
tools already in this pipeline:

- The room's three flat quads already render as two flat tones (lit vs.
  shadowed), not a gradient, because each quad has uniform light incidence
  across its whole flat surface (ADR 0005) — real Phong shading with no
  gradient to speak of. `render_scene_blueprint.py` already noticed and
  relied on this same fact (ADR 0029). Needed zero changes here.
- The wedge cylinder is the one curved surface, where smooth shading *is*
  a continuous gradient — the opposite of toon banding. Fixed by turning
  `smooth_shading` off (flat per-facet shading) and lowering the
  cylinder's polygon count, added as two new `build_room_and_object()`
  parameters (`object_shading`, `cylinder_resolution`) following the same
  pattern as ADR 0029's `surface_shading`. A low-poly, flat-shaded solid
  reads as visibly faceted rather than smoothly graded — a different
  technique from quantized-band toon shading, but a visually similar
  "not-a-smooth-gradient" result. `CELSHADE_CYLINDER_RESOLUTION = 14` was
  picked empirically (rendered a few values): the default 96 sides is
  imperceptibly faceted even flat-shaded; 8 reads as a hard polygon,
  losing the wedge's taper/circle read; 14 keeps the silhouette
  recognizable while still visibly bevelled.
- `add_feature_edges()` (ADR 0029) for the black ink outline, run on the
  cylinder only. First attempt ran it (in near-black `#141414`) on the
  room quads too, at the room's *default* palette/shading (unchanged from
  ADR 0029's `render_scene.py`, so still near-black when unlit — see that
  ADR). Rendered, and the near-black outline nearly vanished against the
  near-black unlit room, including the three corner-highlight lines
  (mistakenly recolored to match) that exist specifically to stay visible
  in those dark corners (ADR 0013/0015's whole point). Fixed by leaving
  `add_edge_highlight_lines()` at its default white and running
  `add_feature_edges()` — black — on the cylinder alone, which sits
  against the much brighter lit shadow-circle regions where black
  reads fine.
- `extract_feature_edges()`'s dihedral-angle threshold for what counts as
  a "feature" defaults to 30° (PyVista's own default, now exposed as
  `add_feature_edges()`'s new `feature_angle` parameter). A 14-sided
  cylinder's side-facet-to-side-facet angle is ~360/14 ≈ 26° — under that
  default, so most facet edges weren't extracted at all; rendered once
  before checking and the object showed visible facets but no outline on
  most of them. Fixed by passing `feature_angle=15.0` for this variant.

## Decision

- `render_scene.py`:
  - `build_room_and_object()` gained `object_shading` (merged over new
    `DEFAULT_OBJECT_SHADING`, the prior hardcoded cylinder shading kwargs)
    and `cylinder_resolution` (default `DEFAULT_CYLINDER_RESOLUTION = 96`,
    the prior hardcoded value) parameters, same pattern as ADR 0029's
    `surface_shading`.
  - `add_feature_edges()` gained a `feature_angle` parameter (default 30°,
    PyVista's own default — unchanged behavior for existing callers).
- New `render_scene_celshade.py`: `CELSHADE_CYLINDER_RESOLUTION = 14`,
  `CELSHADE_OBJECT_SHADING` (`smooth_shading=False, specular=0.0`, raised
  `ambient` a little for the flat-shaded facets to stay readable),
  `CELSHADE_LINE_COLOR = "#141414"`. `build_scene_celshade()` composes
  `build_room_and_object()` (with those two overrides; palette/
  surface_shading left at default) + `add_fitted_lights()` (default three
  colors, unchanged) + `add_edge_highlight_lines()` (default white) +
  `add_feature_edges()` on the cylinder only (`feature_angle=15.0`).
  `__main__` reuses `SCENE_CAMERA_*` (ADR 0029) and writes
  `renders/scene_celshade.png`.
- Verified no regression: re-ran all five prior render scripts (default
  scene/icon variants + the blueprint variant) after this change — every
  output byte-identical (every new parameter defaults to prior behavior).

## Consequences

- A third establishing-shot look now exists, still sharing 100% of the
  geometry/camera/shadow-rig code with the default and with the blueprint
  variant — only shading model, polygon count, and outline placement
  differ.
- `object_shading`/`cylinder_resolution` are available to the next style
  variant (hand-drawn) too; hand-drawn will likely want a genuinely
  different technique (line jitter / stroke texture) rather than reusing
  these two as-is, but the palette/surface_shading/object_shading/
  cylinder_resolution override surface is now fully general for whatever
  it does need.
- The room quads' own boundary edges are still *not* run through
  `add_feature_edges()` in this variant (same as blueprint) — extending
  black ink linework to the room itself, not just the object, would need
  either a brighter unlit room (like blueprint's approach) or a
  differently-colored outline for the room vs. the object, neither
  attempted here.
