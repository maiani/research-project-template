# Figure guide

Read when creating or revising a figure. Paths below are relative to the project root.


- Avoid using title elements.
- Name figure output files with the manuscript figure number plus a descriptive
  slug, e.g. `Fig4-description.pdf` or `FigS2-description.pdf`.
- Name figure scripts in `repository/plots/` to match: `Fig4-description.py`,
  `FigS2-description.py`, etc.
- Figure scripts must generate SVG, PDF, and PNG outputs. Use the PNG for visual
  inspection.
- When a new figure from `repository/` is ready to be included in the manuscript,
  move its SVG to `manuscript/svg/` for the author's final touch-up in Inkscape
  before exporting it as a PDF. Keep the reproducible script and model code in
  `repository/`.
- Name model modules descriptively (e.g. `projected_model.py`, `observables.py`).
- Analytics scripts in `repository/analytics/` must be self-contained and end
  with `assert`-style checks against the closed-form results in the paper.
- Keep a common FigWorks `style.md` for the paper. Apply its Matplotlib
  settings with `matplotlib.rc_context(theme_rc(style_path))` to every plot
  and pass the same style to `figworks.Figure(theme=style_path)`.

### Sketches and schematics

- Build 2D sketches and schematics programmatically with
  [`svg.py`](https://github.com/orsinium-labs/svg) (`import svg`); use
  [VecView](https://github.com/maiani/vecview) for layered 3D scenes. Never
  hand-draw an SVG or edit a generated one by hand in `repository/`; the script
  is the source of truth and must be reproducible.
- Keep sketch scripts next to the other figure scripts in `repository/plots/`
  under the same naming convention (`Fig1-setup-sketch.py`), or as a reusable
  module when several figures share the same drawing.
- Assemble mixed figures with [FigWorks](https://github.com/maiani/figworks).
  Use `Figure.grid()` for named panels, `panel.subplots()` for Matplotlib
  axes, and `panel.add(mpl_fig, fit="axes")` for aligned plot frames. Add a
  schematic with `panel.add(str(canvas), id="setup")`. Use physical dimensions
  and leave space for axis labels; inspect the exported result.
- FigWorks accepts a `vecview.Scene` directly through `panel.add(scene,
  id="device-scene")`; it uses the shared `to_svg_document()` protocol.
  Keep the scene background transparent and padding small when the panel
  layout already provides margins.
- VecView also supports plots embedded in a 3D plane: reserve it with
  `scene.plane(..., id="plot-plane")`, add the scene, then call
  `fig.fill_plane("plot-plane", mpl_fig)`. Match the plane and plot aspect
  ratios and check orientation to avoid mirrored labels.
- For upright labels anchored to 3D points, reserve a `scene.slot(...)` and
  fill it after placement with `fig.fill_slot("label-id", fragment)`, using
  a VecTeX fragment. This keeps its physical font size instead of scaling
  the label with the geometry. `scene.with_camera(...)` reuses the same
  scene under another projection.
- VecView is an optional dependency, not installed by FigWorks itself. When
  shared figure code uses it, declare it in `repository/pixi.toml` and update
  the lockfile with Pixi. Follow the normal-shell dependency rule for private
  exploration.
- For insertion into an existing Matplotlib figure, use
  `figworks.compose({ax: str(canvas)}, fig=mpl_fig)`.
- Drive the sketch from the same quantities as the computed panels — a barrier
  length in the schematic should come from the model module, not from a
  hand-copied coordinate.
- Labels are easiest when placed on the hosting `Axes` with `ax.text(...,
  transform=ax.transAxes)`: they inherit the shared Matplotlib theme and stay
  editable text. When a label must live inside the drawing — rotated along an
  arrow, or scaled with a group — typeset it with
  [`vectex`](https://github.com/maiani/vectex), which compiles a LaTeX snippet
  (`pdflatex` → `dvisvgm`) into one portable SVG `<g>` fragment carrying the
  manuscript's own math typography. The fragment carries metadata for later editing with Inkscape's
  TexText extension:

  ```python
  import svg
  import vectex

  fragment = vectex.render(r"$\Delta_{\rm ind}$", size_pt=9)
  canvas.elements.append(
      svg.G(transform=[svg.Translate(60, 36)], elements=[fragment.to_svg_py()])
  )
  ```

  Position a fragment with an enclosing `svg.G` transform, using its `width_px`,
  `height_px`, and `baseline_px` in SVG coordinates; recolour it with `color=`
  at render time or CSS `color` on the enclosing group.
  Use `vectex.render_math()` for a bare expression and `vectex.render_many()`
  when a figure carries many labels, so they share one compiler invocation.
- `vectex` needs `pdflatex` and `dvisvgm` on `PATH`; with current
  Ghostscript, also install MuPDF's `mutool`. Minimal TeX installations may
  need additional packages. Enable its on-disk cache with `cache_dir=` or the
  `VECTEX_CACHE_DIR` environment variable — point it at
  `plots/figures/.vectex-cache/` — so only the first run pays for LaTeX.
- The composed SVG is the authoritative output; derive the PDF and PNG from it
  with `fig.save("figure.svg")`, `fig.save("figure.pdf")`, and
  `fig.save("figure.png", dpi=600)`. FigWorks uses CairoSVG for PDF/PNG;
  Inkscape can also export the composed SVG.
- Inkscape touch-up stays reserved for `manuscript/svg/`; upstream fixes belong
  in the sketch script.
- After generating or regenerating any panel, visually verify that text and
  graphical elements do not overlap, font sizes suit the target column width,
  and stacked or adjacent panels meet their alignment constraints.


## Provenance and interpretation

Use the shared model for quantitative figures. Label schematic illustrations as
schematic and record deliberate departures from computed values in their source
or caption. Preserve the editable master separately from delivery exports (for
example, live-text SVG for editing and an outlined SVG or PNG for the web).
