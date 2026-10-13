# AI agent instructions — academic research

**Academic Research Workflow version:** 2.0.0

This is the working root for an academic research paper. Read [project.md](project.md)
for the project context — what this paper is, its current status, and physics goals.
These instructions are shared across agents; read this file explicitly when
your client does not load it automatically.

## Project boundaries

| Folder | Purpose | Git repository (remote) | Visibility and release |
|---|---|---|---|
| `workspace/` | Private, personal exploration: draft code, computations, notes, evidence, and agent experiments | root `<slug>` (`github`) | Private; never shared or released |
| `repository/` | Shared/public artifact: reproducible code, documentation, and accompanying material | nested `<slug>-repository` (`github`) | Shared or public; release contents as appropriate |
| `manuscript/` | Authoritative LaTeX manuscript | nested `<slug>-manuscript` (`overleaf` authoritative, `github` mirror) | Private or mirrored from Overleaf; uploaded to arXiv |
| `bibliography/` | Project bibliography, including sources beyond those cited in the manuscript | root `<slug>` (`github`) | Private |
| `journal/` | Daily chained session log | root `<slug>` (`github`) | Private |

- `repository/` must never import from or reference `workspace/`.
  Shared code and plots must be complete and reproducible; documentation and
  supporting material must be organized and ready for collaborators.
- Use `workspace/scratch/` for private agent experiments instead of an
  untracked system temporary directory. Leave a concise trace of the inputs,
  commands, outputs, and conclusion with each experiment; promote only
  finalized results through the normal workflow.
- Treat an existing Overleaf remote as authoritative for `manuscript/`.
  Otherwise use the local manuscript repository created during setup and add
  the remote later.
- Keep the three repositories independent — never submodules — under one
  GitHub organization or account, and create remotes or publish only when
  explicitly authorized.
- Keep `project.md` current when the project stage or next action changes;
  put detailed evidence in the journal and link it rather than duplicating logs.
- New physics results remain hypotheses until verified analytically or
  numerically.
  Report honestly when an effect is fragile.

## Promotion and revisions

- Promotion is the author's call.
  Move code and plots from `workspace/` to `repository/` only after the
  calculation is finalized and the author explicitly approves it.
  Move documentation and accompanying material when the author decides they are
  ready to share. Mark retained workspace prototypes as superseded and link
  their authoritative replacement; do not maintain two active implementations.
- Keep manuscript-connected outreach material, such as lay summaries,
  graphical abstracts, and press-ready figures, in `manuscript/outreach/`.
  Its README records authoritative sources, reproduction commands, and any
  external copies; review it before editing or exporting outreach material.
- Develop revisions on a branch inside `repository/`, never directly on `main`.
  The branch may be shared with collaborators.
  Squash-merge it into `main` only when the revision becomes public, so `main`
  continues to represent the latest released state.

The normal flow is private derivation and computation (`workspace/`) → author
promotion → shared code and material (`repository/`) → paper
(`manuscript/`).

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

## Journaling

Journal entries are chained by day so each session loads with full context in one read.

- **Start of session:** read the newest file matching `journal/20??-??-??.md`.
  Its **Previous session** block at the top summarizes the preceding day. Reach
  back to older files only when the
  summary isn't enough — this keeps token usage minimal.
- **On starting work:** before working, read the latest daily entry. If today is
  different from the latest entry's date, create a new dated file
  `journal/YYYY-MM-DD.md`. **Begin the file with a `## Previous session`
  block** — a concise summary (up to ~8 lines) of the preceding day's entry. Then
  document the current session below. If today is the same day, append each
  additional session to today's existing file; do not rewrite its **Previous
  session** block.
- Update the journal with what was done, what's blocked, and the next action.
- For cross-checks by another agent, link the relevant sources and evidence;
  distinguish independently verified results from prior claims and record any
  unresolved disagreement.

## Coding style

- Define each model and its observables once; figure scripts and notebooks
  import them. Private experiments may reuse shared code, never the reverse.
- When signs, bases, units, or normalizations become nontrivial, record them
  in one conventions note linked from `project.md`. Check physical invariants
  when changing conventions across code, manuscript, and figures.

- Always use the **object-oriented API**: call methods on `Figure` and `Axes`
  instances (`ax.plot()`, `ax.set_xlabel()`, `fig.savefig()`, etc.). Never use
  legacy stateful pyplot functions (`plt.plot()`, `plt.xlabel()`, `plt.title()`,
  `plt.legend()`, etc.). The only accepted `plt.*` calls are figure/axes
  constructors (`plt.figure()`, `plt.subplots()`, `plt.style.use()`) and
  `plt.rcParams` reads.

## Environment and dependencies

- For private work in `workspace/`, use the Python environment provided by the
  normal shell (the system/default environment), unless the user specifies
  another environment. Do not borrow an environment from an unrelated project.
- For shared code in `repository/`, use its Pixi environment: run commands from
  that directory with `pixi run`. Maintain `pixi.toml` and `pixi.lock` together
  so collaborators can reproduce the resolved dependencies. Keep `.pixi/`
  untracked. Use `pixi install --locked` when reproducing an existing lockfile;
  use `pixi install` to resolve the initial environment or intentional changes.
- When promoting code from `workspace/` to `repository/`, declare its
  dependencies and verify it in Pixi rather than assuming the shell environment
  is sufficient. A lockfile fixes package resolution; system tools and fonts
  must also be documented for reproducible figures.
- If a package is missing from the normal shell environment, report it and ask
  before installing it. Do not vendor substitutes or rewrite code to avoid a
  missing dependency. Manage repository dependencies through Pixi.

The plotting stack is `numpy`, `scipy`, `matplotlib`, `sympy`, `svg.py`,
`figworks`, and `vectex` (Python 3.12 or newer). LaTeX labels need `pdflatex`,
`dvisvgm`, and `mutool` on `PATH`. PDF/PNG export also needs Cairo, fontconfig,
and the chosen fonts (the default FigWorks theme uses TeX Gyre Heros).

## Figures

- Use Matplotlib's object-oriented API for plots, svg.py for 2D sketches,
  VecView for 3D scenes, VecTeX for mathematical labels, and FigWorks for
  composition and SVG/PDF/PNG export. VecView is optional.
- Use a shared style, manuscript-numbered filenames, and reproducible scripts.
  Inspect rendered figures before delivery. Final Inkscape touch-up belongs
  in `manuscript/svg/`; upstream fixes belong in the generating code.
- Read [guides/figures.md](guides/figures.md) for composition, 3D integration,
  typography, and export details when working on figures.

## Bibliography

Add every external scholarly resource you consult and consider useful to the
bibliography; this does not apply to files that are part of the project itself.
Keep the project bibliography in `bibliography/<project-slug>.bib`.
It is a superset of the manuscript bibliography, so exploratory references may
remain there even when they are not cited in the paper yet.

Manage it with [pynakes](https://github.com/maiani/pynakes) when available:

Use the bibliography directory for local copies of useful sources as well.
If pynakes is unavailable, add BibTeX entries manually and keep the same
provenance and local-file boundaries.
