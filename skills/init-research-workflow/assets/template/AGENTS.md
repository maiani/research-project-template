# AI agent instructions — academic research

**Academic Research Workflow version:** 1.3

This is the working root for an academic research paper. Read [project.md](project.md)
for the project context — what this paper is, its current status, and physics goals.

## Project boundaries

| Folder | Purpose | Versioning and release |
|---|---|---|
| `workspace/` | Private, personal exploration: draft code, computations, notes, evidence, and agent experiments | Private root repo; never shared or released |
| `repository/` | Shared/public artifact: reproducible code, documentation, and accompanying material | Nested shared repo; release contents as appropriate |
| `manuscript/` | Authoritative LaTeX manuscript | Nested Overleaf repo; uploaded to arXiv |
| `bibliography/` | Project bibliography, including sources beyond those cited in the manuscript | Private root repo |
| `journal/` | Daily chained session log | Private root repo |

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
- New physics results remain hypotheses until verified analytically or
  numerically.
  Report honestly when an effect is fragile.

### Project tree

Use this layout when populating the project.
Some directories are intentionally empty at initialization and are created for
future work rather than filled with placeholder files.

```text
.
├── workspace/              # private exploration, calculations, and evidence
│   └── scratch/            # persistent agent experiments and their trace
├── repository/             # collaborator-ready reproducible artifact
│   ├── analytics/          # self-contained analysis scripts
│   └── plots/              # reproducible figure scripts and generated figures
│       └── figures/
├── manuscript/             # authoritative LaTeX source
│   ├── checkpoints/         # manuscript checkpoints and intermediate versions
│   ├── outreach/             # manuscript-connected outreach material
│   ├── submission/          # response letters and submission material
│   ├── svg/                 # finalized figures for manuscript touch-up
│   ├── badness.toml         # manuscript formatter configuration
│   └── justfile             # manuscript build and formatting recipes
├── bibliography/           # superset BibTeX database and local source files
├── journal/                # dated chained session logs
└── project.md              # project context, status, and physics goals
```

Keep generated build products, downloaded PDFs, and caches out of the tracked
directories unless a later instruction explicitly promotes them as artifacts.

## Promotion and revisions

- Promotion is the author's call.
  Move code and plots from `workspace/` to `repository/` only after the
  calculation is finalized and the author explicitly approves it.
  Move documentation and accompanying material when the author decides they are
  ready to share.
- Keep manuscript-connected outreach material, such as lay summaries,
  graphical abstracts, and press-ready figures, in `manuscript/outreach/`.
- Develop revisions on a branch inside `repository/`, never directly on `main`.
  The branch may be shared with collaborators.
  Squash-merge it into `main` only when the revision becomes public, so `main`
  continues to represent the latest released state.

The normal flow is private derivation and computation (`workspace/`) → author
promotion → shared code and material (`repository/`) → paper
(`manuscript/`).

## Manuscript source and optional formatting

- Use **semantic line breaks** ([sembr.org](https://sembr.org)) for prose:
  start each sentence, and useful long clauses, on a new source line.
  Preserve this convention manually even when no formatter is installed.
- Badness integration is optional.
  When it is installed, run `just format` or `just format-check` from
  `manuscript/`; both use the repository's `badness.toml` and exclude generated
  `*_diff.tex` files.
- The pre-commit formatter hook is also opt-in.
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

## Coding style

- Always use the **object-oriented API**: call methods on `Figure` and `Axes`
  instances (`ax.plot()`, `ax.set_xlabel()`, `fig.savefig()`, etc.). Never use
  legacy stateful pyplot functions (`plt.plot()`, `plt.xlabel()`, `plt.title()`,
  `plt.legend()`, etc.). The only accepted `plt.*` calls are figure/axes
  constructors (`plt.figure()`, `plt.subplots()`, `plt.style.use()`) and
  `plt.rcParams` reads.

## Figure style and consistency

- Avoid using title elements.
- Name figure output files with the manuscript figure number plus a descriptive
  slug, e.g. `Fig4-description.pdf` or `FigS2-description.pdf`.
- Name figure scripts in `repository/plots/` to match: `Fig4-description.py`,
  `FigS2-description.py`, etc.
- Figure scripts must generate SVG, PDF, and PNG outputs. Use the PNG for visual
  inspection.
- When a new figure from `repository/` is ready to be included in the manuscript,
  move its SVG to `manuscript/svg/` for the author's final touch-up in Inkscape
  before exporting it as a PDF. Keep the reproducible script and model code in
  `repository/`.
- Name model modules descriptively (e.g. `projected_model.py`, `observables.py`).
- Analytics scripts in `repository/analytics/` must be self-contained and end
  with `assert`-style checks against the closed-form results in the paper.
- Apply a common `paper_plot_style.mplstyle` to every panel.
- After generating or regenerating any panel, visually verify that text and
  graphical elements do not overlap, font sizes suit the target column width,
  and stacked or adjacent panels meet their alignment constraints.

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

## Bootstrapping a new project

When the user says "start a new project" or "bootstrap from the template",
you (the AI agent) drive the setup by:

1. **Ask the user** for the following (one at a time, naturally):
   - Project slug (directory name, e.g. `project-slug`)
   - Paper title
   - Author name(s)
   - Short description (optional — falls back to the title)
   - Whether they already have an Overleaf project URL or project id (optional)
2. **Run `./bootstrap.sh`** with the collected values:
   ```
   ./bootstrap.sh \
       --slug "<slug>" \
       --title "<title>" \
       --author "<author>" \
       --desc "<description>" \
       [--overleaf-url "<url-or-project-id>"]
   ```
3. **Report the result** — tell the user what was created and the next steps.

The bootstrap script removes the bootstrap material, including this section.

**Template-development exception:** while `bootstrap.sh` and the placeholder
`journal/YYYY-MM-DD.md` both exist, this is still the unbootstrapped template.
Do not create a dated journal file alongside the placeholder. Normal journaling begins after bootstrap renames the placeholder to the actual date.
