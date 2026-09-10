# -*- coding: utf-8 -*-
"""Generate Version I and Version IV growth-curve figures."""
import os
from plumbotectonics.version1 import run as run_v1
from plumbotectonics.version4 import run as run_v4
from plumbotectonics.plotting import plot_version1_growth_curves, plot_version4_growth_curves

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG = os.path.join(BASE, "outputs", "figures")

if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    hist1, _, _, _ = run_v1()
    plot_version1_growth_curves(
        hist1,
        os.path.join(FIG, "version1_growth_curves.png"),
        os.path.join(FIG, "version1_growth_curves.pdf"),
    )
    result4 = run_v4(dp=0.14)
    plot_version4_growth_curves(
        result4,
        os.path.join(FIG, "version4_growth_curves.png"),
        os.path.join(FIG, "version4_growth_curves.pdf"),
    )
    print("Figures written to", FIG)
