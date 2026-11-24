# Academic Research Workflow changelog

This file records changes to the research workflow itself, independently of any
paper, dataset, or public-code release created from the template.

## 3.3.0 — 2026-11-24

### Migration from 3.2

Run `python .workflow/workflow.py update` in each project. Agents then start
journal entries with a provenance line and commit the root repository locally
after each entry; existing journal entries and AGENTS.md files are unchanged. The
commit rule also applies to adopted projects: if an adopted project's root
repository is shared and should stay manual, say so in its AGENTS.md.

Agents no longer check for updates. `check` is replaced by `update --dry-run`,
and `init --status` is removed. Updating drops the unused `updates` setting from
workflow.json.

### Changes

- Agent-written journal entries begin with a provenance line giving the model
  ID, harness and version, and session ID, with `unknown` rather than a guess.
  Entries mark the author's decisions and authorizations as theirs, and each
  check records who ran it: a rerun in the same session is not independent. A
  new project's first journal entry states that `workflow.py init` created it.
- The private root repository is committed locally after each journal entry,
  naming the entry, with large generated data left untracked. Commits in
  `repository/` and `manuscript/` still require authorization. `init` now makes
  the initial root commit by default, and `--commit` only adds initial commits in
  new nested repositories. Without a Git identity, `init` warns and leaves the
  root staged instead of failing.
- Simplified the project commands to `adopt`, `add`, `status`, and `update`.
  Agents no longer check for updates at session start. `update --dry-run`
  replaces `check`: it reports what an update with the same `--to`, `--unpin`,
  or `--source` would install, refuses where the update would, and changes
  nothing. `status` now works offline and reads as text: version, pin, source,
  and whether `.workflow/` has local changes. The daily check cache,
  `check --force`, the `updates` setting, and the unused `init --status` option
  are gone; new projects' project.md starts with the status "Initial setup.".
- Removed rules repeated in files agents load together. conventions.md no longer
  restates the AGENTS.md override, update-check caching, or the squash-merge and
  superseded-prototype details kept in the research-repository skill.
  research-work drops its journaling summary and its pointer to
  research-repository, which conventions already routes. New projects' AGENTS.md
  intro and journal header are shorter. With the new rules, conventions.md is
  still slightly shorter than in 3.2.0.

## 3.2.0 — 2026-11-24

### Migration from 3.1

Run `python .workflow/workflow.py update` in each project. The new-project files
moved from `.workflow/scaffold/` to `.workflow/templates/project/`; compare
against that path when adapting an existing AGENTS.md by hand.

Rerun `python workflow.py install` (with the same `--skills-dir`) from the central
checkout to register `manuscript-preflight`. If you installed the standalone
`editorial-presubmission-check` skill, remove it so only one audit skill remains.

### Changes

- Added the `manuscript-preflight` skill for pre-submission editorial and
  source-readiness audits and follow-up rechecks. It is integrated from
  [maiani/manuscript-preflight](https://github.com/maiani/manuscript-preflight)
  at `e635adf` (v1.1), by the same author under the same license, and works
  outside workflow projects too: its checklist and standard-library checker live
  in its own folder. The checker now reads build logs from the latexmkrc
  `$aux_dir` or `$out_dir`, so it finds logs in kit manuscripts without options;
  `--log-dir` overrides this. In workflow projects, reports are kept in
  `workspace/preflight/` and noted in the journal. `install` registers it
  centrally beside `research-setup`, so it is available for any manuscript.
- Merged `scaffold/` into `templates/project/`. `init` and `add` share one
  placeholder renderer, so an unknown placeholder is a clear error in both, and
  `init --check` now validates every template, not only the project files.
- The project snapshot includes the kit's LICENSE.
- New projects no longer get a root `.gitattributes`, a leftover from when the
  manuscript lived in the root repository; the manuscript repository keeps its
  own, now covering only its justfile. `add outreach` no longer creates an empty
  `visuals/` placeholder. The project `.gitignore` drops manuscript-only LaTeX
  patterns. Existing project files are unchanged.

## 3.1.0 — 2026-11-20

### Migration from 3.0

Run `python .workflow/workflow.py update` in each project; `workflow.json` then
records the readable version. Existing AGENTS.md files are not rewritten: their
block still routes to conventions.md, which now names the repository skill. To
add the new project layout, adapt it from `.workflow/scaffold/AGENTS.md` by hand.

### Changes

- Added the `research-repository` skill for `repository/`, parallel to
  `research-manuscript`: promotion, organization and README provenance,
  collaborator branches, and authorized codebase releases, including a review
  before anything becomes public and tagging releases to manuscript versions.
  `research-work` now covers research, calculations, code, and figures wherever
  the code lives. Existing projects receive the skill on update, without changes
  to their AGENTS.md.
- New projects' AGENTS.md again opens like 2.x: the shared-workflow block sits
  under the title, followed by a project layout giving each folder's contents,
  Git repository with the project's own remote names, and visibility, which
  folders are created on demand, and the workspace → repository → manuscript flow.
  Adopted projects still receive only the appended block; the rules stay in
  conventions.md for both.
- `workflow.json` records a readable `version` (release tag, or nearest tag plus
  commits), kept correct after updates, including rollbacks to 3.0.0. AGENTS.md
  points to it instead of copying a number, so updates still never edit it.
- Restored 2.x rules lost in 3.0: the journal path and `## Previous session`
  heading, honest reporting of fragile effects, Overleaf as the authoritative
  manuscript, squash-merging shared code into `main` at public revisions, figure
  file naming, and no in-figure titles.
- Corrected the bibliography note: only `bibliography/<slug>.files/` is ignored.

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
