# 0009 — Cone angles fitted to room geometry, not hand-picked

## Status

Accepted

## Context

All three lights used a flat `cone_angle=30` (ADR 0005). At the light
distance in use (`FAR = 5 * ROOM`), a 30° half-angle produces a footprint
radius of `FAR * tan(30°)` — several times the room's own size — so every
light's beam massively overshot its intended surface and spilled onto both
neighboring surfaces. This was directly visible as color bleed (e.g. the
amber floor light tinting the bottom of both walls) and was also the root
cause of the "faint secondary shadows" noted in `README.md`'s Known Issues:
a wall's own shadow-casting light wasn't the only one reaching it, so a
second, fainter shadow from a neighboring light's spill showed up too.

Explicit ask: fit each light's angle to its surface, and if a perfect fit
isn't possible, prefer a dark, unlit corner over any color overlap onto a
neighboring surface.

## Decision

Add `fit_cone_half_angle(distance, center_a, extent_a, center_b, extent_b)`,
which computes the half-angle so the light's circular footprint is
*inscribed* in its rectangular target surface — tangent to the **nearest**
edge (`min` over all four edge margins), not sized to reach the farthest
corner. A circular footprint can't exactly fill a rectangle, so this is a
deliberate choice between two imperfect options:

- inscribed (tangent to nearest edge): guaranteed to never cross the
  surface's own boundary → chosen, since a corner going dark is the
  explicitly preferred failure mode;
- circumscribed (reaching the farthest corner): guarantees full coverage of
  the rectangle but necessarily spills past the nearer edges onto whatever
  is beyond them → rejected, this is exactly the color-overlap being fixed.

Each of the three lights now gets its `cone_angle` from this function
instead of a literal `30`, using `ROOM`/`HEIGHT`/`CYL_CENTER` directly so
the fit stays correct if those change.

## Consequences

- Each light's colored footprint now lands cleanly within its own surface;
  no more color bleeding across the corner edge onto a neighboring wall.
- Reduced, but — as it turned out — did not fully eliminate, the
  "faint secondary shadows" issue: cross-illumination between the three
  *explicit* lights stopped, but a second, differently-caused secondary
  shadow was still visible afterward. The actual full cause was unrelated
  to cone angle at all — see ADR 0010.
- Trade-off, as accepted above: each surface now has a visibly dark region
  in its farther corner(s), outside the inscribed circle. This is the
  intended look, not a bug.
- The room's overall visual character changed materially — from "evenly lit
  room with tinted color washes" to "distinct colored spotlight pools with
  dark corners." This was a direct, expected consequence of the fitting
  requirement, not a side effect to be tuned away.
