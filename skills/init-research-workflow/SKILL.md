---
name: init-research-workflow
description: Initialize a new academic research project in the current empty working directory using the bundled research workflow template, including private exploration, reproducible code, manuscript, bibliography, journal, and Git boundaries. Use when the user asks to run /init-research-workflow, start a new research project, initialize an academic paper workflow, or bootstrap a paper project in an empty folder.
---

# Init Research Workflow

Initialize the current empty directory as a new academic research project.
The skill is portable: use the bundled template snapshot rather than assuming
that the template repository is the current directory.

## Preconditions

- Confirm that the current working directory is the intended project directory.
- Require it to be empty before copying the template.
  If it is not empty, stop and ask the user to choose an empty directory or
  explicitly clarify that an existing project should be migrated.
- Read the skill’s bundled workflow only as needed; do not search for a second
  template repository elsewhere on the machine.
- Do not create a dated journal file manually.

## Collect project details

Ask for these details one at a time, in this order:

1. Project slug, used as the directory-safe project name and BibTeX filename.
2. Paper title.
3. Author name or names.
4. Short description, allowing the paper title as the fallback.
5. Existing Overleaf project URL or project ID, if one exists.

Do not ask all questions in one message.
Require a lowercase kebab-case slug: lowercase letters and digits separated by
single hyphens (for example, `project-slug`).
Treat an omitted Overleaf value as a request for a local manuscript repository.

## Initialize the directory

After collecting all details, invoke the bundled script from the current
working directory:

```sh
bash <skill-root>/scripts/init_project.sh "$PWD" \
  --slug "<slug>" \
  --title "<title>" \
  --author "<author>" \
  --desc "<description>" \
  [--overleaf-url "<url-or-project-id>"]
```

Use the exact collected values and quote every argument.
The script copies the bundled template, runs its preflight check, and invokes
the bundled `bootstrap.sh`.
Do not manually recreate the directory layout or bypass the script’s cleanup.

The resulting project contains private `workspace/` exploration,
collaborator-ready `repository/` artifacts, an authoritative `manuscript/`, a
superset `bibliography/<slug>.bib`, and a dated chained journal entry.
When an Overleaf URL or project ID is supplied, preserve the Overleaf checkout
as the authoritative manuscript repository.

## Verify and report

After initialization:

- Confirm `project.md` contains the title, description, and authors.
- Confirm `repository/.git` and `manuscript/.git` exist.
- Confirm the root Git repository does not track files from either nested
  repository.
- Confirm `bibliography/<slug>.bib` and the dated `journal/<date>.md` exist.
- Confirm bootstrap-only files and the development-only `skills/` directory do
  not remain in the generated project.
- Report what was created and the next steps: edit the project context, add an
  Overleaf remote if needed, keep exploration in `workspace/`, and promote only
  finalized material to `repository/`.

Do not commit, push, or publish additional changes beyond the commits made by
the bundled bootstrap script unless the user explicitly asks for that separate
action.
