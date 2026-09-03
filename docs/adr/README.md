# Architecture Decision Records

Numbered, chronological record of the decisions behind `render_scene.py`.
Format: Context / Decision / Consequences. Status is "Accepted" unless noted.

| # | Title |
| --- | --- |
| [0001](0001-rendering-engine.md) | Rendering engine: PyVista (VTK), headless |
| [0002](0002-explicit-room-quads.md) | Room surfaces built as explicit quads, not `pv.Plane` |
| [0003](0003-single-static-illustration.md) | Scope: single static illustration, not a parametrized generator |
| [0004](0004-real-shadow-mapping.md) | Real shadow mapping via positional lights, not faked contact shadows |
| [0005](0005-axis-pinned-distant-lights.md) | Lights pinned to the object's center axis, capped at 5x room size |
| [0006](0006-wedge-cylinder.md) | Floating object built as a "wedge cylinder" for circle/rectangle/triangle shadows |
| [0007](0007-local-venv.md) | Local virtual environment for Python dependencies |
| [0008](0008-neutral-object-color.md) | Floating object recolored to near-white |
| [0009](0009-fitted-cone-angles.md) | Cone angles fitted to room geometry, not hand-picked |
| [0010](0010-disable-default-lightkit.md) | Disable PyVista's default "light kit" on the Plotter |
| [0011](0011-icon-render.md) | Separate square icon render, sharing scene setup via `build_scene()` |
| [0012](0012-equalized-shadow-sizes.md) | Wedge cylinder repositioned to equalize all three shadow-circle sizes |
| [0013](0013-corner-visibility-experiments.md) | Two corner-visibility experiments: unlit edge lines vs. pixel-perfect + blockers |
| [0014](0014-icon-full-containment.md) | Icon camera re-tuned for full circle containment, not edge-to-edge fill |
| [0015](0015-promote-whiteline-to-default.md) | Unlit edge lines promoted from experiment to the default scene |
| [0016](0016-gobo-masks-fix-pixelperfect-overlap.md) | Gobo aperture masks replace blocker fins, fixing pixel-perfect's color overlap |
| [0017](0017-symmetric-object-and-padded-lighting.md) | Room scale-up, symmetric object placement, and padded lighting (all variants) |
| [0018](0018-fixed-object-distance-not-room-derived.md) | Object distance M is a fixed constant, not derived from the (now bigger) room |
| [0019](0019-pixelperfect-padding-asymmetry-unresolved.md) | Pixel-perfect's padding gap renders visibly asymmetric; root cause not found — **closed as moot, see 0026** |
| [0020](0020-camera-scales-with-room-not-fixed.md) | Camera position/focal_point deliberately scale with the room, unlike the object |
| [0021](0021-second-room-enlargement.md) | Second room enlargement (2x), same fixed-object/scaled-camera treatment |
| [0022](0022-icon-gets-its-own-closer-camera.md) | `icon.png` gets its own, closer camera, decoupled from `render_scene.py` — also fixes a real (previously eyeballed-away) corner bleed |
| [0023](0023-icon-camera-tuned-for-tighter-fill.md) | Icon camera pulled in further (`k` search down to the clipping boundary) for a tighter fill |
| [0024](0024-icon-camera-centered-padding.md) | Icon camera centered (pan solved via Newton iteration) so left=right and top=bottom padding |
| [0025](0025-highres-icon-no-svg.md) | `highres_icon.png` (8192px, measured ceiling) added; vector `icon.svg` tested and rejected |
| [0026](0026-remove-pixelperfect-variant.md) | Removed the pixel-perfect variant (`render_scene_pixelperfect.py`); circles are now the only look — ADR 0019 closed as moot, not resolved |
| [0027](0027-grayscale-icon-variant.md) | Grayscale icon variant (`grayscale_icon.png`), light colors parameterized on the shared rig |
| [0028](0028-src-and-renders-directories.md) | `src/` and `renders/` directories: scripts and generated PNGs moved out of the repo root |
| [0029](0029-blueprint-style-variant.md) | Blueprint/technical-drawing style variant (`scene_blueprint.png`), `build_room_and_object` gains `surface_shading` |
| [0030](0030-celshade-style-variant.md) | Cel/toon-shading style variant (`scene_celshade.png`): low-poly flat-shaded object, black ink outline |
