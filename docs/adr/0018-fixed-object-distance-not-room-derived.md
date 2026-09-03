# 0018 — Object distance M is a fixed constant, not derived from the (now bigger) room

## Status

Accepted

## Context

ADR 0017 set `_M = HEIGHT / 2`. This was a mistake: it re-derives `M` from
`HEIGHT` every time `HEIGHT` changes, so when `HEIGHT` doubled (ADR 0017's
own room-scale-up), `M` doubled right along with it (3 → 6) — and since the
light-circle radius is `M − LIGHT_PADDING`, the circles doubled in size
too. Feedback after seeing the result: this defeated the actual point of
doubling the room — the object and its light circles were supposed to stay
the same *absolute* size while the room grew *around* them, both because
"other elements should not grow" was the explicit ask, and because that's
specifically what leaves more relatively-dark room/corner-line space for
`icon.png`'s square crop to reach its corners without background bleed
(ADR 0014/0017's white-void fix). Recomputing `M` from the new `HEIGHT`
undid that on the very same commit that was supposed to deliver it.

## Decision

`_M = 3.0` — a fixed literal, matching the object's distance from before
`ROOM`/`HEIGHT` doubled, with a comment explaining explicitly *why* it must
not be derived from `HEIGHT` (or `ROOM`) again. Still valid as the binding
margin on every surface at the new `ROOM=14`/`HEIGHT=12` (`M ≤ ROOM−M` and
`M ≤ HEIGHT−M`, comfortably true at `M=3`), so ADR 0017's "equal distance ⇒
equal circle size" guarantee is unaffected — only the *value* of `M`
changed, not the structural property.

## Consequences

- Re-rendered `scene.png`: the object and its three light circles are
  visibly the same absolute size as before the room doubled, now floating
  in noticeably more dark negative space — matches the corrected intent.
- Re-rendered `icon.png`: still zero background bleed in any corner, same
  as ADR 0017 achieved — confirms the white-void fix didn't depend on `M`
  scaling with the room, only on `ROOM`/`HEIGHT` growing while the object
  stayed fixed.
- General lesson for this file: any constant derived from `ROOM`/`HEIGHT`
  needs a moment's thought about whether it's *supposed* to track the
  room's size or deliberately not — this one wasn't, and the derivation
  looked reasonable enough to not get questioned at the time it was
  written.
