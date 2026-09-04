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
5. **End cap** (triangle fan) at the full-circle end — reuses the two arc
   strips' own last-row vertices rather than generating fresh ones at that
   boundary, so the seam has no gap from mismatched tessellation density.

This is the three.js analog of `render_scene.py`'s `compute_normals(...,
split_vertices=True, ...)` fix (ADR 0006's own shading-bug fix for the
same curved/flat crease) — arrived at for free by construction, rather
than as a merge-then-split correction step.

### Two normal/winding bugs found via the live viewer, not by inspection

Both were invisible from casual review of the math and only showed up as
wrong shading once actually orbited close in the browser — the same
"render and look, don't just diff" discipline `AGENTS.md` already asks of
the Python side.

**Cut-face normal sign.** A first pass copied `render_scene.py`'s own
`n_upper`/`n_lower` vectors verbatim (`(slope, 0, -1)` / `(slope, 0, 1)`)
on the assumption they were the cut faces' outward normals. They aren't:
those are `vtkClipClosedSurface` *clip-plane* normals, which point at the
material being cut away — the opposite convention from a resulting face's
outward surface normal. Fixed by deriving the outward normal directly
from each face's own plane equation instead: the top face bounds kept
material (`z ≤ zBound(x)`) from above, so outward — away from the solid —
is the gradient of `f(x,z) = z - zBound(x)`, i.e. `(-slope, 0, 1)`; the
bottom face mirrors to `(-slope, 0, -1)` (both given above).

**Inverted triangle winding on the arc and cut strips — the bigger one.**
Even after the sign fix, the taper still showed no blue (from `wallBack`)
or amber (from `floor`) on most of its visible surface — only a thin
sliver, easy to mistake for "just needs more light." Cross-product
analysis of `addQuad()`'s original vertex order (`a,b,c` / `a,c,d`) showed
every arc and cut-strip quad's winding-derived normal was the *negative*
of its assigned explicit normal. Combined with `side: THREE.DoubleSide`
(`room.js`), this triggers three.js's standard shader chunk's back-face
normal auto-flip (`normal *= faceDirection`) for exactly the
outward-facing view that matters — silently negating an
already-analytically-correct custom normal back to wrong. `DoubleSide`
alone doesn't excuse getting winding right: it only removes *culling* as
a way to notice a mistake, while introducing this *auto-flip* as a new
way for the wrong winding to actively corrupt shading instead of just
hiding a face. The end cap fan (built directly with `indices.push()`, not
through `addQuad()`) happened to wind correctly from the start, matching
its own working, never-suspect round-end appearance — which is what made
this bug easy to miss initially (only *half* the geometry was affected).

Diagnosed by forcing `flatShading: true` on the live material (which
recomputes normals from screen-space position derivatives, ignoring the
stored attribute entirely) and comparing: flat-shaded was correct, smooth
(using the stored, per-vertex-verified-correct attribute) was wrong — the
data was right, so the fault had to be in which side the shader treated
that data as belonging to. Confirmed by cross-product before fixing.
Fixed by reversing `addQuad()`'s triangle order (`a,c,b` / `a,d,c`); no
change needed to any of the explicit normal formulas above, which were
already correct.

Verified the same way ADR 0006 did: camera aimed down each cardinal axis
in the browser (`-x` end-on, `-z` top-down, `-y` side-on) confirmed a
clean circle, rectangle, and triangle respectively before trusting the
geometry in the oblique establishing-shot view — and, after the winding
fix, a direct pixel-level comparison against `renders/scene.png` at the
same crop confirmed the taper's three-color gradient (amber top, blue
underside, rose near the round end) now matches.

`side: THREE.DoubleSide` (`web/src/scene/room.js`) is still used —
necessary for the room quads (see Consequences), and kept here too as a
safety net against any *remaining* visibility gaps from viewing angles
not yet tested — but it is not, and was never, a substitute for correct
winding: getting winding wrong doesn't just risk a culled/invisible face,
it risks this exact silent normal-corruption bug on a face that stays
fully visible.

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
- Winding still had to be got right per patch despite `DoubleSide` — see
  the inverted-winding bug above. Any future hand-authored patch added to
  this geometry should have its winding checked against its normal via
  the same cross-product method (or the `flatShading`-vs-smooth
  comparison trick) before trusting it, not assumed safe because
  `DoubleSide` is on.
