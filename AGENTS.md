# AI agent instructions — academic research

**Academic Research Workflow version:** 1.1

This is the working root for an academic research paper. Read [project.md](project.md)
for the project context — what this paper is, its current status, and physics goals.

## Layout

| Folder | Role | Versioning | Ships in release? |
|---|---|---|---|---|
| `repository/` | **Finalized** code — complete & reproducible, published with the paper | nested git → public repo | **Yes** |
| `manuscript/` | The manuscript (LaTeX) | nested Overleaf git | Uploaded on arXiv |
| `workspace/` | Exploration & draft code, computation, notes, evidence | tracked by the root repo | **No** |
| `bibliography/` | Project bibliography (superset of the manuscript) | BibTex tracked by the root repo | **No** |
| `journal/` | Session log — one dated file per day | tracked by the root repo | **No** |

## Working rules

- **`workspace/` is private and never released.** New ideas, derivations,
  **exploratory and draft code, computations**, and accumulated evidence live here.
  This is where calculations and plots are first developed. The public code repo
  must never import from or reference it. Build artifacts are git-ignored.
- **`repository/` is the public artifact — finalized code only.** It must stay
  complete and reproducible (it ships with the paper). It is a separate nested
  git repository; the private root repo should not track it.
- **Promotion is the author's call.** Code/plots move from `workspace/` to
  `repository/` only when a calculation is finalized AND the author explicitly
  decides to promote it. Don't move work into the published repo autonomously —
  propose it and wait for the call.
- **`manuscript/` is authoritative on Overleaf.** Treat Overleaf git as the source of
  truth. If an Overleaf remote exists, clone it into `manuscript/`; do not create
  an independent local manuscript repository.

- **Evidence-before-claims:** new physics results are hypotheses until verified
  numerically. Confirm an effect is real (and report honestly if it's fragile)
  before a rebuttal commits to it.

## How the three folders interact (revision workflow)

1. **Derive, compute & explore in `workspace/`** — analytic notes work out the
   symmetry/algebra and end with a "Takeaway for the rebuttal", and draft
   figure/calculation code is developed and run here. This is where a result is
   first established and verified.
2. **Promote finalized code to `repository/`** — once a calculation is done and
   the author calls it, the script moves to the published repo.
3. **Fold into `manuscript/`** — the verified result becomes a main-text sentence/panel
   (kept minimal) plus the bulk in Supplemental Material, and a point in the
   rebuttal letter.

So a typical task flows: derive + compute (workspace) → [author promotes] → finalized
script + figure (code) → manuscript + rebuttal (paper).

## Journaling

Journal entries are chained so each session loads with full context in one read.

- **Start of session:** read the latest entry in [journal/](journal/) (newest
  filename by ISO date). Its **Previous session** block at the top gives you
  last session's context. Reach back to older files only when the
  summary isn't enough — this keeps token usage minimal.
- **On starting a new session:** before working, read the latest entry. If
  today is a different day than the latest entry's date, create a new dated file
  `journal/YYYY-MM-DD.md`. **Begin the file with a `## Previous session`
  block** — a concise summary (up to ~8 lines) extracted from that latest entry. Then
  document the current session below. This makes every new file self-contained
  context for the next agent invocation. If today is the same day, append to the
  existing entry instead.
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
- When a figure script in `repository/` is ready, created, or updated, place
  the generated SVG in `manuscript/svg/` for the author's final Inkscape
  touch-up. Keep the reproducible script and model code in `repository/`.
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
Manage the bibliography with [pynakes](https://github.com/maiani/pynakes) if available.
Use it to keep a local copy of any useful resource.

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