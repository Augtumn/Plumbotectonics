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
