# {{ PAPER_TITLE }}

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.0000000.svg)](https://doi.org/10.5281/zenodo.0000000)

Code accompanying the manuscript above. The repository contains symbolic-verification
scripts for the key algebraic results and the figure-generation pipeline for all
main-text and supplemental panels.

---

## Repository structure

```
.
├── analytics/       SymPy verification of analytic results
├── plots/           model modules and figure-generation scripts
│   └── figures/     generated output (git-ignored; reproducible from scripts)
├── pixi.toml        reproducible environment
└── pixi.lock
```

### `analytics/`
SymPy scripts that verify the closed-form expressions quoted in the paper.

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
