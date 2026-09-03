"""Blueprint-style icon crop — the exact composition from
`render_scene_blueprint.py`'s `build_scene_blueprint()` (ADR 0029), through
`render_icon.py`'s tuned square icon camera (ADR 0022/0023/0024) instead of
`render_scene.py`'s wide establishing-shot camera. Same room/object
geometry as the default icon — the blueprint variant only changes
palette/lighting/linework, not geometry — so the same zero-background-bleed,
full-circle-containment guarantees hold without re-deriving the camera.
"""

from render_icon import ICON_SIZE, render_icon_from_builder
from render_scene import RENDERS_DIR
from render_scene_blueprint import build_scene_blueprint

if __name__ == "__main__":
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    render_icon_from_builder(
        ICON_SIZE, RENDERS_DIR / "regular_blueprint_icon.png", build_scene_blueprint,
    )
