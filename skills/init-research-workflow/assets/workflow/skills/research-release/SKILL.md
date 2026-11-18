---
name: research-release
description: Prepare reproducible research artifacts and manuscript-connected outreach for an author-approved release.
---

# Research Release

Read `.workflow/conventions.md`, project context, and local
`workflows/release.md` if present. Confirm the intended artifact and audience.
Promotion from private workspace/ requires the author's approval. Use `python
.workflow/workflow.py add repository` only when shared artifacts are needed.

Check that shared code runs without private files, that dependencies and figure
commands are recorded, and that results match the manuscript. Keep numerical
settings and model choices explicit. Record the workflow revision used.

For a codebase release, declare actual dependencies in `pyproject.toml`, generate
`uv.lock`, and verify representative outputs in a clean environment with
`uv sync --locked` and `uv run --locked`. Include the manifest and lockfile in the
release; document system requirements separately. Respect an existing project's
manager unless migration is requested. Exploratory work does not require a new
virtual environment or exact pins; release preparation does require verification
of the resolved dependencies.

Create outreach (`add outreach`), talks, or slides only for an actual requested
deliverable. Keep authoritative sources and reproduction commands with it.
Preparing a release does not authorize a push, publication, or external upload.
