# 0006 — Floating object built as a "wedge cylinder" for circle/rectangle/triangle shadows

## Status

Accepted

## Context

The scene's point (see `README.md` → Concept — "the truth one observes does
not falsify the truth of others") requires one solid object that casts
three *different*, all equally "true," shadow shapes: a rectangle on the
floor, a circle on one wall, a triangle on the other. A plain cylinder gives
a circle (viewed end-on) and two *identical* rectangles (viewed from above
or from the side) — it can't produce a triangle from any orthogonal
direction.

## Decision

Build the floating object as a cylinder with:

- one end left as a full, untouched circular cross-section (the end facing
  the camera), and
- the rest of its length sliced by two symmetric planar cuts — one
  descending from the top, one rising from the bottom — that converge
  exactly on the object's centerline at the opposite end, leaving nothing
  there but a thin diametral line.

This is provably sufficient for the three target projections:

- **End-on (→ circle)**: the untouched full-circle end is a superset of
  every other cross-section along the taper, so the silhouette from that
  direction is that circle, unaffected by the taper.
- **From above (→ floor rectangle)**: the two cuts only trim the `z`
  extent; at every point along the taper the cross-section still reaches
  its full `y = ±radius` at `z = 0`, so the footprint's width never
  narrows — the top-view outline stays a rectangle, unchanged from a plain
  cylinder's.
- **From the side (→ other wall, triangle)**: the cuts taper the `z`-extent
  linearly from full radius (at the circle end) to zero (at the far end) —
  a linear taper is exactly a triangle in profile.

Implementation (`make_wedge_cylinder()` in `render_scene.py`): build a plain
`pv.Cylinder`, `triangulate().clean()` it (required — the raw mesh is
non-manifold, which `clip_closed_surface()` refuses to operate on), then
apply the two cuts via two chained `clip_closed_surface()` calls (which cut
*and* cap, keeping the result a closed solid, unlike plain `clip()`). Plane
orientation for each cut was derived algebraically then confirmed
empirically (checking the mesh's per-slice bounds at both ends and the
midpoint).

A related shading bug surfaced once the cuts were in place: smooth shading
blended across the sharp crease between the curved surface and the new flat
cut faces, producing dark banding. Fixed by calling `compute_normals(...,
split_vertices=True, feature_angle=45)` so the crease gets distinct normals
on each side instead of one blended (and wrong) one.

## Consequences

- One object, three provably-correct "true" shadow shapes — the central
  point of the piece.
- The object's construction is specific to this circle/rectangle/triangle
  case; generalizing to other shape combinations would need a different (or
  parametrized) cut derivation.
- Depends on `clip_closed_surface()`'s manifold requirement — any future
  change to the base geometry needs the same `triangulate().clean()` step
  before clipping, and needs `split_vertices` normals if it introduces new
  sharp creases.
