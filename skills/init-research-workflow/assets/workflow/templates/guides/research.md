# Research implementation defaults

Project configuration and local instructions override these defaults.

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

- During exploration and code development, use the Python environment already
  provided by the normal shell, unless the project specifies another environment.
  Do not create a virtual environment for each project or experiment by default,
  and do not borrow an environment from an unrelated project.
- Prefer uv when Python dependency management is needed. Avoid automatic
  `uv run`, `uv sync`, or `uv add` during exploration: project commands can create
  `.venv/` or resolve dependencies. Run scripts with `python` in the existing
  environment. Do not change an existing project's manager without a migration
  request.
- Add only dependencies actually needed. Record useful versions and execution
  commands with important results, but defer exact dependency locking to codebase
  release preparation. Do not preload a scientific or notebook stack.
- If the current environment lacks a package, report it and ask before modifying
  that shared environment. Do not force system installs or use
  `--break-system-packages`. A demonstrated dependency conflict may justify an
  isolated environment earlier, agreed with the user.
- Before releasing code, declare its Python requirements in `pyproject.toml`,
  generate `uv.lock`, and verify representative results in a clean environment
  using `uv sync --locked` and `uv run --locked`. Keep both files in version
  control for the release. Document system tools, fonts, and hardware separately;
  the Python lockfile does not capture them. Preserve an existing release lock
  unless dependency changes are intentional.

Available plotting tools include `numpy`, `scipy`, `matplotlib`, `sympy`, `svg.py`,
`figworks`, and `vectex` (Python 3.12 or newer). LaTeX labels need `pdflatex`,
`dvisvgm`, and `mutool` on `PATH`. PDF/PNG export also needs Cairo, fontconfig,
and the chosen fonts (the default FigWorks theme uses TeX Gyre Heros).

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
