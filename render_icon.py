"""Render a square icon crop of the room scene, with all three colored
shadow circles fully contained in the frame (not cropped at the edges) and
zero page-background bleed in any corner.

Reuses the exact same room/object/lighting setup as `render_scene.py` (via
`build_scene()`), just with a square window and its own camera (see below —
deliberately NOT the same camera as `render_scene.py`'s wide establishing
shot, as of ADR 0022/0023). `view_angle = 32` is unchanged from
`render_scene.py` — narrower values would clip a circle instead of just
tightening the crop (see ADR 0014); the fill is tuned via camera distance
instead (ADR 0023).

ADR 0014 originally left a small background-bleed gap open in one or two
corners. ADR 0017/0018 claimed this was closed by the first room doubling,
but that was an eyeballed call on a small thumbnail, not a pixel check —
ADR 0022 measured it directly and found `render_scene.py`'s far,
room-proportional camera (correct for `scene.png`'s wide shot) still left
an exact-background-color sliver in every corner of a *square* crop, at
every room size tried, including this file's previous shared-camera setup.
Fixed by giving the icon its own, much closer camera instead of reusing
`render_scene.py`'s — see the camera comment below.
"""

import pyvista as pv

from render_scene import build_scene

ICON_SIZE = 1024

# Icon-specific camera (ADR 0022) — deliberately NOT render_scene.py's
# camera. That camera is tuned to frame the whole room as a wide
# establishing shot (scaling with ROOM/HEIGHT per ADR 0020/0021), which
# left the object/circles very small after two room doublings (ADR 0021)
# and — measured directly, not eyeballed — a real if tiny background sliver
# in every corner of a square crop.
#
# Both problems share one fix: move the icon's camera much closer to the
# object. `ROOM`/`HEIGHT` are now large enough (ADR 0021) that a closer
# camera still comfortably fills every corner of the square frame with room
# silhouette — confirmed by scanning the full rendered image for the
# background color and finding zero matching pixels, not just checking the
# four corner points.
#
# Derived as: a point some fraction k of the way from the object
# (CYL_CENTER = (3,3,3)) toward render_scene.py's camera position/
# focal_point (the dolly/zoom axis, same viewing angle throughout), THEN a
# rigid pan — the same delta added to both position and focal_point along
# the view's local right/up axes — to center the shape cluster in frame.
# Both were found empirically (render + measure at 1024px, never
# eyeballed):
#   - Pan first: centering left=right and top=bottom turned out to matter
#     more than raw fill — the previous (ADR 0023) camera had a real
#     off-center bias (36px/167px left/right, 187px/85px top/bottom), not
#     just an aspect-ratio artifact. Solved by a 2D Newton iteration on
#     the pan offset against (left-right, top-bottom).
#   - k re-searched after re-centering at each candidate (centering shifts
#     the fill slightly via parallax, since the shape cluster isn't flat):
#     bleed stayed at 0 down to k=0.18, hit real clipping (0px clearance)
#     at k=0.17. k = 0.19 is the tightest centered fit with a safety
#     margin comparable to ADR 0023's (~39px / ~3.8% of the 1024px frame
#     on the tighter axis).
#   - Exactly equal padding on all four sides is NOT achievable this way:
#     the shape cluster's own bounding box isn't square (~1.09:1,
#     wider than tall), and a camera zoom scales both axes by the same
#     factor, so no (pan, zoom) combination makes left/right padding equal
#     to top/bottom padding — only left=right and top=bottom
#     independently, which is what's optimized here. Residual at k=0.19:
#     ~39px left/right vs. ~82px top/bottom. See ADR 0024.
#
# Exposed as module-level constants (not just inlined below) so
# render_icon_highres.py can reuse the exact same camera via
# `render_icon()` instead of duplicating these numbers — see ADR 0025.
ICON_CAMERA_POSITION = (13.1272, 11.8836, 8.1087)
ICON_CAMERA_FOCAL_POINT = (4.3872, 4.1316, 3.1687)
ICON_CAMERA_VIEW_ANGLE = 32


def render_icon(size, output_path):
    """Render the icon composition at `size`x`size` px to `output_path`,
    using the camera above. Shared by this file's own default (1024,
    `icon.png`) and `render_icon_highres.py` (8192, `highres_icon.png`) so
    the two outputs can't drift apart into two different compositions.
    """
    plotter = pv.Plotter(off_screen=True, window_size=(size, size), lighting="none")
    build_scene(plotter)
    plotter.camera.position = ICON_CAMERA_POSITION
    plotter.camera.focal_point = ICON_CAMERA_FOCAL_POINT
    plotter.camera.up = (0, 0, 1)
    plotter.camera.view_angle = ICON_CAMERA_VIEW_ANGLE
    plotter.screenshot(output_path)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    render_icon(ICON_SIZE, "icon.png")
