# 0010 — Disable PyVista's default "light kit" on the Plotter

## Status

Accepted

## Context

After ADR 0009 (fitted cone angles), a second, fainter shadow was still
visible on every surface, offset from the intended one — most obviously two
overlapping rectangles on the floor. ADR 0009's fix addressed
cross-illumination *between the three explicit lights*, so this remaining
shadow had a different cause.

Inspecting `plotter.renderer.lights` directly (not just the `lights` dict
this script builds) showed **8** lights present, not 3:

```
0 pos (0.0, 0.0, 1.0)                    Headlight,      intensity 0.25
1 pos (0.11, 0.77, 0.63)                 Camera Light,   intensity 0.75
2 pos (-0.04, -0.97, 0.25)               Camera Light,   intensity 0.25
3 pos (0.94, 0.0, -0.34)                 Camera Light,   intensity 0.21
4 pos (-0.94, 0.0, -0.34)                Camera Light,   intensity 0.21
5 pos (3.0, 4.0, 35.0)   Scene Light (ours: floor)
6 pos (3.0, 35.0, 2.0)   Scene Light (ours: wall_back)
7 pos (35.0, 4.0, 2.0)   Scene Light (ours: wall_side)
```

Lights 0–4 were never added by this script. `pv.Plotter()`'s `lighting`
parameter defaults to `"light kit"`, which — independent of ADR 0004's
earlier removal of the explicit `enable_lightkit()` call — automatically
attaches a standard headlight + 3-point camera-relative light rig to every
new `Plotter` unless told not to. `enable_shadows()` casts shadows from
every light in the renderer, so these camera-relative lights (positioned
relative to the *camera*, not the scene) were each casting their own
shadow of the floating object, visible as a faint secondary shape offset
from the intended per-surface shadow.

## Decision

Pass `lighting="none"` to the `pv.Plotter(...)` constructor, so no lights
are attached automatically. Confirmed via `len(plotter.renderer.lights)`:
8 before this change, 3 (exactly the intended ones) after.

## Consequences

- Each surface now shows exactly one shadow, cast by exactly its own
  light — no offset secondary shape.
- The 5 removed lights were also contributing ambient fill/highlight
  outside each light's colored footprint; without them, everything outside
  the three inscribed circles (ADR 0009) renders essentially black rather
  than a dim gray. This reads as a stronger, more deliberate version of the
  "dark corner" look ADR 0009 already established as the intended
  tradeoff, not a regression.
- Confirms ADR 0004's shadow-artifact fix (dropping `enable_lightkit()`)
  addressed a *different* mechanism than this one — `enable_lightkit()` is
  a separate, explicit method call, while `lighting="light kit"` is the
  `Plotter` constructor's independent default. Both needed to be off.
