# 0005 — Lights pinned to the object's center axis, capped at 5x room size

## Status

Accepted

## Context

Two problems showed up with the initial oblique light placement (each light
positioned at some hand-picked off-axis point, aimed at the object):

1. **Shadow-map acne**: a serrated/jagged line near the top of each wall.
   Diagnosed as grazing-incidence artifacts — each spotlight's cone, wide
   enough to light its own wall evenly, inevitably spilled at a near-90°
   angle onto the *perpendicular* wall (the two walls meet at 90°, so this
   is hard to avoid with an obliquely-placed, wide-cone light).

2. A later request for more "direct" lighting: pull each light back to 10x
   the room's size along the axis through the object, for near-parallel,
   sunlight-like rays.

Testing (2) in isolation (a single wall + floor, no occluding object)
showed a severe regression: most of the floor and the outer edges of both
walls went dark, as if the light weren't reaching them at all. This was
methodically isolated:

- Disabling `enable_shadows()` entirely: full, even coverage restored →
  confirms the *light/cone* itself was never the problem.
- Re-enabling shadows and testing `cone_angle` from 15° up to 75° at 10x
  distance: **no change** in the dark area at all → rules out cone angle as
  the cause.
- Testing light distance directly (14, 21, 35, 70, all at the same
  `cone_angle`): coverage got steadily worse as distance increased, cleanly
  isolating **light-to-scene distance ratio** as the actual variable, not
  cone width.

Conclusion: this is a VTK shadow-map limitation at large light-to-scene
distance ratios (likely in how the shadow camera's clipping range or
resolution is auto-derived at that scale) that isn't controllable through
PyVista's exposed API in this version.

## Decision

- **Axis-pinning**: each light shares two of the floating object's center
  coordinates exactly, varying only the coordinate normal to its target
  surface — placing it exactly on the axis through the object, perpendicular
  to that surface, instead of at an oblique angle. This incidentally
  resolved the grazing-incidence acne from problem (1) as well.
- **Distance cap**: pull each light back to `FAR = 5 * ROOM` along that
  axis, not the originally-requested 10x. 5x was the largest tested ratio
  with full, complete shadow coverage; the ray spread at that distance is
  still small (~8° vs ~4° at 10x), so it still reads as effectively direct,
  parallel light.

## Consequences

- Full, even illumination on all three surfaces, no dark strips.
- Light is very-nearly-but-not-exactly parallel (a ~4° looser cone than the
  10x version would have given).
- If VTK shadow-map controls become reachable later (e.g. driving
  `vtkShadowMapBakerPass` resolution/bias directly rather than through
  PyVista's `enable_shadows()`), the distance cap could potentially be
  relaxed back toward 10x.
