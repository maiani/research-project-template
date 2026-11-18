---
name: research-manuscript
description: Draft or revise a research manuscript, referee response, or manuscript-connected outreach using the project's verified evidence.
---

# Research Manuscript

Read project context, the latest journal, and `.workflow/conventions.md`.
Preserve collaborator edits and the authoritative manuscript repository. Trace
substantive claims to evidence; keep unverified interpretations explicit and
preserve unresolved author decisions.

## Set up and build

- When writing starts and no manuscript repository exists, run
  `python .workflow/workflow.py add manuscript`. For an existing Overleaf project,
  use its authorized checkout rather than a competing manuscript.
- Run `latexmk` (or `just build`) from `manuscript/`; `.latexmkrc` selects the main
  file. Use `latexmk other.tex` for supplemental material or
  `latexmk submission/response.tex` for a response letter.
- Build products go to `aux/` and `out/`, both ignored by Git; keep them for
  incremental builds. `just clean` removes auxiliary files and `just clean-all`
  also removes PDFs; both accept source filenames. `just watch` previews
  continuously. Overleaf uses its own build paths and does not run Just recipes.
- Inspect the rendered output. Changes to build settings, formatting, or dependency
  locks are separate project changes.

## Source conventions

- Use semantic line breaks ([sembr.org](https://sembr.org)): start each sentence,
  and useful long clauses, on a new source line, even without a formatter.
- Badness formatting is optional: `just format` or `just format-check` use the
  repository's `badness.toml` and skip generated `*_diff.tex` files.
- Pre-commit hooks are opt-in: Badness formats sources, and Pynakes checks BibTeX
  entries and duplicate citation keys offline. Run `just install-hooks` only when
  wanted and `pre-commit` is installed; hooks are per clone and Overleaf does not
  run them.

## Revisions and referee reports

- Generate diffs explicitly with `latexdiff --flatten old.tex new.tex >
  revision_diff.tex`, then `latexmk revision_diff.tex`. Review bibliography and
  package-specific diff issues for the actual manuscript.
- Create only the response and material the actual report needs;
  `python .workflow/workflow.py add response` adds a starting template under
  `manuscript/submission/`. Map each response to manuscript edits and evidence.

## Outreach

For a requested lay summary, graphical abstract, or press material, run
`python .workflow/workflow.py add outreach` and keep it in `manuscript/outreach/`.
Its README records authoritative sources, reproduction commands, and external
copies; review it before editing or exporting outreach material.
