# 0011 — Separate square icon render, sharing scene setup via `build_scene()`

## Status

Accepted

## Context

The long-standing "icon for a webpage" goal (tracked in `AGENTS.md` since
before the scene had settled) needed the room/object/lighting scene itself
to stabilize first — `AGENTS.md` explicitly noted this. With the lighting,
color, and shadow issues resolved (ADRs 0008–0010), the scene reads as a
strong, self-contained composition (three colored circles + a pale object),
making this the right point to act on it.

The icon needs a different camera than the full illustration: the full
scene's 45°-into-the-corner framing (`render_scene.py`) leaves a lot of
empty dark corner, which reads fine at illustration size but becomes mostly
wasted space once shrunk to icon/favicon sizes.

## Decision

- Refactor `render_scene.py`: extract room + object + lights construction
  into `build_scene(plotter)`, called by both the original script (now
  gated under `if __name__ == "__main__":`) and a new `render_icon.py`.
  Verified the refactor is a no-op for the existing output (pixel-diffed
  old vs. new `scene.png` — zero differing pixels).
- Add `render_icon.py`: builds the same scene via `build_scene()`, then
  renders it through a square (1024×1024) window with a closer/narrower
  camera than the full illustration's.
- The camera's `view_angle` was tuned empirically (not derived), between
  two failure modes found while iterating:
  - too narrow (~20°): the two wall-mounted circles get cropped at the
    frame edges — reads as an accidental crop.
  - too wide (~27–31°): the room's finite floor/wall quads no longer reach
    the frame's corners, so the artifact's own page background shows
    through as jagged, asymmetric slivers.
  `view_angle = 22` (vs. the full scene's `32`) was the point where the
  room's silhouette fills the square frame edge-to-edge with no background
  showing, while both wall circles stay fully inside the frame (the floor
  circle and object are already near-center and unaffected either way).

## Consequences

- `icon.png` (1024×1024) reads clearly from roughly 128px up: the three
  colored surfaces plus the pale object are immediately legible as one
  composition.
- **Known limitation, not addressed here**: at true favicon sizes (32px,
  16px) the composition collapses into indistinct colored blobs — checked
  directly by downscaling `icon.png` and viewing it at each size. This is
  an inherent consequence of the scene's level of detail (fine shadow
  shapes, thin gradients, a small pale object against three color fields),
  not a framing problem this ADR's camera tuning can fix. A true 16px mark
  would need a separately-designed, much-simplified graphic (e.g., flat
  color blocks with no gradient/shadow detail) rather than a downscale of
  this render — left as a follow-up, not attempted here.
- `render_scene.py`'s `build_scene()` is now the single source of truth for
  room/object/light setup; any future scene-level change (geometry, color,
  lighting) should go there so both the illustration and the icon render
  stay in sync automatically, rather than needing to be duplicated by hand.
