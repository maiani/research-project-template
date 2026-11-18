---
name: research-manuscript
description: Draft or revise a research manuscript or referee response using the project’s verified evidence.
---

# Research Manuscript

Read project context, `.workflow/conventions.md`, and local
`workflows/manuscript.md` if present. Preserve collaborator edits and the
authoritative manuscript repository. Trace substantive claims to evidence; keep
unverified interpretations explicit and preserve unresolved author decisions.

When manuscript work actually starts, use `python .workflow/workflow.py add
manuscript` if no manuscript repository exists. For an existing Overleaf project,
use its authorized checkout rather than creating a competing manuscript.
Read `.workflow/templates/guides/manuscript.md` for build and formatting defaults.
Build from manuscript/ using its own settings. Inspect rendered outputs. Changes
to dependency locks, build settings, or formatting are separate project changes.

For referee work, create only the response and supporting material needed for
the actual report (`add response` offers a starting template). Map each response
to manuscript edits and evidence. Do not create submission, outreach, or slides
folders in anticipation of future work.
