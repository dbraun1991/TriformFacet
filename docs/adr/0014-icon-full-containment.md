# 0014 — Icon camera re-tuned for full circle containment, not edge-to-edge fill

## Status

Accepted

## Context

ADR 0011 tuned `render_icon.py`'s camera to fill the square frame
edge-to-edge with no page-background bleed, at the cost of letting the two
wall circles bleed *off* the frame edges (a "full-bleed badge" look).
Feedback on that result: prefer every circle fully inside the frame, even
at the cost of some background showing, and — separately — ADR 0012
equalized all three shadow-circle sizes, which changes what "fully contain"
even requires here.

## Decision

With all three circles now the same size and (per ADR 0012) each reaching
close to the room's own physical boundary in most directions, containing
the circles turned out to mean almost the same thing as containing the
whole room. Re-tuning `view_angle` down from ADR 0011's tight framing
converged back toward the *full illustration's own* `view_angle = 32` —
tested `22` (the ADR 0011 value: clips a wall circle), `30` (contains all
three, but the blue circle sits flush against the frame edge with no
margin), and `32` (contains all three with visible clearance on every
side). Kept `32`.

## Consequences

- `icon.png` now shows every colored circle fully, with margin — the
  stated priority.
- Not fully solved: a small triangle of the page's own pale background
  still shows through in one or two frame corners at `view_angle = 32`,
  since the room's own outer silhouette doesn't quite reach the square
  frame's corners either (a milder version of ADR 0011's original
  background-bleed problem). Explicitly flagged during the same
  discussion as possibly needing "wall & floor size adjustment" — not
  attempted in this pass, since `ROOM`/`HEIGHT` are shared constants
  (`build_room_and_object`) used by every render variant, and enlarging
  them to solve the icon's framing would also reshape `scene.png`,
  `scene_whiteline.png`, and `scene_pixelperfect.png`, none of which have
  this problem. A follow-up could pass `ROOM`/`HEIGHT` overrides into
  `build_room_and_object` so the icon variant alone gets a bigger room
  (more unlit floor/wall beyond the existing, unchanged circles) without
  affecting the others — not implemented here.
