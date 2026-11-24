---
name: research-setup
description: Initialize a minimal research project or adopt the shared research workflow in an existing project, preserving scientific content and local conventions. Use when the user asks to start, set up, or bootstrap a research or paper project, or to adopt or attach the research workflow in an existing project.
---

# Set Up a Research Workflow

Resolve this SKILL.md through any symlink. The kit root is two directories above
its containing folder and holds workflow.py, tools/, and templates/.
Keep the complete kit together; individual skill folders are not standalone.

## Existing projects

When asked to adopt the workflow, inspect the project's instructions and repository
boundaries first. Run from its root:

```sh
python <kit-root>/workflow.py adopt [--title "<title>"] [--author "<authors>"]
```

Pass the title and authors when known; optional components use them later.
Only this setup skill and manuscript-preflight are registered centrally. Adoption
installs a pinned copy of the method, including the research, repository, and
manuscript skills, and adds a short AGENTS.md block routing to it, without
creating project folders or replacing existing instructions. Local rules remain
overrides; review conflicting old defaults selectively. Adoption does not
authorize changes to models, environments, manuscript settings, remotes, or
publication status.
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
python <kit-root>/workflow.py init "$PWD" \
  --title "<title>" --author "<authors>" --desc "<objective>" \
  [--rename-to "<confirmed-slug>"] [--overleaf-url "<url-or-id>"]
```

Quote each value. Setup needs only Python 3.11+ and Git. It commits the private
root repository locally. Pass `--commit` to also commit new nested repositories,
only with explicit authorization; never commit into an Overleaf checkout.

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
without a current need. Tests stay in the kit source; shared tools remain inside
the hidden method snapshot, outside the visible project scaffold.

Continue the user's actual research task with the skill that
`.workflow/conventions.md` names for it. Update project.md and the journal with
the objective, evidence, and next action. Explain optional setup only as it
becomes relevant:

```sh
python .workflow/workflow.py add manuscript
python .workflow/workflow.py add repository
```

Local project instructions override the shared skills. Updates refresh the method
only; existing scientific files and build configuration remain project-owned.
