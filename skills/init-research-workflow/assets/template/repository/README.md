# {{ PAPER_TITLE }}

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.0000000.svg)](https://doi.org/10.5281/zenodo.0000000)

Shared material accompanying the manuscript above.
This repository contains finalized reproducible scripts used to generate the
paper's calculations, checks, and figures, together with public documentation
and any other material intended for collaborators or release.

---

## Repository structure

This is the initial shared-repository structure.
Empty directories are created during bootstrap so early projects have a stable
place for finalized analytics and plot scripts.
Add clearly named directories such as `docs/` or `materials/` as the project
needs them for public documentation and other accompanying files.

```
.
├── analytics/       self-contained checks and analytic verification scripts
├── plots/           model modules and figure-generation scripts
│   └── figures/     generated output (git-ignored; reproducible from scripts)
├── pixi.toml        dependency specification
└── pixi.lock        resolved versions for reproducibility (created by pixi install)
```

### `analytics/`
Self-contained scripts that verify closed-form expressions, limiting cases, or
other analytic results quoted in the paper.

### `plots/`

- **Model modules** — shared implementations of the Hamiltonians and observables
  used by every figure.
- **Figure scripts** — one per manuscript figure. Outputs land in
  `plots/figures/`.
- **Sketch scripts** — schematics and illustrative panels drawn
  programmatically with [svg.py](https://github.com/orsinium-labs/svg) and
  assembled with Matplotlib panels using
  [FigWorks](https://github.com/maiani/figworks). LaTeX labels inside a sketch are
  typeset with [vectex](https://github.com/maiani/vectex), which compiles a
  snippet with `pdflatex` and `dvisvgm` into a placeable SVG group, so
  schematic math matches the manuscript's typography. Avoid hand-edited SVG.
- **3D scenes** — [VecView](https://github.com/maiani/vecview) scenes integrate
  directly with `panel.add(scene)`. Use `scene.plane()` plus
  `fig.fill_plane()` to embed plots in 3D, and `scene.slot()` plus
  `fig.fill_slot()` for upright VecTeX labels at fixed physical size. VecView
  is optional; add it with `pixi add --pypi vecview` when a figure needs it and
  include the updated manifest and lockfile in the same change.

---

## Requirements

The scripts need Python 3.12 or newer, `numpy`, `scipy`, `matplotlib`, and `sympy`, plus
[svg.py](https://github.com/orsinium-labs/svg),
[FigWorks](https://github.com/maiani/figworks), and
[vectex](https://github.com/maiani/vectex) for sketch panels. LaTeX labels
additionally need `pdflatex`, `dvisvgm`, and MuPDF's `mutool` on `PATH`.
FigWorks PDF/PNG export needs Cairo, fontconfig, and the chosen fonts
(TeX Gyre Heros by default). Install these system dependencies separately.

Use this repository's [Pixi](https://pixi.sh) environment for development and
reproduction. `pixi.toml` declares dependencies; `pixi.lock` records their
resolved versions across supported platforms. Keep both in version control.

For initial setup or an intentional dependency update:

```sh
pixi install
```

To reproduce the checked-in lockfile and generate a figure:

```sh
pixi install --locked
pixi run python plots/FigN-description.py
```

Notebook tooling is optional: use `pixi install -e notebooks` and
`pixi run -e notebooks jupyter lab`. Install TeX and fonts through your system;
document their versions for a release, since the lockfile does not capture them.

Private exploration in the project's `workspace/` uses the normal shell
Python unless an alternative is specified; shared code is verified here in Pixi.

---

## Reproducing the figures

Run figure scripts from this repository root with `pixi run python`.

Point vectex's cache at `plots/figures/.vectex-cache/` (via `cache_dir=` or
`VECTEX_CACHE_DIR`) so only the first run pays for LaTeX.

---

## Documenting reproducible results

As results are promoted, map each figure or analytic claim to its script and
shared model. Record the parameter set, expected output, and validation command.
Document approximate runtime for expensive calculations, including cold rebuilds.
If results are cached, record the generating command, relevant parameters and
code version, and how to rebuild or invalidate the cache. A cache must not be
the only surviving source of a result.

## Citation

If you use or adapt this code for related work, please cite the associated
manuscript and link back to this repository.
