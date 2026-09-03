# 0013 — Two corner-visibility experiments: unlit edge lines vs. pixel-perfect + blockers

## Status

Superseded. The unlit-line approach was promoted to the default scene in
ADR 0015 (`render_scene_whiteline.py` no longer exists as a separate
file — `render_scene.py` *is* that version now). The pixel-perfect
approach's color-overlap problem, left unresolved here, was fixed in
ADR 0016 by replacing the blocker fins described below with gobo masks;
`render_scene_pixelperfect.py` still isn't the default scene, but for a
different reason now (a deliberately different look, not a bug). This ADR
is kept for the historical comparison and the fins' dead-end reasoning.

## Context

Since ADR 0010, everything outside the three lights' inscribed circles
renders flat black — the room reads as "three shapes floating in a void"
more than as a 3D space. Two directions were proposed to fix this, with
real, opposing tradeoffs (see the session discussion for the full pros/cons
write-up): (a) add unlit highlight lines along the room's three shared
edges, or (b) light every surface fully and pixel-perfectly with no dark
corner and no color overlap, likely requiring physical blocker geometry.

Asked to pursue both rather than choose one, as separate, comparable
outputs alongside the existing `scene.png`.

## Decision

Refactored `render_scene.py`'s `build_scene()` into `build_room_and_object()`
(room + object only) and `add_fitted_lights()` (the existing lighting),
so both experiments — and `render_icon.py` — can share the room/object
geometry without duplicating it.

**(a) `render_scene_whiteline.py` → `scene_whiteline.png`.** Adds
`add_edge_highlight_lines()`: three `pv.Line` segments along the room's
shared edges (floor/wall_back, floor/wall_side, wall_back/wall_side),
rendered with `lighting=False` and `render_lines_as_tubes=True` so they
stay a constant bright white regardless of which spotlight (if any) reaches
that spot. **Result: works cleanly.** The room's 3D structure becomes
immediately legible even in the unlit areas, with no change to the existing
lighting/shadow system and no new risk of reopening ADRs 0005/0009's bugs.

**(b) `render_scene_pixelperfect.py` → `scene_pixelperfect.png`.** Adds
`fit_cone_half_angle_circumscribed()` (reaches the farthest corner of the
target rectangle, not just the nearest edge) and `add_blocker_fins()`:
a diagonal quad along each shared edge, standing in the plane bisecting
the two surfaces that meet there, meant to intercept a light's
circumscribed overshoot before it reaches the neighboring surface without
blocking that surface's own dedicated light (which approaches from a
different angle).

**Result: a genuine partial success, with new problems, not a clean
solution:**

- Coverage is much fuller — each surface now shows nearly its whole
  rectangle instead of an inscribed circle, which is the shape ADR 0009's
  circles were only ever an approximation of.
- But the fins are clearly *visible* as solid gray-blue panels where a
  light hits them at a grazing angle, not blending into the dark corner as
  intended (they were colored near-black, but still have normal
  diffuse/specular shading, so an unlucky light angle reveals them).
- The fins also *self-shadow* the very surfaces they're meant to protect,
  near the seam — because a fin sized to block one surface's spill onto
  its neighbor sits close enough to also partially occlude that neighbor's
  own dedicated light near the same edge. This produces a visible dark
  "frame" border around each shape instead of a clean, invisible seam —
  arguably a worse-looking artifact than the plain dark corners it was
  meant to replace.

This matches the pros/cons discussion's prediction that a truly invisible,
pixel-perfect blocker was unlikely on a first attempt; per that
discussion's own terms, this is reported rather than iterated on further
in this pass.

## Consequences

- `scene_whiteline.png` is a clean, low-risk win — worth considering for
  promotion to the "main" scene, or keeping as a permanent alternate.
- `scene_pixelperfect.png` demonstrates the approach is *directionally*
  right (widened lights genuinely fill the rectangles) but the specific
  blocker implementation here isn't good enough to ship. Follow-up ideas,
  not attempted: color-match the fins more carefully to whatever they're
  lit by rather than a flat near-black; shrink/reshape them to intercept
  less of each surface's own dedicated light; or replace the fin approach
  entirely with a gobo/aperture mask between each light and the room
  (considered during design, set aside due to camera-obstruction risk —
  the camera sits on the same general side as two of the three lights, so
  a mask plane large enough to shape the beam risked blocking the camera's
  own view of the room).
- `render_scene.py`'s own `scene.png` and `render_icon.py`'s `icon.png`
  are untouched by this ADR — both still use `add_fitted_lights()`
  (inscribed circles, dark corners), unaffected by either experiment.
