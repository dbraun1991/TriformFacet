# 0022 — `icon.png` gets its own, closer camera, decoupled from `render_scene.py`

## Status

Accepted

## Context

After ADR 0021's second room doubling, feedback: the three colored shadow
circles read as "quite small" in both `scene.png` and `icon.png` — measured
at ~22% the pixel area of the pre-ADR-0017 original (confirmed directly via
`PIL`, not just eyeballed: 245×233px bounding box → 114×110px). That
smallness is an accepted, intentional consequence of the anti-white-void
design (bigger room, fixed-size object — ADR 0017/0018/0021): confirmed
with the user this is a known, accepted tradeoff, not a bug to undo.

The follow-up request: reposition the *icon's* camera specifically ("shoot
the icon from a different place"), since `render_icon.py` had always reused
`render_scene.py`'s camera verbatim — a wide shot tuned to frame the whole
room, scaling with `ROOM`/`HEIGHT` (ADR 0020/0021), which is the right
choice for `scene.png`'s establishing shot but not obviously right for a
square icon crop.

While investigating, checked something ADR 0017/0018 had only eyeballed on
a thumbnail: "zero background bleed" in `icon.png`'s corners. Measured
directly (scan the full rendered image for the exact page-background color,
not just glance at the corners) and found this claim was **wrong** — a
tiny, sub-visible sliver of background color was present in every corner of
`icon.png` at every room size tried, including both before and after ADR
0021's second doubling. Not something ADR 0021 introduced; it had been
there all along, just too small to notice by eye at thumbnail size.

## Decision

Give `render_icon.py` its own camera, independent of `render_scene.py`,
rather than reusing that file's wide-shot camera:

- Same viewing direction/angle as `render_scene.py`'s camera, just a closer
  stop along that same line from the object: parametrize by
  `k`, where
  `position = CYL_CENTER + k * (render_scene_position - CYL_CENTER)` and
  likewise for `focal_point`. `k = 1` reproduces `render_scene.py`'s
  camera exactly; smaller `k` moves the icon's camera closer to the object.
- Picked `k = 0.45` empirically — rendered and pixel-measured a range of
  `k` values (1.0 down to 0.25), checking two things directly rather than
  by eye: (a) full-image scan for the exact background color (any count
  above 0 = a real bleed), and (b) the colored shapes' bounding-box
  clearance from the frame edge (want comfortably >0, matching ADR 0014's
  "visible clearance, not flush" bar, not just "not clipped").
  - `k = 1.0` (the old shared camera): background bleed present (confirmed
    non-zero pixel count), circles smallest.
  - `k <= 0.6`: zero background pixels anywhere in the frame — the closer
    camera fills the square crop's corners more easily than the far one
    does, so shrinking `k` *fixes* the bleed rather than risking it.
  - `k = 0.45`: circles back to ~104% of their very first (pre-ADR-0017)
    on-screen size, ~24% frame-width clearance from the edge (healthy
    margin), zero background pixels. Chosen as the sweet spot: object size
    restored to what it was before either room doubling, corner bleed
    actually eliminated (not just claimed), well clear of clipping.
- Concretely: `position = (25.77, 24.69, 16.23)`,
  `focal_point = (5.07, 6.33, 4.53)`, `view_angle` unchanged at `32`.
- `render_scene.py` (`scene.png`) and `render_scene_pixelperfect.py`
  (`scene_pixelperfect.png`) are **unchanged** — both are 16:9 establishing
  shots that intentionally show background above the room (not a bleed,
  by design), and the "small circles" feedback for those two files is
  still open (see AGENTS.md — not addressed by this ADR, which is scoped
  to the icon specifically per the request).

## Consequences

- `icon.png`: circles back to a size that reads clearly at typical icon
  display sizes, background bleed eliminated (verified pixel-exact, not
  eyeballed this time), still zero clipping.
- `render_icon.py` and `render_scene.py` now have genuinely independent
  cameras — a future change to one's camera (further tuning, a new room
  size, etc.) does not automatically apply to the other. `render_icon.py`'s
  camera comment documents the `k`-interpolation derivation so a future
  room-size change can be re-run through the same empirical search rather
  than guessed.
- Corrects the record: ADR 0017/0018's "zero background bleed, confirmed
  by inspection" claim was an overclaim (true only to the eye at thumbnail
  size, not pixel-exact) — worth remembering next time a similar claim is
  made about this scene: verify with a pixel scan, not a glance.
- Still open: `scene.png`/`scene_pixelperfect.png`'s own "circles feel
  small" feedback — not addressed here, since those are wide establishing
  shots where reusing the icon's tight framing would defeat their purpose
  (showing the room, not just the object). Worth a future pass if wanted.
