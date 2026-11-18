# {{ PAPER_TITLE }}

Shared material accompanying the manuscript. Promote only finalized code and
material approved for sharing; this codebase must not depend on private files.
Create analytics, model, plot, and documentation directories only as needed.

## Development

Use the existing shell Python environment and run scripts with `python`.
No virtual environment or lockfile is required just to start developing code.
`pyproject.toml` starts with no dependencies: add only what this codebase uses.
Do not install the entire plotting stack or notebook tooling in anticipation.
Prefer uv when dependency management becomes necessary; respect existing project
choices. Ask before changing a shared environment. Use an isolated environment
earlier only when a real compatibility problem or project requirement warrants it.

uv project commands such as `uv run` and `uv sync` normally manage a `.venv/`.
Use them for release verification rather than automatically during exploration.
Record the Python and relevant library versions alongside important results,
without freezing every exploratory environment.

## Release preparation

Before a codebase release, review the Python version requirement and declare all
runtime dependencies in `pyproject.toml`. Then resolve and validate them:

```sh
uv lock
uv sync --locked
uv run --locked python path/to/verification_script.py
```

Replace the example script path with this codebase's actual verification command.
Run this verification in a clean checkout or fresh environment. Check the results
against the manuscript, then include `pyproject.toml` and `uv.lock` in the release.
Keep `.venv/` untracked. Later reproduction uses the checked-in lockfile:

```sh
uv sync --locked
uv run --locked python path/to/figure_script.py
```

Document non-Python requirements separately: TeX, fonts, system libraries, and
hardware as applicable. Add notebooks or specialized plotting packages only if
used. Dependency upgrades after release are deliberate changes with validation.

## Reproducible results

Map each figure or analytic claim to its script and shared model. Record inputs,
parameters, expected outputs, commands, and approximate runtime. For cached results,
record the code version and how to rebuild or invalidate the cache. A cache must
not be the only surviving source of a result.

Keep editable figures and inspect exported versions. Document figure tooling and
any system requirements that are not captured by the Python lockfile.

## Citation

When the manuscript and repository have publication identifiers, document how to
cite them here.
