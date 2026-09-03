"""High-resolution render of the blueprint-style icon — same composition
and camera as `render_icon_blueprint.py`, just 8192x8192. See
`render_icon_highres.py` for why 8192 is this machine's measured
resolution ceiling.
"""

from render_icon import render_icon_from_builder
from render_scene import RENDERS_DIR
from render_scene_blueprint import build_scene_blueprint

HIGHRES_SIZE = 8192

RENDERS_DIR.mkdir(parents=True, exist_ok=True)
render_icon_from_builder(
    HIGHRES_SIZE, RENDERS_DIR / "highres_blueprint_icon.png", build_scene_blueprint,
)
