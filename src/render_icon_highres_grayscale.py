"""High-resolution render of the grayscale icon variant — same composition,
camera, and 8192px ceiling rationale as `render_icon_highres.py`, just with
`render_icon_grayscale.py`'s light (desaturated) light colors instead of
`render_icon_highres.py`'s amber/blue/rose. See that file for why 8192 is
the resolution ceiling on this machine, and `render_icon_grayscale.py` for
the light-color choices.
"""

from render_icon_grayscale import render_grayscale_icon
from render_scene import RENDERS_DIR

HIGHRES_SIZE = 8192

RENDERS_DIR.mkdir(parents=True, exist_ok=True)
render_grayscale_icon(HIGHRES_SIZE, RENDERS_DIR / "highres_grayscale_icon.png")
