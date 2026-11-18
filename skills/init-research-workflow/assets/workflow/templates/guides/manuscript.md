# Manuscript defaults

Project configuration and local instructions override these defaults.

## Manuscript source and optional formatting

- Run `latexmk` (or `just build`) from `manuscript/`; `.latexmkrc` selects
  the main manuscript. Use `latexmk other.tex` for supplemental material or
  `latexmk submission/response.tex` for a response letter.
- Build products live in `aux/` (logs, bibliography, references) and `out/`
  (PDFs), both ignored by Git. Keep auxiliary files between builds for
  incremental compilation. `just clean` removes auxiliary files;
  `just clean-all` also removes generated PDFs. Both accept source filenames.
- `just watch` runs latexmk's continuous preview mode. Change `.latexmkrc`
  when configuring the engine or default manuscript; Overleaf controls its
  own build paths and does not run Just recipes.
- Generate revisions explicitly with `latexdiff --flatten old.tex new.tex >
  revision_diff.tex`, then `latexmk revision_diff.tex`. Review bibliography
  and package-specific diff issues for the actual manuscript.
- Use **semantic line breaks** ([sembr.org](https://sembr.org)) for prose:
  start each sentence, and useful long clauses, on a new source line.
  Preserve this convention manually even when no formatter is installed.
- Badness integration is optional.
  When it is installed, run `just format` or `just format-check` from
  `manuscript/`; both use the repository's `badness.toml` and exclude generated
  `*_diff.tex` files.
- The pre-commit hooks are also opt-in: Badness formats sources, and Pynakes
  checks BibTeX entries and duplicate citation keys offline.
  Run `just install-hooks` only when desired and when `pre-commit` is installed.
  Hooks are local to each clone and are not installed by cloning or run by
  Overleaf.
