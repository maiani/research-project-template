# Figures in a research project

Use the project's existing generators, scientific model, data, and style. Keep
private exploration in workspace/ and promote shared generators only when the
author approves. Create figure and output directories only when needed.

## Use FigWorks' own skill

For figure authoring, follow the `figworks` skill shipped with the installed
FigWorks version. Find it without installing another copy:

```sh
python -m figworks.skill path
```

Read SKILL.md in the returned folder and only the relevant references. This keeps
composition, rendering, preflight, and environment guidance with its library.
If skill discovery is wanted, register it once in the agent's configured skill
directory with `python -m figworks.skill install DESTINATION`, where DESTINATION
is the complete target folder ending in `figworks`. Preserve local customizations;
do not overwrite another skill automatically.

If FigWorks is unavailable or an older version lacks the skill command, check
its matching documentation and the project's environment choices. Do not upgrade
a published codebase merely to match a new example. FigWorks is optional for
kit installation and adoption; install figure tools when figure work needs them.

## Research-specific conventions

- Keep one authoritative model; do not hand-copy parameters into figure scripts.
  Distinguish computed results, measured data, and illustrative schematics.
- Use manuscript-numbered names when numbering is established and stable element
  IDs across revisions. Keep theme choices in the project's style.md.
- Retain editable SVG and the generator. Export requested delivery formats and a
  PNG preview; inspect the rendering and report any outstanding visual review.
- Run FigWorks preflight for the intended export. Review warnings and unchecked
  features as well as errors; passing preflight is not a scientific validation.
- Record source data, commands, and relevant versions with important figures.
  Lock codebase dependencies at release preparation, not for every sketch.
- Keep manual Inkscape touch-up distinct from generated output, with provenance
  in manuscript/svg/ when used. Fix reusable problems in the generator.
- Use Matplotlib's object-oriented API: call methods on `Figure` and `Axes`
  instances (`ax.plot()`, `ax.set_xlabel()`, `fig.savefig()`). The only accepted
  `plt.*` calls are `plt.figure()`, `plt.subplots()`, `plt.style.use()`, and
  `plt.rcParams` reads; never use stateful calls such as `plt.plot()`.

FigWorks composes Matplotlib plots, VecTeX equations, VecView geometry, and
VecWire circuits as needed. Let its package declare required dependencies; add
optional producers only when used. System TeX, fonts, and rendering libraries
remain separate requirements documented by its environment reference.
