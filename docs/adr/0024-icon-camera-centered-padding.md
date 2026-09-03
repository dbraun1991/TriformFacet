# 0024 — Icon camera centered for symmetric padding

## Status

Accepted

## Context

ADR 0023 maximized fill but didn't check whether the leftover black padding
was evenly distributed. Measured directly: it wasn't — 36px left vs. 167px
right, 187px top vs. 85px bottom. A real off-center bias, not just an
aspect-ratio artifact. Feedback: try to make the padding around the circles
match on all sides.

Reflected before changing anything (per request): "equal padding on all
four sides" is actually two separate goals. (1) *Centered* — left=right and
top=bottom — is fully achievable via a camera pan. (2) *All four sides
equal to each other* is only achievable if the shape cluster's own
bounding box is square; a camera zoom scales width and height by the same
factor, so it can't independently equalize a non-square box's padding
against a square frame. Measured the cluster's bbox at ~821×752px
(k=0.22) — about 1.09:1, not square — so (2) has a hard floor no camera
move alone can close without cropping content or accepting less fill.
Proceeded on that basis: solve (1) exactly, then re-maximize fill given the
new centered composition, leaving the small residual from (2) as an
accepted, explained limit rather than something to keep chasing.

## Decision

- **Pan**: computed the camera's local right/up axes (perpendicular to the
  view direction, derived from `position`/`focal_point`/`up`) and applied
  the *same* offset to both `position` and `focal_point` — a rigid
  sideways shift of the whole camera rig, not a rotation, so the viewing
  angle and zoom are unaffected. The exact offset was found by a 2D Newton
  iteration (finite-difference Jacobian, one refinement step) driving
  `(left − right, top − bottom)` to zero — calculated, not guessed.
- **Re-zoom**: re-centering shifts the fill slightly (the shape cluster
  isn't flat, so panning introduces a little parallax), so `k` was
  re-searched at each candidate with the pan re-solved each time. Landed
  on `k = 0.19` — bleed stays at 0 down to `k = 0.18`, real clipping
  (0px clearance) starts at `k = 0.17`; `0.19` leaves ~39px (~3.8%)
  clearance on the tighter axis, comparable in size to ADR 0023's own
  safety margin.
- Concretely: `position = (13.1272, 11.8836, 8.1087)`,
  `focal_point = (4.3872, 4.1316, 3.1687)`, `view_angle` unchanged at `32`.
- Result: left=39px, right=39px, top=82px, bottom=81px. Left/right and
  top/bottom pairs are equal (to the pixel); the pair-to-pair residual
  (~39px vs. ~82px) is the accepted, explained floor from the shape
  cluster's non-square bounding box — not something this camera move can
  close further without sacrificing fill or cropping a circle.

## Consequences

- `icon.png` is now genuinely centered, not just tightly filled — both
  properties verified by direct pixel measurement, not eyeballing.
- If a future change alters the shape cluster's bounding-box aspect ratio
  (e.g., a differently-proportioned floating object), the ~1.09:1 ratio
  driving the current residual would change too, and this whole
  pan+zoom search should be re-run rather than assumed still valid.
- The pan-solve method (rigid rig shift + Newton iteration on frame-edge
  margins) is reusable for any future icon recentering — documented in
  `render_icon.py`'s camera comment, not just here.
