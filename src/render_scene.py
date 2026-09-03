"""Render a floating object in the corner of a room (floor + two walls).

The three orthogonal planes double as an unscaled coordinate frame: the floor
is the x-y plane, the two walls are x-z and y-z, meeting at the corner (0,0,0).
The object floats above the floor with its long axis parallel to the
floor/wall-1 edge (the x-axis).

Three spotlights illuminate the scene, each pinned to the axis running
straight through the object's center, perpendicular to one surface, and
pulled back along that axis — near-parallel, "direct" light rather than a
nearby point source. Each light's cone angle is derived from the room's own
geometry so its circular footprint stays inscribed within its own surface
(tangent to the nearest edge) rather than spilling its color onto a
neighboring wall — a farther corner may go dark instead. Real shadow mapping
is enabled, so the floating object casts a distinct shadow onto each of the
three surfaces.

The floating object is a "wedge cylinder": a cylinder with a full circular
cross-section at one end, sliced by two symmetric planes (one from above, one
from below) that converge to a single diametral line at the other end. This
keeps the object's silhouette a circle when viewed end-on (down its axis) and
a rectangle when viewed from directly above (its footprint never narrows in
the axis-perpendicular direction, since the z=0 diameter survives the whole
taper) — while the side view (perpendicular to both the axis and to "above")
becomes a triangle, since the taper is linear. One object, three different
"true" shadow shapes depending on which side you observe it from.
"""

from pathlib import Path

import numpy as np
import pyvista as pv

# Every render script writes into ../renders/ relative to this file (i.e.
# <repo root>/renders/), regardless of the cwd it's invoked from — resolved
# from __file__ rather than assumed cwd == repo root. Defined once here and
# imported by the other render_*.py siblings so they can't drift onto
# different output locations.
RENDERS_DIR = Path(__file__).resolve().parent.parent / "renders"

ROOM = 28.0    # room extends 0..ROOM along x and y — doubled again per
HEIGHT = 24.0  # ADR 0021 (first doubled per ADR 0017). Both linear
# dimensions double, so each surface's area — floor ROOM×ROOM, walls
# ROOM×HEIGHT — comes out four times its old size, not just double. Object
# position/size and light padding below are deliberately NOT touched (ADR
# 0018/0021) so only the surfaces themselves get bigger; the camera IS
# rescaled to match (ADR 0020/0021 — see the __main__ camera comment).

CYL_RADIUS = 0.5
CYL_LENGTH = 2.8 * 2 / 3  # shortened by one third — closer to boxish proportions
# Deliberately NOT scaled up with the room (ADR 0017) — kept at its
# original absolute size so it (and the light circles, sized off CYL_CENTER
# below, not off this) end up relatively smaller within the now-bigger
# room, leaving more dark room/corner-line area for the room's own
# silhouette to reach a square crop's frame edges — aimed at closing
# ADR 0014's leftover background-bleed gap in icon.png.

# (x, y, z) — floating, at the same distance M from all three near
# surfaces (floor, wall_back, wall_side), not just the same *margin*
# arrived at via different coordinates like the previous placement (ADR
# 0012). See ADR 0017/0018.
#
# M is a FIXED constant — deliberately NOT derived from ROOM/HEIGHT (an
# earlier version used M = HEIGHT/2, which scales the object and its light
# circles up right along with the room, defeating the point: doubling the
# room was supposed to leave everything else the same absolute size, so
# the object/circles end up relatively smaller and the room's own
# silhouette has more reach to close icon.png's white-void gap. M = 3
# matches the object's position from before the room doubled (ADR 0018),
# so neither the object nor the circles grew even though the room did.
# Still valid as the binding margin on every surface at the new, bigger
# ROOM/HEIGHT (M <= ROOM-M and M <= HEIGHT-M, comfortably true at M=3).
_M = 3.0
CYL_CENTER = (_M, _M, _M)

# Gap kept between each light shape and the white corner line nearest it
# (ADR 0017) — subtracted from the raw margin/aperture rather than filling
# all the way to the line the way ADR 0009's original tangent circles did.
LIGHT_PADDING = 0.5


def fit_cone_half_angle(distance, center_a, extent_a, center_b, extent_b, padding=0.0):
    """Half-angle (degrees) for a spotlight's circular footprint to land
    *inscribed* within a rectangular target surface spanning
    [0, extent_a] x [0, extent_b], aimed at (center_a, center_b), from
    `distance` away along the surface's normal, shrunk by `padding` (world
    units, at the target plane).

    Uses the distance to the *nearest* edge, not the farthest corner: the
    footprint circle stays tangent to the closest edge and therefore never
    spills past the surface's own boundary onto a neighboring wall (no
    color overlap). The tradeoff — deliberately preferred over any overlap
    — is that a farther corner can fall outside the lit circle and stay
    dark. `padding` (ADR 0017) pulls the circle back from that near edge by
    a fixed gap instead of leaving it exactly tangent, so it doesn't touch
    the white corner line drawn along that same edge
    (`add_edge_highlight_lines`).
    """
    margin = min(center_a, extent_a - center_a, center_b, extent_b - center_b) - padding
    return float(np.degrees(np.arctan(margin / distance)))


def quad(p0, p1, p2, p3):
    """Explicit quad from four corners, exact edges — no guessing PyVista's
    Plane axis convention."""
    mesh = pv.PolyData(np.array([p0, p1, p2, p3]), faces=[4, 0, 1, 2, 3])
    mesh.compute_normals(auto_orient_normals=True, inplace=True)
    return mesh


def make_wedge_cylinder(radius, length, resolution=96, full_end="max"):
    """A cylinder (axis along x, centered at the origin) with a full round
    cross-section at one end, tapering via two symmetric planar cuts (upper
    and lower) to a flat diametral line at the other end.

    full_end="max" puts the untouched full circle at local x=+length/2 and
    the thin-line end at x=-length/2 (or the reverse for "min").
    """
    x_full = length / 2 if full_end == "max" else -length / 2
    x_thin = -length / 2 if full_end == "max" else length / 2
    slope = -radius / (x_thin - x_full)  # dz/dx of the upper taper line

    cyl = pv.Cylinder(
        center=(0, 0, 0), direction=(1, 0, 0), radius=radius, height=length,
        resolution=resolution, capping=True,
    )
    cyl = cyl.triangulate().clean()

    n_upper = np.array([slope, 0.0, -1.0])
    n_upper /= np.linalg.norm(n_upper)
    wedge = cyl.clip_closed_surface(normal=n_upper, origin=(x_full, 0, radius))

    n_lower = np.array([slope, 0.0, 1.0])
    n_lower /= np.linalg.norm(n_lower)
    wedge = wedge.triangulate().clean().clip_closed_surface(
        normal=n_lower, origin=(x_full, 0, -radius)
    )

    # split_vertices so the crease between the curved surface and the two
    # flat cut faces gets distinct normals on each side — without this,
    # smooth shading blends across the crease and produces dark banding.
    wedge.compute_normals(
        auto_orient_normals=True, split_vertices=True, feature_angle=45,
        inplace=True,
    )
    return wedge


def build_room_and_object(plotter):
    """Add the room (floor + two walls) and the floating wedge cylinder to
    `plotter` — everything about the scene except lighting, which is
    `add_fitted_lights`'s own concern. Shared by every render variant
    (`render_scene.py`, `render_icon.py`, `render_icon_highres.py`) so the
    room/object geometry can't drift out of sync between them.
    """
    plotter.set_background("#eef1f5")
    plotter.enable_anti_aliasing("ssaa")

    # --- room: floor (x-y) and two walls (x-z at y=0, y-z at x=0), sharing
    # the corner edge (0, 0, 0..HEIGHT) exactly ---
    floor = quad((0, 0, 0), (ROOM, 0, 0), (ROOM, ROOM, 0), (0, ROOM, 0))
    wall_back = quad((0, 0, 0), (ROOM, 0, 0), (ROOM, 0, HEIGHT), (0, 0, HEIGHT))  # y=0
    wall_side = quad((0, 0, 0), (0, ROOM, 0), (0, ROOM, HEIGHT), (0, 0, HEIGHT))  # x=0

    surface_kwargs = dict(smooth_shading=True, specular=0.05, ambient=0.12, diffuse=0.9)
    plotter.add_mesh(floor, color="#d9d4c6", **surface_kwargs)
    plotter.add_mesh(wall_back, color="#e6e2d6", **surface_kwargs)
    plotter.add_mesh(wall_side, color="#cec9ba", **surface_kwargs)

    # --- the floating wedge cylinder: full circle facing the camera (large
    # x, nearest the viewer), tapering to a thin line at the small-x end ---
    cylinder = make_wedge_cylinder(CYL_RADIUS, CYL_LENGTH, full_end="max")
    cylinder.translate(CYL_CENTER, inplace=True)
    plotter.add_mesh(
        cylinder,
        color="#f2f0ea",  # light gray, near-white — reflects the projected
        # light colors rather than competing with them with its own hue
        smooth_shading=True,
        specular=0.4,
        specular_power=20,
        diffuse=0.85,
        ambient=0.12,
    )


def add_edge_highlight_lines(plotter, color="#ffffff", line_width=3.0):
    """Draw the room's three shared edges (floor/wall_back, floor/wall_side,
    wall_back/wall_side) as bright, unlit lines.

    These are rendered with `lighting=False` — a deliberate cheat, not a
    simulated light source: nowhere in a physically-lit version of this
    scene can a line "honestly" stay visible in every corner, since the
    corners are by construction exactly where none of the three spotlights
    reach (see ADR 0009's dark-corner tradeoff). Kept as an isolated,
    additive change on top of the normal fitted lighting, rather than
    touching the light rig itself (ADR 0013/0015).
    """
    edges = [
        ((0, 0, 0), (ROOM, 0, 0)),   # floor / wall_back shared edge
        ((0, 0, 0), (0, ROOM, 0)),   # floor / wall_side shared edge
        ((0, 0, 0), (0, 0, HEIGHT)),  # wall_back / wall_side shared edge
    ]
    for p0, p1 in edges:
        plotter.add_mesh(
            pv.Line(p0, p1),
            color=color,
            line_width=line_width,
            lighting=False,
            render_lines_as_tubes=True,
        )


def add_fitted_lights(plotter):
    """Add the three inscribed-footprint spotlights (see
    `fit_cone_half_angle`) and enable shadow mapping — the scene's one
    lighting rig, used by every render variant.
    """
    # --- three spotlights, each aimed straight down one axis at the
    # cylinder ---
    # Each light shares two of the cylinder center's three coordinates
    # exactly, varying only the coordinate normal to its target surface —
    # so it sits on the axis running straight through the cylinder,
    # perpendicular to that surface, rather than off at an oblique angle.
    # It's then pulled back along that axis: far enough that the rays
    # reaching the room are effectively parallel (direct/"sunlight"-like),
    # not a nearby point source spraying outward. Each also gets a
    # distinct, clearly saturated color so the surface it's responsible for
    # reads as its own hue.
    #
    # Note: pulling the lights back to 10x the room size (as originally
    # tried) reads as more "direct," but empirically breaks VTK's
    # shadow-map coverage at this scene scale — isolated tests showed the
    # illuminated area shrinking to a fraction of the wall well before
    # 10x, regardless of cone_angle (which turned out not to be the
    # limiting factor at all). 5x keeps the rays nearly as parallel (the
    # angular spread only grows from ~4° to ~8°) while staying inside the
    # distance range where the shadow map behaves.
    far = 5 * ROOM  # distance along the fixed axis

    # Each cone_angle is derived (via fit_cone_half_angle) from the room's
    # own geometry, not hand-picked — a fixed 30° cone at this distance
    # massively overshoots each surface (its footprint radius alone would
    # be ~20, several times the room size), spilling colored light past
    # every surface's edges onto its neighbors. The fitted angle keeps each
    # light's footprint inscribed within its own surface instead.
    lights = {
        "floor": pv.Light(  # varies z only — straight down onto the floor
            position=(CYL_CENTER[0], CYL_CENTER[1], far),
            focal_point=CYL_CENTER,
            color="#ffb54d",  # amber
            intensity=0.85,
            cone_angle=fit_cone_half_angle(
                far, CYL_CENTER[0], ROOM, CYL_CENTER[1], ROOM, padding=LIGHT_PADDING
            ),
        ),
        "wall_back": pv.Light(  # varies y only — straight at the back wall (y=0)
            position=(CYL_CENTER[0], far, CYL_CENTER[2]),
            focal_point=CYL_CENTER,
            color="#5b9bd5",  # blue
            intensity=0.85,
            cone_angle=fit_cone_half_angle(
                far, CYL_CENTER[0], ROOM, CYL_CENTER[2], HEIGHT, padding=LIGHT_PADDING
            ),
        ),
        "wall_side": pv.Light(  # varies x only — straight at the side wall (x=0)
            position=(far, CYL_CENTER[1], CYL_CENTER[2]),
            focal_point=CYL_CENTER,
            color="#e8637f",  # rose
            intensity=0.85,
            cone_angle=fit_cone_half_angle(
                far, CYL_CENTER[1], ROOM, CYL_CENTER[2], HEIGHT, padding=LIGHT_PADDING
            ),
        ),
    }
    for light in lights.values():
        light.positional = True
        light.exponent = 0  # flat falloff inside the cone — no visible hot spot
        light.attenuation_values = (1, 0, 0)  # no distance falloff, so pulling
        # the lights back only narrows/straightens the rays, not the brightness
        plotter.add_light(light)

    plotter.enable_shadows()


def build_scene(plotter):
    """`build_room_and_object()` + `add_fitted_lights()` + the unlit
    corner-edge lines (`add_edge_highlight_lines()`) — the scene, used by
    `render_scene.py` (this file's own `__main__`) and by `render_icon.py`.

    The edge lines were originally a separate experiment (ADR 0013), tried
    alongside a "pixel-perfect" fully-lit alternative that widened each
    light to fully cover its own surface instead of leaving dark corners.
    The edge-lines look was preferred and promoted to the default here (ADR
    0015); the pixel-perfect variant was later removed outright (ADR 0026)
    rather than kept as an unused alternate.
    """
    build_room_and_object(plotter)
    add_fitted_lights(plotter)
    add_edge_highlight_lines(plotter)


if __name__ == "__main__":
    plotter = pv.Plotter(off_screen=True, window_size=(1600, 1200), lighting="none")
    # lighting="none" — pv.Plotter defaults to lighting="light kit", which
    # silently attaches 5 camera-relative lights (a headlight + 4 "camera
    # lights") in addition to any lights added explicitly. Those aren't part
    # of this scene's three-light design, but enable_shadows() still casts
    # them, producing a second, fainter, differently-shaped shadow on every
    # surface alongside the intended one. Disabling the automatic kit leaves
    # only the three explicit pv.Light objects added in build_scene().
    build_scene(plotter)

    # --- camera: standing inside the room, looking into the corner ---
    # Position/focal_point are scaled by exactly the same 2x factor
    # ROOM/HEIGHT were just doubled by again (ADR 0021), same as the first
    # doubling (ADR 0017/0020) — i.e. expressed as a fraction of
    # ROOM/HEIGHT, both are UNCHANGED across every doubling so far (e.g.
    # 53.6/ROOM == 26.8/(old ROOM) == 13.4/(older ROOM), for every
    # component). This is a deliberate choice, not the same kind of mistake
    # as ADR 0018's M bug: M was supposed to be a fixed, room-size-
    # independent distance (the object's own position), while the camera's
    # job is to frame the *room* itself, so keeping it at a fixed fraction
    # of the room's size — not a fixed absolute position — is what keeps a
    # consistent view of the room as it grows. A literal fixed-absolute
    # camera was tested and rejected (ADR 0020): it crops the light circles
    # at icon.png's frame edges (reopening ADR 0011/0014), since the camera
    # would then be relatively too close to the now-bigger room.
    plotter.camera.position = (53.6, 51.2, 32.4)
    plotter.camera.focal_point = (7.6, 10.4, 6.4)
    plotter.camera.up = (0, 0, 1)
    plotter.camera.view_angle = 32

    RENDERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RENDERS_DIR / "scene.png"
    plotter.screenshot(str(out_path))
    print(f"wrote {out_path}")
