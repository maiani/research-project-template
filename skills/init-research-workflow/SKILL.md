---
name: init-research-workflow
description: Initialize a minimal research project or adopt the shared research workflow in an existing project, preserving scientific content and local conventions.
---

# Set Up a Research Workflow

Resolve paths relative to this skill folder. The bundled scaffold and workflow
are portable; do not depend on a separate development checkout.

## Existing projects

When asked to adopt the workflow, inspect the project's instructions and repository
boundaries first. Run from its root:

```sh
python <skill-root>/assets/workflow/workflow.py adopt
```

This installs the shared method and adds instruction routing, without creating
project folders or replacing existing instructions. Local rules remain overrides;
review conflicting old defaults selectively. Adoption does not authorize changes
to models, environments, manuscript settings, remotes, or publication status.
Use `adopt --editable /path/to/development-checkout` only when a pilot project is
explicitly intended to follow development changes immediately.

## New projects

Confirm the intended directory. Require it to be empty, except for empty reserved
`.git`, `.agents`, `.codex`, `.claude`, and `.aws` directories. For a populated
project, use adoption instead of copying a scaffold over it.

Derive a lowercase kebab-case slug from the directory name. Collect the missing
title, authors, and short objective, reusing information already supplied. Ask one
question at a time when needed. The title can serve as the description. Confirm
any directory rename. Ask about an existing Overleaf project when manuscript work
is part of the current task; do not require future publication choices to begin.

```sh
python <skill-root>/scripts/init_project.py "$PWD" \
  --title "<title>" --author "<authors>" --desc "<objective>" \
  [--rename-to "<confirmed-slug>"] [--overleaf-url "<url-or-id>"]
```

Quote each value. Setup needs only Python 3.11+ and Git. Nothing is staged or
committed by default. Use `--commit` only with explicit authorization for initial
local commits; never commit into an Overleaf checkout.

Default setup creates the project context, private workspace, bibliography,
journal, and shared package. Add `--manuscript` or `--repository` only if that work
is needed now. An Overleaf URL implies manuscript setup and preserves the remote
as authoritative, named `overleaf`. Do not create remotes or publish without an
explicit request.

## Verify and continue

Read the generated AGENTS.md explicitly. Check project metadata, the dated journal,
bibliography, and installed shared package. Confirm that any requested manuscript
or artifact repository has an independent Git root and is excluded from root Git.
No optional outreach, response, slides, or scratch directories should be created
without a current need. Setup tests and development scripts stay in the package
source, outside the visible project scaffold.

Continue the user's actual research task using the relevant installed skill.
Update project.md and the journal with the objective, evidence, and next action.
Explain optional setup only as it becomes relevant:

```sh
python .workflow/workflow.py add manuscript
python .workflow/workflow.py add repository
```

The ongoing skills cover research, manuscript/revision, and sharing/release. Local
project instructions override them. Updates refresh the method only; existing
scientific files and build configuration remain project-owned.
