"""High-resolution render of the exact same icon composition as
render_icon.py — same camera (`ICON_CAMERA_*`, ADR 0022/0023/0024), same
`build_scene()`, just a bigger canvas: 8192x8192 instead of 1024x1024.
Reuses `render_icon()` rather than duplicating the camera setup, so this
file and `render_icon.py` can never render two different compositions by
accident.

8192 is a measured ceiling, not a round-number guess: on this machine's
headless/software OpenGL backend, the render silently breaks at 16384
(`vtkOpenGLFramebufferObject`: `FRAMEBUFFER_INCOMPLETE_ATTACHMENT`, a 0x0
depth renderbuffer) — a driver/software-rasterizer limit, not something
this project's code controls. 8192 renders cleanly in ~3s; a pixel-level
crop of a shadow edge at that resolution shows a clean anti-aliased
boundary, not the staircase artifacts a shadow-map resolution limit would
produce. See ADR 0025.

A true vector `icon.svg` was tried and rejected, not just assumed
unworkable: `pyvista`'s `save_graphic()` (`raster=True` and `raster=False`
alike) produced byte-identical output — a PNG screenshot wrapped in SVG
`<image>` tags, not real vector paths. This scene's shadows are a real
shadow-mapped, screen-space/texture effect (ADR 0004's whole point, not a
flat painted shape), so there's no vector geometry for the shadow
edges/gradients to export in the first place — a bigger raster is the only
way to get a higher-fidelity version of this particular render.
"""

from render_icon import render_icon

HIGHRES_SIZE = 8192

render_icon(HIGHRES_SIZE, "highres_icon.png")
