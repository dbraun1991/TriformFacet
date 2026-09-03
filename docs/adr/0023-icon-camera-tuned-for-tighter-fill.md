# 0023 — Icon camera pulled in further for a tighter fill

## Status

Accepted

## Context

ADR 0022 gave `icon.png` its own camera at `k = 0.45` (a point 45% of the
way from the object toward `render_scene.py`'s far camera, along the same
line — see that ADR for the parametrization). Feedback: good direction,
but still too much black surface area relative to the colored shapes — push
the camera in further, maximizing fill, as long as (a) all three circles
stay fully inside the frame (no clipping) and (b) — implicitly, carried
over from ADR 0022 — no background bleed.

## Decision

Searched `k` down from `0.45` in steps, rendering at full icon resolution
(1024px, not a smaller proxy) and measuring two things directly per `k`:

- Full-frame scan for the exact page-background color → bleed count.
- The colored shapes' minimum pixel clearance from any frame edge →
  clipping risk.

Results: bleed stayed at exactly 0 pixels for every `k` down to `0.16`
(consistent with ADR 0022's finding that a closer camera fills the frame's
corners more easily, not less). Clearance shrinks smoothly as `k` drops and
hits exactly `0` — a shape touching the frame edge — at `k = 0.20`.

Chose `k = 0.22`: the tightest fill with a real, comfortable margin short
of that boundary — 36px clearance on the tightest side (~3.5% of the
1024px frame), safely clear of both clipping and of any anti-aliasing
softness right at the edge.

Concretely: `position = (14.132, 13.604, 9.468)`,
`focal_point = (4.012, 4.628, 3.748)`, `view_angle` unchanged at `32`.

## Consequences

- `icon.png`: substantially less black/dark surface area around the
  shapes than ADR 0022's `k = 0.45`, all three circles fully contained
  with a verified (not assumed) margin, zero background bleed.
- `render_icon.py`'s camera comment documents the search range and the
  exact `k` where clipping starts (`0.20`), so a future fill request can
  either nudge `k` closer to that boundary or re-run the same search after
  a room-size or object change, rather than guessing.
- `render_scene.py`/`render_scene_pixelperfect.py` remain untouched — this
  ADR, like 0022, is scoped to the icon's own camera only.
