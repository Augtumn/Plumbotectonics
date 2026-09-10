# -*- coding: utf-8 -*-
"""Layout regression tests for the publication figures.

The suptitle used to be pinned at ``y=1.02`` while ``constrained_layout`` was
active, which pushed it out of the canvas and made it overlap the middle panel
title of the Version I figure. These tests pin the geometry.
"""
import os
import tempfile

import matplotlib
matplotlib.use("Agg")

from matplotlib.backends.backend_agg import FigureCanvasAgg

from plumbotectonics.plotting import (
    plot_version1_growth_curves,
    plot_version4_growth_curves,
)
from plumbotectonics.version1 import run as run_v1
from plumbotectonics.version4 import run as run_v4


def _assert_layout(fig, name):
    # plt.close() downgrades the canvas to FigureCanvasBase, which has no
    # get_renderer(); re-attach an Agg canvas to measure the layout.
    FigureCanvasAgg(fig)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    suptitle = fig._suptitle
    assert suptitle is not None, name + ": missing suptitle"
    box = suptitle.get_window_extent(renderer)
    canvas = fig.get_window_extent(renderer)
    assert box.y1 <= canvas.y1 + 0.5, "%s: suptitle above canvas (%.1f > %.1f)" % (name, box.y1, canvas.y1)
    assert box.y0 >= canvas.y0 - 0.5, "%s: suptitle below canvas" % name
    assert box.x0 >= canvas.x0 - 0.5, "%s: suptitle clipped on the left" % name
    assert box.x1 <= canvas.x1 + 0.5, "%s: suptitle clipped on the right (%.1f > %.1f)" % (name, box.x1, canvas.x1)
    for index, ax in enumerate(fig.axes):
        title = ax.title.get_window_extent(renderer)
        assert not box.overlaps(title), "%s: suptitle overlaps axes[%d] title" % (name, index)


def _tmp_png(name):
    return os.path.join(tempfile.mkdtemp(), name)


def test_version1_figure_layout():
    out = _tmp_png("v1.png")
    history, _, _, _ = run_v1()
    fig = plot_version1_growth_curves(history, out)
    _assert_layout(fig, "version1")
    assert os.path.getsize(out) > 0


def test_version4_figure_layout():
    out = _tmp_png("v4.png")
    result = run_v4(dp=0.14)
    fig = plot_version4_growth_curves(result, out)
    _assert_layout(fig, "version4")
    assert os.path.getsize(out) > 0


def test_pdf_has_no_creation_timestamp():
    """The PDFs must stay byte-reproducible (docs/correctness.md section 6).

    matplotlib stamps ``/CreationDate`` with the wall-clock time unless it is
    explicitly cleared, which made the committed PDF figures differ on every
    regeneration.  The earlier layout tests only ever wrote a PNG, so nothing
    covered the PDF path.
    """
    directory = tempfile.mkdtemp()
    png = os.path.join(directory, "v1.png")
    pdf = os.path.join(directory, "v1.pdf")

    history, _, _, _ = run_v1()
    plot_version1_growth_curves(history, png, pdf)

    with open(pdf, "rb") as handle:
        raw = handle.read()
    assert raw.startswith(b"%PDF-"), "not a PDF"
    assert b"/CreationDate" not in raw, "PDF embeds a wall-clock timestamp"
    assert b"/ModDate" not in raw, "PDF embeds a modification timestamp"

    result = run_v4(dp=0.14)
    plot_version4_growth_curves(result, png, pdf)
    with open(pdf, "rb") as handle:
        assert b"/CreationDate" not in handle.read()
