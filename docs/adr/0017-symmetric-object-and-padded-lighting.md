# 0017 — Room scale-up, symmetric object placement, and padded lighting (all variants)

## Status

Accepted. Answers to the three open questions below, then implemented as
planned.

## Context

Six related changes were requested together, explicitly because they
interact rather than being independent tweaks:

0. Unlit corner edge lines (currently only in the default scene, ADR 0015)
   should also appear in `render_scene_pixelperfect.py`.
1. `ROOM` and `HEIGHT` each double (7→14, 6→12) — "four times the size" per
   surface is the area consequence of doubling *both* linear dimensions
   (a wall's area is `ROOM × HEIGHT`; doubling only one of them would only
   double its area, not quadruple it — doubling both is what the "square
   logic" arithmetic requires for the walls, and is also consistent with
   the floor, which only strictly needed `ROOM` doubled since it's already
   square).
2. The wedge cylinder's center moves from ADR 0012's `(3, 4, 3)` — chosen
   so the three *margins* happened to match — to a literally symmetric
   position: equal distance from all three near surfaces (`CYL_CENTER =
   (M, M, M)` for a single value `M`), not just equal margins arrived at
   through different coordinates. Framed as decoupling the object's
   placement from camera composition entirely: the object sits at a
   canonical, symmetric position: relative to the corner it floats above,
   and only the camera is tuned for how that reads on screen.
3. Equal light-circle sizes is then an automatic *consequence* of #2, not
   a separate step — with `Cx = Cy = Cz = M` and `M ≤ HEIGHT/2`, the
   binding (smallest) margin on every one of the three surfaces is `M`
   itself (checked algebraically below), so `fit_cone_half_angle` already
   gives all three lights the same angle without any further change.
4. Each light circle gets a visible gap (padding) from the white corner
   lines, instead of ADR 0009's original tangent-to-the-edge circle. This
   changes the radius formula from "= the margin" to "= the margin minus a
   padding constant."
5. `render_scene_pixelperfect.py` gets the same two treatments: the corner
   lines from #0, and a padding gap between its (now square, not circular)
   lit region and those lines — shrinking the gobo mask's aperture on the
   two edges that have a corner line, not all four.

## Dependency order

`0` is independent (additive, low-risk) and can happen any time. `1` must
happen before `2` (the valid range for `M` depends on the new `HEIGHT`).
`2` must happen before `3`/`4` (padding is subtracted from whatever margin
`2` establishes). `5` depends on both `0` (needs the line-drawing function)
and `4` (needs the padding value settled first, applied to a rectangular
aperture instead of a circular one).

## Why `M` must satisfy `M ≤ HEIGHT/2`

With `Cx = Cy = Cz = M`, `ROOM = 14`, `HEIGHT = 12`:

- Floor margins (x, y both use `ROOM`): `(M, 14−M)`.
- wall_back margins (x uses `ROOM`, z uses `HEIGHT`): `(M, 14−M, M, 12−M)`.
- wall_side margins (y uses `ROOM`, z uses `HEIGHT`): `(M, 14−M, M, 12−M)`.

`M` is the binding (smallest) margin for all three surfaces — and thus the
one true circle radius, satisfying #3 "for free" — only as long as `M` is
`≤` every one of `14−M` and `12−M` too, i.e. `M ≤ 7` and `M ≤ 6`. The
tighter bound is `M ≤ 6` (half of the shorter dimension, `HEIGHT`). Above
6, the z-margin (`12−M`) would become the binding one instead of `M`
itself, breaking the "equal distance to all three surfaces ⇒ equal circle
size" equivalence this plan relies on.

## Answers

1. **`M = 6`** — the recommended value, confirmed.
2. **Padding: `0.5` world units**, a fixed constant (`LIGHT_PADDING` in
   `render_scene.py`) — the "fixed number" type was chosen but no exact
   figure was given, so `0.5` (a visible but modest ~8% gap relative to
   `M`) was picked as a reasonable default, applied, and rendered for
   review rather than blocking on a further round-trip.
3. **Wedge cylinder stays its current absolute size — deliberately not
   scaled with the room.** The stated reasoning: since the room's own
   silhouette now reaches much closer to a square crop's frame corners
   while the light circles (sized off `CYL_CENTER`/`M`, unrelated to the
   object's own physical dimensions) stay proportionally the same size as
   before, an unscaled — and therefore relatively smaller — object leaves
   more dark room/corner-line area available to close ADR 0014's leftover
   white-void gap in `icon.png`. Confirmed effective after implementing:
   `icon.png` now shows zero background bleed in any corner, at the same
   `view_angle = 32` that previously left small pale slivers.

## Consequences

- Every surface's light circle (or, in the pixel-perfect variant, square)
  is provably the same size, by construction (equal `CYL_CENTER`
  coordinates) rather than by coincidence of differently-chosen
  coordinates landing on the same margin.
- The object's position is now a fixed, symmetric constant independent of
  camera concerns — future camera retuning no longer risks disturbing the
  "equal treatment of all three surfaces" property, since that now holds
  regardless of viewing angle.
- `render_scene_pixelperfect.py` and `render_scene.py`/`render_icon.py`
  converge further in structure (both padded from the same corner lines,
  both share `add_edge_highlight_lines`), even though their lit-area
  *shapes* (circle vs. square) remain the deliberate difference between
  them.
- The camera needed retuning in both `render_scene.py` and
  `render_icon.py` after the room/object geometry changed size — done by
  scaling the previous camera `position`/`focal_point` coordinates by the
  same ×2 factor as `ROOM`/`HEIGHT`, which reproduced closely equivalent
  framing on the first try (no further iteration needed) for both the
  illustration and — as noted above — fixed the icon's background-bleed
  issue as a side effect.
- **Side effect confirmed by inspection, not just intended**: the padding
  gap and equal circle sizes are both clearly visible in the rendered
  output (checked via close crops of the corner seams in both `scene.png`
  and `scene_pixelperfect.png`), and the pixel-perfect variant's color
  separation (ADR 0016) survived the geometry change unchanged — no new
  overlap introduced.
