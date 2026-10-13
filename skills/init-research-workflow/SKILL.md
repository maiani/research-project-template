---
name: init-research-workflow
description: Initialize a new academic research project in the current empty working directory using the bundled research workflow template, including private exploration, reproducible code, manuscript, bibliography, journal, and Git boundaries. Use when the user asks to run /init-research-workflow, start a new research project, initialize an academic paper workflow, or bootstrap a paper project in an empty folder.
---

# Init Research Workflow

Initialize the current empty directory as a new academic research project.
These instructions apply to any agent with filesystem and shell access. Resolve
`<skill-root>` as the directory containing this file, regardless of how the
client discovers or invokes the skill.

The skill is portable: use the bundled template snapshot rather than assuming
that the template repository is the current directory.

## Preconditions

- Confirm that the current working directory is the intended project directory.
- Require it to be empty before copying the template. Empty reserved
  `.git`, `.agents`, `.codex`, `.claude`, and `.aws` directories created by managed
  workspaces are allowed and preserved; populated directories are rejected.
  If it is not empty, stop and ask the user to choose an empty directory or
  explicitly clarify that an existing project should be migrated.
- Read the skill’s bundled workflow only as needed; do not search for a second
  template repository elsewhere on the machine.
- Do not create a dated journal file manually.

## Collect project details

Ask for these details one at a time, in this order:

1. Derive the project slug from the current directory name. If it is lowercase
   kebab-case, ask the user to confirm that it is the intended project name;
   do not ask for the slug independently.
   If it is not a valid slug, or the user wants a different name, ask for a
   lowercase kebab-case replacement and confirm that the empty directory may be
   renamed before initialization.
2. Temporary project title.
3. Author name or names.
4. Short description, allowing the project title as the fallback.
5. Existing Overleaf project URL or project ID, if one exists.

Do not ask all questions in one message.
The final directory name and slug must be lowercase kebab-case: lowercase
letters and digits separated by single hyphens (for example, `project-slug`).
Treat an omitted Overleaf value as a request for a local manuscript repository.

## Initialize the directory

After collecting all details, invoke the bundled script from the current
working directory:

```sh
python <skill-root>/scripts/init_project.py "$PWD" \
  [--rename-to "<confirmed-slug>"] \
  --slug "<slug>" \
  --title "<title>" \
  --author "<author>" \
  --desc "<description>" \
  [--overleaf-url "<url-or-project-id>"] [--no-commit]
```

Use `--no-commit` when the user wants an uncommitted project; otherwise the
initializer creates initial local commits. Never commit into an Overleaf checkout.
Use the exact collected values and quote every argument. Pass `--rename-to`
only after the user has confirmed a different valid directory name. The runner
renames only an empty target directory and rejects a slug that does not match
the final directory name.
The initializer validates inputs, prepares the project from `assets/template/`,
and initializes the Git repositories. Only Python 3.11+ and Git are needed for setup.
Do not manually recreate the directory layout.

The resulting project contains private `workspace/` exploration,
collaborator-ready `repository/` artifacts, an authoritative `manuscript/`, a
superset `bibliography/<slug>.bib`, and a dated chained journal entry.
When an Overleaf URL or project ID is supplied, preserve the Overleaf checkout
as the authoritative manuscript repository, with its remote named `overleaf`.
An optional GitHub manuscript mirror must use the remote name `github` and is
added only after the user authorizes its account or organization.

## Verify and report

After initialization:

- Read the generated `AGENTS.md` explicitly; do not depend on client-specific
  automatic loading.
- Confirm `project.md` contains the title, description, and authors; confirm
  the three repository naming conventions are documented in `AGENTS.md`.
- Confirm `repository/.git` and `manuscript/.git` exist.
- Confirm the root Git repository does not track files from either nested
  repository.
- Confirm `bibliography/<slug>.bib` and the dated `journal/<date>.md` exist.
- Confirm setup scripts, tests, and the development-only `skills/` directory
  were not copied into the generated project.
- Report what was created and the next steps: edit the project context, add an
  Overleaf remote if needed, keep exploration in `workspace/`, and promote only
  finalized material to `repository/`.

Do not commit, push, or publish additional changes beyond the commits made by
the initializer unless the user explicitly asks for that separate
action.
