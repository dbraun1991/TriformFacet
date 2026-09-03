# 0028 — `src/` and `renders/` directories

## Status

Accepted

## Context

Before this, every `render_*.py` script and every generated `.png` output
sat flat in the repo root alongside `README.md`, `AGENTS.md`, `LICENSE`, and
`docs/`. That was five scripts and five images (`scene.png`, `icon.png`,
`highres_icon.png`, `grayscale_icon.png`, `highres_grayscale_icon.png` as of
ADR 0027) crowding the top level, with more of both kinds explicitly
expected (AGENTS.md's Future Work lists alternate rendering styles —
blueprint, cel/toon, hand-drawn — as deferred but not abandoned).

Considered, and rejected, going further to a proper installable-package
layout (`src/triformfacet/__init__.py` etc., with relative imports). ADR
0003 deliberately scoped this project as a single static illustration with
"no config/CLI layer" — there's no `setup.py`/`pyproject.toml`, nothing
installs this, and the scripts' only consumers are each other (direct
imports) and a human running `python <script>.py`. A package/import
machinery upgrade would be solving a problem this project doesn't have.

Considered, and rejected, grouping `renders/` output by variant (`renders/
icon/`, `renders/icon_grayscale/`, etc.) rather than flat — with only 5
files today, the extra directory nesting wasn't worth it; flat `renders/`
can be revisited if the variant count grows enough to make the flat list
hard to scan.

## Decision

- New `src/` directory holds all five `render_*.py` scripts, moved via `git
  mv` where already tracked. They keep importing each other by bare module
  name (e.g. `from render_scene import build_scene`) — unchanged from
  before the move, since Python puts a directly-invoked script's own
  directory on `sys.path[0]`, and every script here is always run that way
  (`python src/render_icon.py`, not imported as a package member).
- New `renders/` directory holds all five generated PNGs, flat, moved the
  same way.
- `render_scene.py` gained one new constant, `RENDERS_DIR = Path(__file__).
  resolve().parent.parent / "renders"` — resolved from the script's own
  file location, not the invoking shell's cwd, so every script writes to
  the same `<repo root>/renders/` regardless of where it's invoked from.
  Every other `render_*.py` imports `RENDERS_DIR` from `render_scene`
  rather than hardcoding a second copy of the path, and calls
  `RENDERS_DIR.mkdir(parents=True, exist_ok=True)` before writing (the
  directory now needs to exist, unlike the old flat layout where every
  script's own cwd already existed by definition).
- Verified no regression: re-ran all five scripts after the move and diffed
  every output against its pre-move version — byte-identical across the
  board (only the write *location* changed, nothing about the render
  pipeline itself).

## Consequences

- Repo root now holds only docs (`README.md`, `AGENTS.md`, `LICENSE`,
  `docs/`) plus the two new top-level directories — materially less
  cluttered, and scales cleanly to more scripts/outputs (e.g. the deferred
  alternate-style renderers) without another reorg.
- Every script can be run from any cwd and still write to the right place —
  more robust than the old implicit "assumes cwd == repo root" behavior,
  which was never actually documented as a requirement before.
- `src/`'s flat, non-package layout means a script run as `python
  src/render_icon.py` works, but `python -m src.render_icon` or importing
  `render_icon` from outside `src/` (e.g. a future test suite in a sibling
  `tests/` directory) would not, without adding `src/` to `sys.path`
  first. Acceptable for now per ADR 0003's scope; revisit if that scope
  ever changes.
