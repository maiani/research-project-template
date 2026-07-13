# Academic Research Workflow changelog

This file records changes to the research workflow itself, independently of any
paper, dataset, or public-code release created from the template.

## Unreleased

- Added pinned `tex-fmt` formatting and pre-commit configuration to generated
  manuscript repositories, with wrapping disabled and generated latexdiff
  sources excluded.
- Added explicit manuscript recipes for formatting, checking, and installing
  hooks, plus bootstrap preservation and smoke-test coverage.

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
