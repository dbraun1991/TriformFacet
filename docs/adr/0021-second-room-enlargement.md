# 0021 — Second room enlargement (2x), same fixed-object/scaled-camera treatment as ADR 0017/0018/0020

## Status

Accepted

## Context

Requested: enlarge the room surfaces (floor/walls) again, by the same 2x
factor as ADR 0017's doubling, with nothing else deliberately changed.
This raised the same question ADR 0020 already answered once: does the
camera need to move, or does everything just get bigger under a fixed
camera?

Answer confirmed again here: yes, the camera has to scale too. It's kept
at a fixed *fraction* of `ROOM`/`HEIGHT`, not a fixed absolute position
(ADR 0020), specifically so it keeps framing the room correctly as the
room's own size changes. Leaving the camera's literal coordinates alone
while doubling `ROOM`/`HEIGHT` again would reproduce exactly the cropping
ADR 0020 tested and rejected — the camera would be relatively too close to
the now-larger room.

## Decision

- `ROOM`: `14.0` → `28.0`. `HEIGHT`: `12.0` → `24.0`. (Second doubling;
  each surface's area is now 16x its pre-ADR-0017 original.)
- Camera `position`/`focal_point` in all three scripts scaled by the same
  2x factor, per ADR 0020's rule (unchanged as a *fraction* of
  `ROOM`/`HEIGHT`): `position (26.8, 25.6, 16.2) → (53.6, 51.2, 32.4)`,
  `focal_point (3.8, 5.2, 3.2) → (7.6, 10.4, 6.4)`. `view_angle` (32)
  unchanged.
- Everything else left untouched on purpose: `CYL_CENTER`, `CYL_RADIUS`,
  `CYL_LENGTH`, `LIGHT_PADDING` are all fixed literals already (ADR
  0018), not derived from `ROOM`/`HEIGHT`, so they needed no edit.

Verified rather than assumed that the light circles (`render_scene.py`'s
`fit_cone_half_angle`) stay the same absolute size under this change:
`margin = min(center_a, extent_a - center_a, center_b, extent_b - center_b)
- padding` is bound by `center_a`/`center_b` (`CYL_CENTER`'s fixed
coordinates, e.g. `3`), not by `extent_a`/`extent_b` (`ROOM`/`HEIGHT`), as
long as the room stays at least roughly twice `CYL_CENTER`'s coordinate on
each axis — comfortably true here. So `margin`, and therefore each
footprint's world-space radius, is unchanged even though `ROOM`/`HEIGHT`
(and therefore the light's pull-back distance `FAR = 5 * ROOM`) both grew.
Confirmed visually in the re-rendered `icon.png`/`scene.png` too — same
absolute circle sizes, more dark room area around them.

`render_scene_pixelperfect.py`'s squares are the one thing that *does*
grow with the surfaces — by design, not as a side effect: that variant's
whole point is full-rectangle coverage, so its lit region is defined as
"the surface minus padding," not a fixed size. Growing with the surface is
consistent with that design, not a violation of "nothing else changed."

## Consequences

- `scene.png`/`icon.png`: more dark room/corner-line area around the
  same-sized object and light circles, same camera framing, zero
  background bleed still holds in `icon.png` (re-verified, not just
  assumed).
- `scene_pixelperfect.png`: bigger colored squares (tracking the bigger
  surfaces), same clean color separation, same still-unresolved padding
  asymmetry (ADR 0019 — unrelated to and unaffected by this change).
- Confirms the general rule from ADR 0020 for any future room resize:
  scale `ROOM`/`HEIGHT` and the camera together (same factor); leave
  `CYL_CENTER`/`CYL_RADIUS`/`CYL_LENGTH`/`LIGHT_PADDING` fixed unless a
  future request specifically asks to change the object/lighting itself.
