# {{ PAPER_TITLE }}

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.0000000.svg)](https://doi.org/10.5281/zenodo.0000000)

Code accompanying the manuscript above. This repository contains the finalized,
reproducible scripts used to generate the paper's calculations, checks, and
figures.

---

## Repository structure

This is the planned public-code structure. Empty directories are created during
bootstrap so early projects have a stable place for finalized analytics and plot
scripts.

```
.
├── analytics/       self-contained checks and analytic verification scripts
├── plots/           model modules and figure-generation scripts
│   └── figures/     generated output (git-ignored; reproducible from scripts)
├── pixi.toml        reproducible environment
└── pixi.lock
```

### `analytics/`
Self-contained scripts that verify closed-form expressions, limiting cases, or
other analytic results quoted in the paper.

### `plots/`

- **Model modules** — shared implementations of the Hamiltonians and observables
  used by every figure.
- **Figure scripts** — one per manuscript figure. Outputs land in
  `plots/figures/`.

---

## Reproducing the figures

The environment is managed with [pixi](https://pixi.sh). From the repository
root:

```sh
pixi run python plots/FigN-description.py
```

---

## Citation

If you use or adapt this code for related work, please cite the associated
manuscript and link back to this repository.
