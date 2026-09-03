# 0007 — Local virtual environment for Python dependencies

## Status

Accepted

## Context

The dev machine's system Python is externally managed, and the project
needs `pyvista` (which pulls in `vtk`, a large binary dependency) without
polluting or depending on system-wide packages.

## Decision

Create a project-local virtual environment (`python3 -m venv .venv`) and
install `pyvista` into it. All commands run through `.venv/bin/python` /
`.venv/bin/pip` rather than a bare `python`/`pip`.

## Consequences

- Reproducible, isolated dependency set; nothing installed system-wide.
- `.venv/` is a local build artifact and should be excluded from version
  control once this directory becomes a git repository (it isn't one yet).
- Anyone (human or agent) running `render_scene.py` needs to create/activate
  this venv first — documented in `README.md` → "Running it" and in
  `AGENTS.md`.
