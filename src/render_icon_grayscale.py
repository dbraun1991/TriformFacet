"""Grayscale variant of `render_icon.py`'s square icon: identical scene,
object, and camera (via `render_icon()`), but each of the three spotlights
uses a light, fully desaturated (R=G=B) color instead of amber/blue/rose —
so the three shadow shapes are told apart by lightness rather than hue.

"Light" here means restricted to the upper half of the grayscale range
(0xff down to 0xb3 — i.e. >= ~70% white), not just any gray: the point is a
bright, airy mark, not a literal amber/blue/rose desaturation (which would
have landed much darker/muddier, since none of those three hues are
naturally light when flattened to luminance alone).
"""

from render_icon import ICON_SIZE, render_icon
from render_scene import RENDERS_DIR

GRAYSCALE_LIGHT_COLORS = {
    "floor": "#ffffff",      # brightest — was amber
    "wall_back": "#d9d9d9",  # mid-light — was blue
    "wall_side": "#b3b3b3",  # dimmest of the three, still light — was rose
}


def render_grayscale_icon(size, output_path):
    render_icon(size, output_path, light_colors=GRAYSCALE_LIGHT_COLORS)


if __name__ == "__main__":
    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    render_grayscale_icon(ICON_SIZE, RENDERS_DIR / "grayscale_icon.png")
