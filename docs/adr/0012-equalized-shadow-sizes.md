# 0012 — Wedge cylinder repositioned to equalize all three shadow-circle sizes

## Status

Accepted

## Context

With `CYL_CENTER = (3.0, 4.0, 2.0)` and `HEIGHT = 5.0`, the floor's
inscribed shadow-circle margin (`fit_cone_half_angle`'s binding value) was
3, while both walls' margins were 2 — the floor circle was visibly bigger
than the two wall circles. This was a direct consequence of `HEIGHT` (5)
being smaller than `ROOM` (7): the z-axis had less room to place the object
away from both the floor and the ceiling-height boundary than x/y had.

Asked directly, the preference was to equalize the three circles as a pure
composition/balance fix (object size unchanged), over the alternative of
scaling the object bigger for icon legibility.

## Decision

- Raise `HEIGHT` from 5 to 6, giving the z-axis enough room to match x/y.
- Move `CYL_CENTER` to `(3.0, 4.0, 3.0)` — same x/y as before, z raised
  from 2 to 3 (`HEIGHT / 2`, maximizing the achievable z-margin).

With these values: x-margin `min(3, 7-3) = 3`, y-margin `min(4, 7-4) = 3`,
z-margin `min(3, 6-3) = 3` — all three of `fit_cone_half_angle`'s binding
margins are now exactly 3, so all three lights' inscribed circles are the
same radius.

## Consequences

- The three colored shadow circles now read as visually equal in the
  render — confirmed in `scene.png`.
- Side effect, not a bug: at radius 3, the floor and both wall circles now
  sit tangent to *two* of their surface's edges simultaneously (not just
  one), since the x, y, and z margins all bind at exactly the same value.
  In the render this shows as each circle appearing to nestle snugly into
  a corner of its own rectangle rather than floating with clearance on
  every side — an inherent consequence of margins matching exactly, not a
  new artifact.
- This is a shared, scene-level change (`ROOM`/`HEIGHT`/`CYL_CENTER` are
  used by every render variant via `build_room_and_object`), so it also
  reshapes `icon.png`'s composition — see ADR 0014.
