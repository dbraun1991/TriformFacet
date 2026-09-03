"""High-resolution render of the hand-drawn-style icon — same composition
and camera as `render_icon_handdrawn.py`, just 8192x8192. See
`render_icon_highres.py` for why 8192 is this machine's measured
resolution ceiling.
"""

from render_icon import render_icon_from_builder
from render_scene import RENDERS_DIR
from render_scene_handdrawn import build_scene_handdrawn

HIGHRES_SIZE = 8192

RENDERS_DIR.mkdir(parents=True, exist_ok=True)
render_icon_from_builder(
    HIGHRES_SIZE, RENDERS_DIR / "highres_handdrawn_icon.png", build_scene_handdrawn,
)
