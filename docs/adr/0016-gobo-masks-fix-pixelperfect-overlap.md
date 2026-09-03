# 0016 — Gobo aperture masks replace blocker fins, fixing pixel-perfect's color overlap

## Status

Accepted

## Context

ADR 0013 flagged `render_scene_pixelperfect.py`'s diagonal blocker fins as
visibly imperfect (self-shadowing, visible panels) but didn't establish
whether they actually stopped the cross-surface color bleed they were
built for. Direct inspection (cropping and re-examining the rendered walls)
showed they did not: a large lighter-colored ellipse plus a muddy off-hue
crescent were both clearly visible on the wall_back (blue) surface,
produced by the wall_side (rose) light's widened cone — explicitly called
out as "not allowed by default."

Geometric analysis of why the fins fell short: a circumscribed light's cone
overshoots its own target rectangle by a lot — for the wall_side light
here, roughly half the cone's angular budget lands outside its own
rectangle's valid range entirely. Those "wasted" rays don't just graze the
neighboring surface's edge; they cross into it well before reaching the
shared corner, over a large continuous area — far more than a small
corner-fin was ever sized to block.

## Decision

Replace the fins with a "gobo" aperture: an opaque frame (built as 4 quads
— a picture-frame border, not a boolean-cut mesh) with a rectangular hole,
placed between each light and the room, sized so the hole reproduces
exactly that light's target rectangle by the time the beam reaches the
room. This blocks 100% of anything outside the intended rectangle by
construction, for any cone width, rather than relying on a blocker's shape
approximating the overshoot region.

Placement was the open question from ADR 0013 (a mask near the target was
set aside there over camera-visibility risk). Resolved by placing each
mask near the *light* instead (`MASK_FRACTION = 0.5`, halfway along the
light-to-target distance) and checking the angle between the camera's view
direction and the vector to each mask position: all three came out above
55°, well outside the camera's ~16° half-angle field of view, so none of
the three masks appear in the render — confirmed by inspecting the output,
not just the angle math.

## Consequences

- Re-examining the walls (cropped both shared-edge seams) after the fix
  shows clean color separation — no mixed-color patches, no off-hue
  crescents, on either wall or the floor.
- One rendering hazard found and fixed along the way: `add_mesh(...,
  lighting=False)` on the mask meshes, combined with `enable_shadows()`,
  produced a shader-compile error (`Could not set shader program`) — VTK's
  shadow-map shader variant apparently has no unlit code path. Harmless in
  the actual image (these meshes are outside the camera frustum either
  way), but fixed by leaving the masks' default lighting on rather than
  relying on a broken shader.
- `render_scene_pixelperfect.py` now achieves the "no color overlap" half
  of ADR 0013's original ask cleanly. It still isn't adopted as the
  default scene — its look (every surface fully lit, no dark corners at
  all) is a different aesthetic choice from ADR 0015's promoted
  white-line/dark-corner version, not a strictly-better version of it.
