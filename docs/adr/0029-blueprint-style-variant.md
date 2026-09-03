# 0029 — Blueprint/technical-drawing style variant

## Status

Accepted

## Context

First of the three deferred "alternate rendering styles" from AGENTS.md's
Future Work (blueprint/technical-drawing, cel/toon, hand-drawn — see also
ADR 0013's precedent of building these as separate side-by-side variants,
not a single direction picked unprompted).

Two design questions came up:

**How to differentiate the three lights without hue or lightness steps.**
The default scene uses three saturated colors (amber/blue/rose); the
grayscale icon variant (ADR 0027) uses three different lightness steps
instead. A blueprint/technical drawing conventionally reads as one ink
color on one paper color — introducing three different blues (or three
grays) to distinguish floor/wall_back/wall_side would read as "the
grayscale variant, but blue" rather than as its own genre. Decided instead
to light all three surfaces with the *same* color and let the linework and
shape alone carry the "which surface, which shadow" information — the
concept's "different observers, different truths" framing doesn't require
a distinct hue per observer, just a distinct *view*.

**How to keep the shadow shapes legible without color differentiation.**
Losing per-light hue costs the scene one legibility channel; shadows still
need to read. The room's three surfaces are flat planes with, by
construction (ADR 0005), uniform light incidence across each surface — so
real per-pixel Phong shading on a flat plane doesn't produce a gradient,
just two flat tones (lit vs. shadowed, i.e. direct+ambient vs. ambient
only). That's already exactly the flat, graphic two-tone a technical
illustration wants; no faking or redrawing of the shadow shapes was
needed, just picking a palette where the two tones stay visibly distinct.

First attempt used the same low `ambient=0.12` the default scene uses,
paired with a dark blueprint-blue palette — rendered, and the unlit tone
crushed to near-black (0.12 × a dark base color ≈ black), losing the wall
silhouette against the also-near-black void background. This is because
`ambient` scales the *base* surface color multiplicatively; a dark base
color needs a much higher ambient fraction to stay visible unlit, which
the default warm-neutral palette (light base colors) never needed. Fixed
by raising `ambient`/`diffuse` for this variant specifically (0.55/0.55)
paired with a brighter mid-blue base palette — required exposing
`surface_shading` as a second override parameter on `build_room_and_object`
alongside the existing `palette` one, since the two previously shared one
hardcoded `surface_kwargs` dict.

Also added `add_feature_edges()` — extracts each mesh's boundary and
sharp-crease edges (`PolyData.extract_feature_edges()`) and draws them as
bright unlit lines, the same "unlit cheat" pattern `add_edge_highlight_lines`
already uses (ADR 0013/0015) for the room's three shared corner edges, just
generalized to arbitrary meshes. Gives the wedge cylinder a crisp rim/taper
outline instead of relying on shading gradient alone to read as 3D — the
hallmark linework of a technical illustration.

## Decision

- `render_scene.py`:
  - `build_room_and_object(plotter, palette=None, surface_shading=None)` —
    added `surface_shading`, merged over new `DEFAULT_SURFACE_SHADING`
    (`smooth_shading=True, specular=0.05, ambient=0.12, diffuse=0.9`, the
    prior hardcoded values). Also now returns the four meshes it built
    (`{"floor", "wall_back", "wall_side", "cylinder"}`) instead of nothing,
    so a caller can post-process them.
  - New `add_feature_edges(plotter, meshes, color="#ffffff", line_width=1.5)`
    — draws boundary + feature-angle-45° crease edges of each given mesh as
    unlit lines.
  - New `SCENE_CAMERA_POSITION`/`FOCAL_POINT`/`UP`/`VIEW_ANGLE` module
    constants, extracted from `render_scene.py`'s own `__main__` (values
    unchanged) so a style variant can reuse the exact same wide-shot camera
    instead of duplicating the numbers — the same reason `render_icon.py`
    exposes `ICON_CAMERA_*`.
- New `render_scene_blueprint.py`: `BLUEPRINT_PALETTE` (near-black void
  background, mid-blue floor/walls, near-white object),
  `BLUEPRINT_SURFACE_SHADING` (`ambient=0.55, diffuse=0.55`),
  `BLUEPRINT_LIGHT_COLORS` (all three surfaces lit with the same
  `#eaf4ff`), `BLUEPRINT_LINE_COLOR`. `build_scene_blueprint()` composes
  `build_room_and_object()` + `add_fitted_lights()` +
  `add_edge_highlight_lines()` + `add_feature_edges()` with these. `__main__`
  reuses `SCENE_CAMERA_*` verbatim and writes `renders/scene_blueprint.png`.
- Verified no regression: re-ran all five prior render scripts after this
  change — every output byte-identical (both new `build_room_and_object`
  parameters default to the prior hardcoded behavior).

## Consequences

- A second establishing-shot look now exists alongside the default, sharing
  100% of the geometry/camera/shadow-rig code — only palette, shading
  params, and light color differ.
- `build_room_and_object`'s new `surface_shading` parameter and mesh return
  value are available to the next style variant (cel/toon) too, likely
  useful there as well (toon shading typically wants its own flat/stepped
  shading model, not the default Phong).
- The blueprint shadow shapes are legible by brightness/shape, same as the
  grayscale icon variant, but with one further reduction: even the
  lightness-per-light signal is gone here (grayscale still varies which
  light is *brightest*; here all three are identical). Only the outline/
  position tells the three shadows apart, which is consistent with a real
  technical drawing's information density, but is a further step down in
  "which light did this" legibility from every prior variant.
