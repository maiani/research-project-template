# Academic Research Workflow changelog

This file records changes to the research workflow itself, independently of any
paper, dataset, or public-code release created from the template.

## 3.0.0 — 2026-11-18

### Migration from 2.x

The setup skill is now `research-setup` (was `init-research-workflow`). Pull the
kit checkout, remove the old skill link or copy from your agent's skill directory,
and run `python workflow.py install` again. Existing 2.x projects adopt the
workflow without moving files (`workflow.py adopt`); their copied instructions
remain local overrides and need selective review, not automatic replacement.

### Changes

- Added a top-level `workflow.py` for one-time skill installation,
  initialization, and adoption, with agent-led installation first in the README.
- The kit lives at the repository root: `skills/`, `tools/`, `scaffold/`,
  `templates/`, `conventions.md`, and `tests/`. Only `research-setup` is installed
  globally.
- Each project receives a versioned `.workflow/` snapshot of the kit, with two
  ongoing skills: `research-work` (research, code, figures, codebase releases)
  and `research-manuscript` (manuscript, referee responses, outreach). The
  project's AGENTS.md gets a short block routing to `.workflow/conventions.md`,
  which names the skills. Local AGENTS.md rules override the shared defaults.
- Added release selection, persistent version pins, local-change protection,
  cached update checks, and editable pilot installs that link only the kit files.
  Updates run the selected version's installer and change only `.workflow/`,
  never local instructions, scientific content, environments, locks, or
  manuscript configuration. Checks report updates only for older releases,
  never suggest a downgrade, and never update automatically.
- New projects start with private work, context, bibliography, and journal only.
  Manuscript and shared repositories, outreach, and referee-response templates
  are added on demand with `add`; slides have no scaffold. Response and outreach
  templates can join existing folders without overwriting files.
- Initialization no longer stages or commits by default; `--commit` is explicit.
  Removed the `--no-commit` and `--slug` flags and the `init_project.sh` wrapper.
  `adopt` accepts `--title` and `--author` for components added later.
- Replaced the Pixi scaffold with a minimal uv-compatible `pyproject.toml`.
  Use existing Python environments for development; add dependencies as needed
  and lock and verify them when preparing a codebase release.
- Delegated figure API guidance to FigWorks' packaged skill, checked against
  FigWorks 0.11.0, VecTeX 0.5.0, and VecView 0.5.0. Updated optional manuscript
  hooks to Badness 0.29.1 and Pynakes 0.9.0.

## 2.0.0 — 2026-10-13

### Migration from 1.x

Initialize new projects through `skills/init-research-workflow/SKILL.md` or
`scripts/init_project.py` inside that skill folder; the template no longer
contains `bootstrap.sh`. Setup requires Python 3.11+ and Git. Existing projects
are not migrated automatically: adopt the manuscript `.latexmkrc`, updated
hooks, and workflow guidance selectively. Manuscript builds now write auxiliary
files to `aux/` and PDFs to `out/`. Agent instructions live in `AGENTS.md`;
clients that do not load it automatically should be told to read it explicitly.

### Changes

- Updated the Badness pre-commit hook to 0.27.0 and added Pynakes 0.7.0
  bibliography lint and duplicate citation-key checks.
- Removed CLAUDE.md aliases; keep one shared AGENTS.md and agent-neutral skill
  instructions, with optional client metadata separated from the workflow.
- Documented explicit instruction loading and evidence-based cross-checks when
  switching agents; allow empty Claude metadata directories during setup.
- Incorporated mature-project practices: convention notes when needed, model reuse,
  script/result mappings, cache provenance, and current project-stage summaries.
- Added a minimal outreach README and visuals folder for authoritative sources,
  reproducible assets, schematic/data distinctions, and delivery provenance.

- Consolidated setup into one Python initializer outside the template, with a
  compatibility shell wrapper. Tests are no longer copied into new projects.
- Moved figure examples into an on-demand guide and trimmed unrelated ignore rules.
- Made notebook dependencies optional and documented system TeX; setup itself
  requires only Python and Git.
- Preserved empty-directory checks, directory renaming, independent Git roots,
  initial-commit options, and authoritative Overleaf configuration/content.

- Documented optional VecView integration: direct scene panels, embedded plots,
  fixed-size labels anchored in 3D, and reusable camera projections.
- Replaced the manuscript Just build/cleanup/diff machinery with `.latexmkrc`
  and thin build/watch/clean recipes; separate ignored `aux/` and `out/`
  directories retain incremental build state.
- Updated the plotting workflow to FigWorks 0.8 / VecTeX 0.4 and Python 3.12+,
  including named panels, SVG/PDF/PNG export, fonts, and system dependencies.
- Corrected stale skill verification instructions and bootstrap behavior for
  fresh checkouts and no-commit initialization; protect ancestor Git repositories.
- Added the development-only `init-research-workflow` skill under `skills/`.
- Replaced `tex-fmt` with `badness`.
- Moved the GitHub repository plan out of `project.md` into the condensed
  project-boundary table in `AGENTS.md`.
- Added `svg.py`, `vectex`, and `figworks` to the generated plotting stack, with
  figure guidance requiring sketch panels to be built programmatically with
  `svg.py` and assembled with Matplotlib panels using FigWorks instead of
  hand-edited SVG.
- Adopted [vectex](https://github.com/maiani/vectex) for LaTeX labels inside
  sketches: it compiles snippets with `pdflatex` and `dvisvgm` into portable,
  textext-editable SVG groups, backed by its own on-disk cache. It replaces the
  bundled `repository/plots/latex_svg.py`, which has been removed along with
  `drawsvg`.
- Use the normal shell Python for private `workspace/` exploration unless the
  user specifies another environment. Use Pixi for `repository/`, keeping the
  manifest and lockfile together and verifying promoted code there.

## 1.2 — 2026-07-24

- Clarified that `repository/` is the shared/public artifact for reproducible
  code, documentation, and accompanying collaborator material, while
  `workspace/` is the author's private, personal working area.
- Added Windows support through Git Bash: Python command discovery now accepts
  `python3` or `python`, executable shell inputs are pinned to LF line endings,
  paths containing spaces are covered by the smoke test, and the generated Pixi
  workspace targets Linux, macOS, and Windows.
- Added optional, pinned Badness and pre-commit integration to generated
  manuscript repositories.
  Bootstrap does not require either tool; opt-in recipes format, check, or
  install hooks using semantic wrapping while excluding generated latexdiff
  sources.
- Consolidated bibliography guidance in `AGENTS.md`; bootstrap now creates the
  project BibTeX file directly instead of carrying bibliography placeholder
  files.

## 1.1 — 2026-07-10

- Made manuscript bootstrapping create a committed nested Git repository when
  no Overleaf remote is supplied, and always removed both nested repositories
  from the root index.
- Standardized journaling on one file per day with explicit daily discovery and
  same-day append behavior.
- Required figure scripts to generate SVG, PDF, and PNG outputs, with PNG used
  for inspection and finalized SVGs moved into the manuscript for touch-up.
- Made the workflow version visible in `AGENTS.md` and the root `README.md`.
- Clarified the boundary between private exploration, finalized public code,
  and the manuscript.
- Documented the unbootstrapped-template exception to normal journaling.
- Clarified that bibliography capture applies to useful external scholarly
  resources, not the project's own files.
- Added an isolated end-to-end bootstrap smoke test.
- Made generated projects thin by removing root bootstrap documentation, tests,
  assets, script, and bootstrap-specific agent instructions after setup.

## 1.0

- Established the research workflow, three-folder layout, journaling chain,
  bibliography conventions, figure standards, and guided bootstrap process.
