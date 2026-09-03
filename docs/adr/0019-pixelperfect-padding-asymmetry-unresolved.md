# 0019 — Pixel-perfect's padding gap renders visibly asymmetric; root cause not found

## Status

Closed as moot (ADR 0026 removed `render_scene_pixelperfect.py` entirely)
— never resolved. Recorded so the investigation isn't repeated from scratch
if a similar gobo/circumscribed-light approach is ever tried again.

## Context

Feedback: `scene_pixelperfect.png`'s padding gap (ADR 0017) doesn't look
"aligned" between the two walls — the gap next to the corner line looks
noticeably wider on `wall_back` (blue) than on `wall_side` (rose).
Measured directly (pixel-column scan at a fixed image row): roughly a 2:1
width ratio (e.g. ~45px vs ~21px in one measurement), not a minor rounding
difference.

## Investigation

Verified the padding *calculation* is correct and symmetric before looking
anywhere else: `gobo_hole_range()` was called with numerically identical
inputs for both walls (`CYL_CENTER` is `(3,3,3)`, so `center_a`/`extent_a`
are literally the same numbers for wall_back's x-dimension and wall_side's
y-dimension), producing identical hole values (`(1.75, 8.5)` and
`(1.75, 7.5)` for both), and the inverse projection formula confirms both
reconstruct to exactly `LIGHT_PADDING = 0.5` at the target surface.

With the math ruled out, tested — and ruled out — every plausible
rendering-level explanation:

- **Camera perspective**: persisted with a camera constructed to be exactly
  symmetric under x↔y swap (`position=(26,26,16.2)`,
  `focal_point=(3,3,3.2)`).
- **Orthographic projection** (removes perspective's depth-based scaling
  entirely, leaving only directional foreshortening): persisted. A careful
  recomputation of each wall's padding-direction projection onto the
  camera's screen-right vector even predicted the *opposite* direction of
  asymmetry (rose's gap should read slightly *wider*, not narrower) and a
  much smaller magnitude (~13%) than observed (~100%+).
- **The wedge object's shadow**: persisted with the object entirely removed
  from the scene (room + lights + masks only).
- **The two gobo masks intersecting each other in 3D** (a real geometric
  fact at `MASK_OUTER_HALF = 60`, since both mask planes' extents reached
  the other's fixed-axis coordinate): persisted after shrinking
  `MASK_OUTER_HALF` to `15`, well below the ~32-unit threshold at which the
  masks stop intersecting — a plausible-looking hypothesis that turned out
  to be wrong.
- **Light/mask add order**: persisted when wall_back-first and
  wall_side-first orders were both tried.

What's left, not yet explained: the asymmetry is consistently tied to
*which axis* the light travels along (`axis=1`/y-traveling always shows
the wider gap, `axis=0`/x-traveling always shows the narrower one),
regardless of which wall/color is assigned to which axis. Plain circular
`fit_cone_half_angle` lights (`scene.png`, no gobo mask involved) have
never shown this kind of asymmetry anywhere in this project's history —
this looks specific to the gobo-mask/circumscribed-light combination
introduced in ADR 0016, not something inherent to having two
90°-apart lights.

## Decision

Leave `LIGHT_PADDING`/`gobo_hole_range` as they are — verified correct —
rather than apply an unexplained fudge-factor "fix" with no principled
basis. Document the open discrepancy here instead of re-investigating from
scratch next time it's noticed.

## Consequences

- `scene_pixelperfect.png`'s padding gap is real (not a math bug that
  produces zero padding on one side) but visibly uneven between the two
  walls — a cosmetic imperfection in an already-explicitly-experimental
  variant (`render_scene.py`'s `scene.png` remains the default, unaffected
  by this).
- Follow-up options, not attempted: try VTK's lower-level
  `vtkShadowMapBakerPass`/`vtkShadowMapPass` directly (outside PyVista's
  `enable_shadows()` convenience wrapper) for resolution/bias controls
  that might reveal or fix an internal precision difference between the
  two lights; or render each wall's gobo-lit square as a directly painted
  region (bypassing the light/shadow simulation for this specific look)
  if an exactly-even padding gap turns out to matter more than the
  "real lighting" approach ADR 0004 originally chose.
