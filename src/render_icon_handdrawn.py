"""Hand-drawn-style icon crop — the exact composition from
`render_scene_handdrawn.py`'s `build_scene_handdrawn()` (ADR 0031), through
`render_icon.py`'s tuned square icon camera (ADR 0022/0023/0024) instead of
`render_scene.py`'s wide establishing-shot camera. Same room/object
geometry as the default icon (the hand-drawn variant only changes
palette/lighting/linework, not geometry), so the same
zero-background-bleed, full-circle-containment guarantees hold without
re-deriving the camera.
"""

from render_icon import ICON_SIZE, render_icon_from_builder
from render_scene import RENDERS_DIR
from render_scene_handdrawn import build_scene_handdrawn

if __name__ == "__main__":
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    render_icon_from_builder(
        ICON_SIZE, RENDERS_DIR / "regular_handdrawn_icon.png", build_scene_handdrawn,
    )
