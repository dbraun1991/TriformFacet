# 0031 — Hand-drawn/sketchbook style variant

## Status

Accepted

## Context

Third and last of the three deferred alternate rendering styles
(blueprint/technical-drawing and cel/toon shipped first, ADR 0029/0030).

Unlike those two, there was no existing PyVista/VTK feature to lean on —
neither variant's shortcuts (flat two-tone shading from uniform incidence,
low-poly faceting, `extract_feature_edges()`) produce a *wobbly* line;
VTK draws geometry exactly as given. A "sketchy hand-drawn line" isn't
something the library provides, so it needed building from primitives:
`add_sketchy_line()` subdivides a straight edge into ~48 points and
displaces each one, perpendicular to the edge, by a sum of a few sine
waves at randomized-but-seeded frequency/phase/weight — smooth
low-frequency noise (not independent per-point jitter, which would read
as static/zigzag rather than a hand wobble) — then rebuilds it as a
`pv.MultipleLines` polyline. Each edge is drawn 2-3 times with different
seeds for a "multiple pencil attempts" look.

**First bug: the lines didn't render at all**, with no error. Root cause,
found by bisecting down to a minimal repro (a red line alone on a blank
background rendered fine; the same call inside the full scene did not):
the corner edges sit exactly on the seam between two already-opaque room
quads, and the sketchy line was drawn with `opacity=0.75` for a "layered
pencil strokes" blend effect. A translucent object positioned at the same
depth as already-rendered opaque geometry loses the depth test in the
standard depth-tested transparency pipeline and gets silently discarded —
a generic translucent-vs-opaque-at-equal-depth issue, not specific to this
scene, but one the codebase hadn't hit before (every previous unlit-line
overlay, `add_edge_highlight_lines`/`add_feature_edges`, happened to use
full opacity already). Fixed by defaulting `add_sketchy_line()`'s
`opacity` to `1.0`: each pass is fully opaque, but since the three passes
have independently randomized wobble, they still visibly diverge from
each other along the line's length, reading as multiple overlaid strokes
without needing alpha blending at all.

**Second issue, not a bug: near-black unlit surfaces.** Same fact ADR
0029 already found (default `ambient=0.12` crushes any base color to
near-black unless the void background is similarly dark) applies here
too — a first attempt used a bright cream "paper" background, and the
room read as a black silhouette cutout against it rather than warm paper.
Fixed the same way as the blueprint variant: a dark (not bright) void
background, paired with `surface_shading=dict(ambient=0.55, diffuse=0.55)`
so the warm tan walls stay visible unlit.

**Observed, not fixed: muted lit-circle colors.** With colored (non-neutral)
room-surface base colors under the default colored spotlights, the lit
regions come out as `light_color × base_color` (VTK's multiplicative
material model) — e.g. the blue spotlight over a warm-tan wall renders as
a desaturated sage-teal, not the saturated blue seen in every other
variant (all of which use a near-neutral base palette, where multiplying
by a color barely shifts it). Left as-is: the muted, slightly
"hand-tinted-photograph" quality reads as consistent with the hand-drawn
aesthetic rather than a defect, and this is a real optical consequence of
the deliberate palette choice, not something to "fix."

`add_feature_edges()`'s clean linework (unmodified from the blueprint/cel
variants) still handles the wedge cylinder's own outline — the wobble
treatment was scoped to the room's three corner edges only. See
Consequences for why.

## Decision

- New `render_scene_handdrawn.py`, self-contained — no new
  `render_scene.py` parameters were needed (unlike ADR 0029/0030, which
  each added override hooks to `build_room_and_object`/`add_feature_edges`
  used generically by later variants; this variant's only new mechanism,
  the sketchy-line generator, is specific enough to this style that it
  lives in this file rather than being generalized).
  - `HANDDRAWN_PALETTE`: dark sepia void, warm tan floor/walls, near-white
    object.
  - `HANDDRAWN_SURFACE_SHADING = dict(ambient=0.55, diffuse=0.55)`.
  - `_sketch_offset(t, seed, amplitude)`: smooth seeded sine-sum
    displacement over a `[0, 1]` parameter.
  - `add_sketchy_line(plotter, p0, p1, ...)`: builds `passes` (default 3)
    independently wobbled, fully-opaque `pv.MultipleLines` polylines
    approximating the straight segment `p0`→`p1`, each overshooting both
    endpoints slightly.
  - `add_sketchy_room_edges()`: applies it to the room's three shared
    corner edges (same three edges `add_edge_highlight_lines` draws
    straight).
  - `build_scene_handdrawn()` composes `build_room_and_object()` (custom
    palette/shading, default light colors) + `add_fitted_lights()` (also
    default colors) + `add_sketchy_room_edges()` + `add_feature_edges()`
    (cylinder only, unmodified/clean). `__main__` reuses `SCENE_CAMERA_*`
    (ADR 0029) and writes `renders/scene_handdrawn.png`.
- Verified no regression: re-ran all six prior render scripts (default
  scene/icon variants + blueprint + cel/toon) after this change — every
  output byte-identical. This variant touches no shared code at all, so
  that was expected rather than something that needed defending.

## Consequences

- All three deferred alternate-style variants (AGENTS.md Future Work) are
  now shipped: blueprint/technical-drawing (ADR 0029), cel/toon (ADR
  0030), hand-drawn (this ADR) — each its own script sharing the default's
  geometry/camera/shadow-mapping pipeline, differing only in
  palette/shading/linework.
- The wedge cylinder's own outline stays crisp/undistorted in this
  variant — applying the same wobble to it would need jittering ~100
  short facet-boundary segments (from `extract_feature_edges()`) coherently
  rather than independently (an independent per-segment jitter would read
  as a broken line, not one wobbly stroke around a curve), which needs
  either a continuous parametrization of the cylinder's silhouette curves
  or a segment-adjacency-aware jitter — neither built here. Scoped out as
  a further pass if hand-drawn ever needs the object to wobble too, not
  attempted in this round.
- `add_sketchy_line()` is generically usable for any straight edge in
  world space if a future variant wants it (it isn't scene-specific
  beyond taking two 3D points), even though it currently lives in this
  style-specific file rather than `render_scene.py`.
