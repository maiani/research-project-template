"""Exercise the documented figure stack; outputs go to the supplied directory.

Run with an existing Python environment containing the plotting dependencies:
    python tests/smoke-figures.py /tmp/research-figure-smoke
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import numpy as np
import svg
import vectex
from figworks import Figure, compose
from figworks.matplotlib import theme_rc
from lxml import etree

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
style = out / "style.md"
style.write_text("---\nbase: aps\n---\n\n# Common figure style\n")
with matplotlib.rc_context(theme_rc(style)):
    fig = Figure(width="178mm", height="65mm", theme=style)
    panels = fig.grid([["setup", "signal"]], margins=("8mm", "5mm", "12mm", "12mm"), gap="20mm")
    fragment = vectex.render(r"$\Delta_{\rm ind}$", size_pt=9, cache_dir=out / ".vectex-cache")
    canvas = svg.SVG(width=200, height=120, viewBox="0 0 200 120", elements=[
        svg.Rect(x=20, y=25, width=160, height=70, rx=8, fill="#dceaf5", stroke="#24486c"),
        svg.G(transform=[svg.Translate(80, 62)], elements=[fragment.to_svg_py()]),
    ])
    panels["setup"].add(str(canvas), id="setup-sketch")
    mpl_fig, ax = panels["signal"].subplots()
    phase = np.linspace(0, 2 * np.pi, 200)
    ax.plot(phase, np.cos(phase))
    ax.set_xlabel(r"$\phi$ (rad)")
    ax.set_ylabel(r"$\cos\phi$")
    panels["signal"].add(mpl_fig, id="signal-plot", fit="axes")
    for label, panel in zip("ab", panels.values(), strict=True):
        fig.label(label, panel.nw)
    for suffix in ("svg", "pdf", "png"):
        fig.save(out / f"composition.{suffix}")
    fig.save(out / "repeat.svg")
    assert (out / "composition.svg").read_bytes() == (out / "repeat.svg").read_bytes()
    tree = etree.parse(out / "composition.svg")
    for element_id in ("setup-sketch", "signal-plot"):
        assert tree.xpath("//*[@id=$value]", value=element_id)
    bridge = compose({ax: str(canvas)}, fig=mpl_fig)
    etree.fromstring(bridge.encode())
    assert (out / "composition.pdf").read_bytes().startswith(b"%PDF")
    assert (out / "composition.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
print(f"Figure smoke test passed: {out}")
