---
name: research-work
description: Develop and verify research calculations, numerical experiments, code, and figures in a project that uses the shared research workflow.
---

# Research Work

Read project context, the latest journal, and `.workflow/conventions.md`.
Establish the current objective and acceptance criteria before expanding a
calculation. Reuse the existing model and evidence.

## Develop and verify

- Check prior work before making novelty claims. Record assumptions, units, bases,
  observables, and competing explanations where they affect the result.
- Distinguish hypotheses, numerical evidence, and established results. Validate
  with relevant limits, convergence checks, or independent calculations rather
  than judging success from an attractive plot.
- Keep analytic checks in self-contained scripts that end with `assert`-style
  comparisons against the closed-form results stated in the paper.

## Code

- Define each model and its observables once; figure scripts and notebooks import
  them. Private experiments may reuse shared code, never the reverse.
- When signs, bases, units, or normalizations become nontrivial, record them in one
  conventions note linked from `project.md`. Check physical invariants when
  changing conventions across code, manuscript, and figures.
- For figures, read [figures.md](figures.md).

## Environments

- Use the Python environment of the normal shell unless the project specifies
  another. Do not create a virtual environment per project or experiment, and do
  not borrow one from an unrelated project.
- Prefer uv when dependency management is needed, but avoid `uv run`, `uv sync`,
  and `uv add` during exploration: they create `.venv/` or resolve dependencies.
  Keep an existing project's manager unless migration is requested.
- Add only dependencies the code uses. Record useful versions and commands with
  important results; defer exact locking to codebase release.
- If a package is missing, report it and ask before changing a shared environment.
  Do not substitute vendored code, rewrite working code to avoid the dependency,
  force system installs, or use `--break-system-packages`. A demonstrated conflict
  may justify an isolated environment, agreed with the user.

## Bibliography

The project bibliography is a superset of the manuscript's. Manage it with
[pynakes](https://github.com/maiani/pynakes) when available; `pynakes capabilities`
lists the installed commands:

```sh
pynakes ref import bibliography/<slug>.bib DOI-arXiv-ID-or-URL
pynakes lint bibliography/<slug>.bib
```

Otherwise add BibTeX entries manually. Keep local copies of useful sources in
`bibliography/<slug>.files/`, pynakes' material folder, which Git ignores.
