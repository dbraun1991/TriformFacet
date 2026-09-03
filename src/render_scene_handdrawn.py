"""Hand-drawn/sketchbook style variant of `render_scene.py`'s wide
establishing shot: same geometry, camera, and shadow-mapped lighting rig,
restyled — warm paper palette, sepia ink, and genuinely wobbly stroke
geometry for the room's corner edges (not a straight line dressed up to
*look* wobbly, and not an image-space filter over the rendered PNG).

Third of the three deferred alternate rendering styles (blueprint/
technical-drawing and cel/toon shipped first, ADR 0029/0030). Unlike
those two, there's no existing PyVista/VTK feature to lean on here — a
"sketchy line" renderer isn't something the library provides, needed
building from primitives (`pv.MultipleLines` and basic trig), documented
in ADR 0031.

`add_sketchy_line()` subdivides a straight edge into many points and
displaces each one, perpendicular to the edge, by a sum of a few sine
waves at randomized (but seeded, so reproducible) frequency/phase/weight —
smooth low-frequency noise, not per-point jitter, so the result reads as
one continuous hand-wobbled stroke rather than static. Each edge is drawn
2-3 times with different seeds, each pass fully opaque (see ADR 0031 for
why partial opacity silently fails here) but independently wobbled, so the
passes visibly diverge from each other along the line's length — reading
as multiple overlaid pencil attempts even without alpha blending — with a
small overshoot past each endpoint (real sketched lines rarely stop
exactly on the corner).

Applied only to the room's three shared corner edges — the wedge
cylinder's own outline stays the clean `add_feature_edges()` linework from
the blueprint/cel variants (undistorted, default resolution): its
silhouette is a real shadow-mapped 3D solid with genuine curvature, and a
per-mesh-edge independent jitter on ~100 short facet-boundary segments
would read as a broken line, not one coherent wobbly stroke, without a lot
more machinery to keep neighboring segments' jitter continuous. Scoped out
for now — see ADR 0031's Consequences.
"""

import numpy as np
import pyvista as pv

from render_scene import (
    HEIGHT,
    ROOM,
    RENDERS_DIR,
    SCENE_CAMERA_FOCAL_POINT,
    SCENE_CAMERA_POSITION,
    SCENE_CAMERA_UP,
    SCENE_CAMERA_VIEW_ANGLE,
    add_feature_edges,
    add_fitted_lights,
    build_room_and_object,
)

HANDDRAWN_PALETTE = {
    "background": "#241a10",  # dark sepia void, not bright paper — see
    # module docstring: a bright void against the default ambient=0.12
    # unlit-wall darkness read as a black silhouette cutout, not paper.
    "floor": "#d8c39c",
    "wall_back": "#e0cca3",
    "wall_side": "#cdb691",
    "object": "#faf5e6",
}

# Same fix render_scene_blueprint.py needed (ADR 0029): the default
# ambient=0.12 crushes any base color to near-black unlit, which only
# reads fine when the void behind the room is *also* near-black (the
# default scene's own look). Raised here too, paired with the warm
# palette above, so the unlit walls stay a visible warm tan.
HANDDRAWN_SURFACE_SHADING = dict(ambient=0.55, diffuse=0.55)

INK_COLOR = "#4a3524"


def _sketch_offset(t, seed, amplitude):
    """Smooth, seeded pseudo-random displacement over the [0, 1] parametric
    range `t` — a weighted sum of a few sine waves at random frequency/
    phase, not per-sample noise, so it reads as one continuous wobble."""
    rng = np.random.default_rng(seed)
    freqs = rng.uniform(1.0, 2.8, size=3)
    phases = rng.uniform(0, 2 * np.pi, size=3)
    weights = rng.uniform(0.4, 1.0, size=3)
    weights /= weights.sum()
    offset = np.zeros_like(t)
    for freq, phase, weight in zip(freqs, phases, weights):
        offset += weight * np.sin(2 * np.pi * freq * t + phase)
    return amplitude * offset


def add_sketchy_line(
    plotter, p0, p1, color=INK_COLOR, n_points=48, passes=3, amplitude=0.22,
    line_width=2.5, base_seed=0, opacity=1.0,
):
    """Draw a hand-wobbled approximation of the straight segment p0->p1:
    `passes` overlapping jittered strokes (see `_sketch_offset`), each
    displaced perpendicular to the segment and slightly overshooting both
    endpoints — each pass's independent random wobble diverges from the
    others at different points along the line, so the *set* still reads as
    a messy multi-stroke sketch even at full opacity.

    `opacity` defaults to fully opaque, not partial, despite these tubes
    visually overlapping: this edge sits exactly on the seam between two
    already-opaque room quads (ADR 0031 found this the hard way) — a
    translucent tube there loses the depth test against the opaque quads
    already in the depth buffer and silently fails to render at all, a
    generic translucent-vs-opaque-at-equal-depth issue, not a bug specific
    to this scene.
    """
    p0, p1 = np.asarray(p0, dtype=float), np.asarray(p1, dtype=float)
    direction = p1 - p0
    length = np.linalg.norm(direction)
    direction = direction / length

    # Any vector not parallel to `direction` works as a seed for the
    # perpendicular; z-up unless the edge itself runs along z.
    seed_vec = np.array([0.0, 0.0, 1.0]) if abs(direction[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    perp = np.cross(direction, seed_vec)
    perp /= np.linalg.norm(perp)

    t = np.linspace(0.0, 1.0, n_points)
    overshoot = 0.02 * length
    for k in range(passes):
        offset = _sketch_offset(t, base_seed * 100 + k, amplitude)
        pts = p0 + np.outer(t * length, direction) + np.outer(offset, perp)
        pts[0] -= direction * overshoot
        pts[-1] += direction * overshoot
        plotter.add_mesh(
            pv.MultipleLines(points=pts), color=color, line_width=line_width,
            lighting=False, render_lines_as_tubes=True, opacity=opacity,
        )


def add_sketchy_room_edges(plotter, color=INK_COLOR):
    """The room's three shared corner edges (see
    `add_edge_highlight_lines`), hand-wobbled instead of ruler-straight."""
    edges = [
        ((0, 0, 0), (ROOM, 0, 0)),
        ((0, 0, 0), (0, ROOM, 0)),
        ((0, 0, 0), (0, 0, HEIGHT)),
    ]
    for i, (p0, p1) in enumerate(edges):
        add_sketchy_line(plotter, p0, p1, color=color, base_seed=i + 1)


def build_scene_handdrawn(plotter):
    meshes = build_room_and_object(
        plotter, palette=HANDDRAWN_PALETTE, surface_shading=HANDDRAWN_SURFACE_SHADING,
    )
    add_fitted_lights(plotter)
    add_sketchy_room_edges(plotter, color=INK_COLOR)
    add_feature_edges(plotter, {"cylinder": meshes["cylinder"]}, color=INK_COLOR, line_width=1.5)


if __name__ == "__main__":
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 1200), lighting="none")
    build_scene_handdrawn(plotter)

    # Same camera as render_scene.py's default look — a style variant, not
    # a recomposition.
    plotter.camera.position = SCENE_CAMERA_POSITION
    plotter.camera.focal_point = SCENE_CAMERA_FOCAL_POINT
    plotter.camera.up = SCENE_CAMERA_UP
    plotter.camera.view_angle = SCENE_CAMERA_VIEW_ANGLE

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDERS_DIR / "scene_handdrawn.png"
    plotter.screenshot(str(out_path))
    print(f"wrote {out_path}")
