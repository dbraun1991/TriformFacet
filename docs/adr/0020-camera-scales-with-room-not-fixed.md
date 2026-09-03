# 0020 — Camera position/focal_point deliberately scale with the room, unlike the object

## Status

Accepted

## Context

After ADR 0018 fixed `M` (the object's distance from each surface) to stop
scaling with `ROOM`/`HEIGHT`, a fair question followed: did the *camera*
get the same treatment it should have, or was its position also altered
as an unprincipled side effect of the room-doubling work in ADR 0017 (the
same category of mistake `M` was)?

Tested directly: reverted `render_scene.py`/`render_icon.py`'s camera
`position`/`focal_point` to their exact pre-ADR-0017 absolute values,
re-rendered `icon.png` at the same `view_angle = 32`. Result: the light
circles are cropped at the frame edges again — the same problem ADR
0011/0014 already solved once, reopened.

## Decision

Keep the camera at its current values (`position=(26.8, 25.6, 16.2)`,
`focal_point=(3.8, 5.2, 3.2)`) — which are exactly the pre-doubling values
scaled by the same 2x factor `ROOM`/`HEIGHT` were doubled by. Checked
explicitly: expressed as a *fraction* of `ROOM`/`HEIGHT`, every component
of both `position` and `focal_point` is unchanged from before ADR 0017
(e.g. `26.8 / 14 == 13.4 / 7`, and likewise for every other component).

This is judged a different kind of quantity than `M`, not a repeat of the
same bug: `M` was supposed to be a fixed, room-size-independent distance
(the object's own placement, deliberately decoupled from the room in ADR
0017/0018's whole point). The camera's job is to frame the *room itself*,
so keeping its position at a fixed *proportion* of the room's size — not a
fixed absolute position — is what keeps showing a consistent view as the
room grows underneath it. A fixed absolute camera position, by contrast,
would effectively zoom the view in every time the room grows, since the
camera would be relatively closer to a room that's now bigger — which is
exactly the cropping observed when this was tested.

## Consequences

- Confirms the current camera values, rather than changing anything —
  the "regression" suspected here doesn't exist on inspection, so nothing
  in `render_scene.py`/`render_icon.py`/`render_scene_pixelperfect.py`
  changed as a result, beyond adding comments cross-referencing this
  reasoning at each `camera.position`/`camera.focal_point` assignment so
  it isn't re-litigated from scratch.
- General principle for future room-size changes: re-derive the camera as
  the same fraction of the new `ROOM`/`HEIGHT` (i.e. scale it right along
  with those constants), while object-placement constants like `CYL_CENTER`
  and `CYL_RADIUS`/`CYL_LENGTH` should generally *not* be re-derived from
  `ROOM`/`HEIGHT` at all (ADR 0018) — these are opposite defaults, and it's
  worth pausing on which one applies to any new constant before changing
  either.
