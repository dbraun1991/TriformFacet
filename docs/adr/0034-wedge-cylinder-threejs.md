# 0034 — Wedge cylinder re-derived as a hand-built three.js geometry

## Status

Accepted

## Context

`render_scene.py`'s `make_wedge_cylinder()` (ADR 0006) builds the floating
object by clipping a plain cylinder with two symmetric planar cuts via
`vtkClipClosedSurface`, which cuts *and* caps the result, keeping it a
closed manifold solid. Porting this to three.js (ADR 0033) needed either a
CSG library performing the equivalent boolean-clip operation, or a
hand-authored geometry satisfying the same three-silhouette guarantee ADR
0006 proved (end-on circle, top-down rectangle, side-view triangle).

## Decision

**Hand-built `THREE.BufferGeometry`** (`web/src/scene/wedgeCylinder.js`),
not a CSG library (rejected: `three-bvh-csg`, the closest three.js
equivalent to `vtkClipClosedSurface`, is pre-1.0 with no stable API
contract, and adds a dependency pair — itself plus `three-mesh-bvh` — for
a shape that has closed-form math). Mirroring VTK's clip *algorithm* would
also be the wrong instinct given ADR 0033's re-derivation framing: the
goal is the resulting solid, not a reimplementation of a general-purpose
boolean-clip operator this one shape doesn't need.

Worked the geometry through from `make_wedge_cylinder()`'s own cut-plane
math (radius, length, and the derived `slope = radius/length`) rather than
guessing a "close enough" tapered shape:

- The cut is a **flat plane** through the cylinder (`n_upper`/`n_lower`,
  origin at the full-circle end's top/bottom, exactly as in
  `render_scene.py`). At any intermediate `x`, the plane intersects the
  cylindrical surface in a **circle clipped by two horizontal chords** at
  `z = ±zBound(x)` — a lens/stadium cross-section, not an ellipse. (An
  ellipse would result from naively lerping the `z`-extent while holding
  `y` fixed at ±radius — a tempting shortcut, but not what a flat-plane cut
  through a cylinder actually produces.)
- `zBound(x) = radius * (x - xThin) / length` (0 at the thin/diametral end,
  `radius` at the full-circle end — the same linear taper `slope` encodes).
  The half-width of each cut face at that `x` is `w(x) = radius *
  cos(asin(zBound(x)/radius))`, which traces a quarter-circle arc against
  `x` (since `zBound` is linear in `x`) — i.e. the cut faces are flat
  planes in 3D, but their *boundary curve* is genuinely circular, not
  polygonal, and needs real subdivision to approximate smoothly, not just
  two straight edges.
- Both the chord-cut and the ellipse-shortcut constructions satisfy ADR
  0006's three cardinal-axis silhouette proofs identically — the
  difference only shows up from an oblique angle, which is exactly what
  the establishing-shot camera (`SCENE_CAMERA_POSITION`) uses. Chose the
  chord-cut version specifically because it's what actually matches the
  existing reference PNGs in that view, not just the three axis-aligned
  checks in isolation.

Implementation: five vertex groups, each pushing its own vertices (never
sharing indices across groups, even where positions coincide) so every
crease gets distinct per-face normals by construction:

1. **Right lateral arc strip** (`y ≈ +radius`): `θ ∈ [-θmax(x), +θmax(x)]`
   per `x`, radial outward normals.
2. **Left lateral arc strip** (`y ≈ -radius`): mirrored, `θ` centered on
   `π`.
3. **Top cut strip** (`z = +zBound(x)`): flat outward normal ∝
   `(-slope, 0, 1)`.
4. **Bottom cut strip** (`z = -zBound(x)`): flat outward normal ∝
   `(-slope, 0, -1)`.

A first pass copied `render_scene.py`'s own `n_upper`/`n_lower` vectors
verbatim (`(slope, 0, -1)` / `(slope, 0, 1)`) on the assumption they were
the cut faces' outward normals. They aren't: those are
`vtkClipClosedSurface` *clip-plane* normals, which point at the material
being cut away — the opposite convention from a resulting face's outward
surface normal. The bug was invisible in isolation (lighting direction
still looked plausible from most angles) but read as a flat, unlit,
"see-through"-looking taper once viewed closely in the live orbit viewer,
since the two cut strips make up most of the tapered half's visible
surface. Fixed by deriving the outward normal directly from each face's
own plane equation instead of reusing the Python source's vector: the top
face bounds kept material (`z ≤ zBound(x)`) from above, so outward — away
from the solid — is the gradient of `f(x,z) = z - zBound(x)`, i.e.
`(-slope, 0, 1)`; the bottom face mirrors to `(-slope, 0, -1)`.
5. **End cap** (triangle fan) at the full-circle end — reuses the two arc
   strips' own last-row vertices rather than generating fresh ones at that
   boundary, so the seam has no gap from mismatched tessellation density.

This is the three.js analog of `render_scene.py`'s `compute_normals(...,
split_vertices=True, ...)` fix (ADR 0006's own shading-bug fix for the
same curved/flat crease) — arrived at for free by construction, rather
than as a merge-then-split correction step.

Triangle winding is **not** guaranteed consistently outward across all
five patches (the two lateral arc strips are parameterized in opposite
rotational senses around the cylinder). Rather than hand-verify winding
per patch, the geometry is rendered with `side: THREE.DoubleSide`
(`web/src/scene/room.js`) — a pragmatic simplification also applied to the
room quads themselves, whose fixed corner winding likewise doesn't face
the establishing-shot camera consistently across all three planes (an
early-testing bug: one wall was silently backface-culled and missing
entirely until this fix).

Verified the same way ADR 0006 did: camera aimed down each cardinal axis
in the browser (`-x` end-on, `-z` top-down, `-y` side-on) confirmed a
clean circle, rectangle, and triangle respectively before trusting the
geometry in the oblique establishing-shot view.

## Consequences

- One JS module (`buildWedgeCylinderGeometry()`) is the full geometry
  spec — no external CSG dependency, keeping `web/`'s runtime dependency
  footprint at just `three` itself.
- `resolution` (matching `render_scene.py`'s own parameter) drives both
  angular and length-wise subdivision together, so the cel-shade style's
  low-poly look (14 vs. the default 96) falls out of the same code path
  used everywhere else, not a special case.
- Like ADR 0006's original, this construction is specific to the
  circle/rectangle/triangle wedge case — generalizing to a different
  target-shape combination would need re-deriving the cross-section math,
  not just tweaking parameters.
- `DoubleSide` rendering trades a small, negligible-at-this-mesh-size GPU
  cost for not having to hand-verify winding per patch — acceptable given
  the object's small triangle count, but worth revisiting if this
  construction is ever reused for a much larger mesh.
