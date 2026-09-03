# 0025 — High-resolution icon render added; vector SVG rejected after testing

## Status

Accepted

## Context

Requested: a higher-resolution version of `icon.png`, and/or a vector
`icon.svg`.

Tested the SVG path rather than assuming: `pyvista.Plotter.save_graphic()`
supports `.svg` via VTK's GL2PS exporter, with a `raster` flag suggesting a
true-vector mode (`raster=False`) versus an embedded-raster mode
(`raster=True`). Rendered both and diffed the output — byte-identical
except for the embedded creation timestamp. Both are a base64-encoded PNG
screenshot wrapped in an SVG `<image>` tag, not real vector paths, in
either mode. This makes sense in hindsight: this scene's shadows are a
real shadow-mapped, screen-space/texture effect, deliberately chosen over
faked/painted shadows (ADR 0004) — there is no vector geometry
representing a shadow edge or a smooth-shaded gradient for GL2PS to emit,
so the exporter (or this headless software-GL setup's feedback-buffer
support for it) falls back to a raster capture regardless of the flag. An
`icon.svg` from this pipeline would be a PNG in a trench coat: no
scalability benefit, and a misleading file extension. Rejected.

Tested resolution ceiling directly rather than picking a round number:
2048/4096/8192 all rendered cleanly (8192 in ~3s, 1MB output); 16384 failed
with `vtkOpenGLFramebufferObject: FRAMEBUFFER_INCOMPLETE_ATTACHMENT` (a 0x0
depth renderbuffer) — a driver/software-rasterizer limit on this machine,
not something in this project's control. Also checked whether the shadow
map (a known lower-resolution-than-output-image known issue — see README)
would show visible staircasing at 8192 that isn't visible at 1024: cropped
a shadow edge to actual pixel level and found a clean anti-aliased
boundary, no staircase artifacts.

## Decision

- `render_icon.py` refactored to expose a `render_icon(size, output_path)`
  function and module-level `ICON_CAMERA_POSITION` /
  `ICON_CAMERA_FOCAL_POINT` / `ICON_CAMERA_VIEW_ANGLE` constants (ADR
  0022/0023/0024's tuned camera), guarded behind `if __name__ ==
  "__main__"` so importing it doesn't trigger a render as a side effect.
- New `render_icon_highres.py` imports `render_icon()` and calls it at
  `8192x8192`, writing `highres_icon.png`. Same camera, same composition
  (verified: identical margins as a fraction of frame size between the two
  outputs), no separate tuning needed or wanted.
- No `icon.svg` — see Context above for why that path was tested and
  rejected rather than skipped by assumption.

## Consequences

- `highres_icon.png` available for large-format/print use at ~8x the
  linear resolution of `icon.png`, same exact framing.
- `render_icon.py` and `render_icon_highres.py` share one source of truth
  for the icon camera — a future re-tune (e.g. after another room-size
  change) only needs to change `render_icon.py`'s constants once.
- 8192 is documented as a measured, not assumed, ceiling on this machine;
  a different machine/GL backend might allow more, but re-verify rather
  than assume before ever raising it.
- If vector output becomes a real requirement later (e.g. for a
  print-shop workflow needing infinite scalability), it would need a
  fundamentally different renderer for a simplified, flat-shaded version
  of this scene — not an export flag on the current shadow-mapped
  pipeline.
