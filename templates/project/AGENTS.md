# {{ PROJECT_TITLE }}

Agent instructions for this research project, shared by all agents; read this file
explicitly if your client does not load it automatically.

{{ WORKFLOW_BLOCK }}

## Project layout

| Path | Contents | Git repository | Visibility |
| --- | --- | --- | --- |
| `project.md` | Objective, current stage, next action, links to evidence | root | Private |
| `journal/` | One `YYYY-MM-DD.md` per day, opening with a Previous session summary | root | Private |
| `workspace/` | Exploration: derivations, code, notes, scratch experiments | root | Private; never shared |
| `bibliography/` | `{{ PROJECT_SLUG }}.bib`, a superset of the manuscript's references | root | Private |
| `repository/` | Promoted, reproducible code and accompanying material | nested `{{ PROJECT_SLUG }}-repository` | Collaborators; public on release |
| `manuscript/` | Authoritative manuscript source; an `overleaf` remote is authoritative | nested `{{ PROJECT_SLUG }}-manuscript` | Co-authors; public on submission |

The root repository is `{{ PROJECT_SLUG }}`. `repository/` and `manuscript/` are
independent repositories, excluded from the root and never submodules; create them
only when that work starts, with `python .workflow/workflow.py add repository` or
`add manuscript`. Results flow one way: `workspace/` → author approval →
`repository/` → `manuscript/`.

## Project-specific instructions

Record scientific assumptions, notation and conventions (signs, units, bases),
environments, and working preferences here or in notes linked from here.
