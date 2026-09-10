# -*- coding: utf-8 -*-
"""Publication-style plotting helpers for the plumbotectonics models."""
from __future__ import annotations

import os
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.unicode_minus"] = False

_RESERVOIRS = ["mantle", "upper", "lower", "sub", "orogene"]
_LABELS = {
    "mantle": "Mantle",
    "upper": "Upper crust",
    "lower": "Lower crust",
    "sub": "Subcrust",
    "orogene": "Orogene",
}
_COLORS = {
    "mantle": "#1f77b4",
    "upper": "#d62728",
    "lower": "#2ca02c",
    "sub": "#9467bd",
    "orogene": "#ff7f0e",
}
_MARKERS = {
    "mantle": "o",
    "upper": "s",
    "lower": "^",
    "sub": "D",
    "orogene": "x",
}


def _extract_version4_series(history: list[dict[str, Any]]) -> dict[str, dict[str, list[float]]]:
    series: dict[str, dict[str, list[float]]] = {}
    for name in _RESERVOIRS:
        xs, y207, y208, ts, u_pb = [], [], [], [], []
        for h in history:
            d = h.get(name)
            if not d or d.get("206/204") is None:
                continue
            xs.append(d["206/204"])
            y207.append(d["207/204"])
            y208.append(d["208/204"])
            ts.append(h["time_Ga"])
            u_pb.append(d["238U/204Pb"])
        series[name] = {"x": xs, "y207": y207, "y208": y208, "t": ts, "u_pb": u_pb}
    return series


def plot_version4_growth_curves(result: dict[str, Any], out_png: str, out_pdf: str | None = None) -> None:
    """Plot Version IV growth curves; returns the closed figure."""
    hist = result["history"]
    series = _extract_version4_series(hist)

    fig, axes = plt.subplots(2, 2, figsize=(13, 11), constrained_layout=True)

    # A: 206/204 vs 207/204
    ax = axes[0, 0]
    for name in _RESERVOIRS:
        s = series[name]
        if s["x"]:
            ax.plot(s["x"], s["y207"], marker=_MARKERS[name], ms=4, lw=1.5,
                    color=_COLORS[name], label=_LABELS[name])
    ax.set_xlabel("206Pb/204Pb")
    ax.set_ylabel("207Pb/204Pb")
    ax.set_title("(A) 207Pb/204Pb vs 206Pb/204Pb growth curve")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    # B: 206/204 vs 208/204
    ax = axes[0, 1]
    for name in _RESERVOIRS:
        s = series[name]
        if s["x"]:
            ax.plot(s["x"], s["y208"], marker=_MARKERS[name], ms=4, lw=1.5,
                    color=_COLORS[name], label=_LABELS[name])
    ax.set_xlabel("206Pb/204Pb")
    ax.set_ylabel("208Pb/204Pb")
    ax.set_title("(B) 208Pb/204Pb vs 206Pb/204Pb growth curve")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    # C: 206/204 vs time
    ax = axes[1, 0]
    for name in _RESERVOIRS:
        s = series[name]
        if s["t"]:
            ax.plot(s["t"], s["x"], marker=_MARKERS[name], ms=4, lw=1.5,
                    color=_COLORS[name], label=_LABELS[name])
    ax.set_xlabel("Time (Ga)")
    ax.set_ylabel("206Pb/204Pb")
    ax.set_title("(C) 206Pb/204Pb vs time")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    # D: 238U/204Pb vs time
    ax = axes[1, 1]
    for name in _RESERVOIRS:
        s = series[name]
        if s["t"]:
            ax.plot(s["t"], s["u_pb"], marker=_MARKERS[name], ms=4, lw=1.5,
                    color=_COLORS[name], label=_LABELS[name])
    ax.set_xlabel("Time (Ga)")
    ax.set_ylabel("238U/204Pb")
    ax.set_title("(D) 238U/204Pb vs time")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    fig.suptitle("Plumbotectonics Version IV growth curves (Haines & Zartman, 1988)", fontsize=15)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    if out_pdf:
        os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
        fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    return fig


def plot_version1_growth_curves(history: list[dict[str, Any]], out_png: str, out_pdf: str | None = None) -> None:
    """Plot Version I growth curves; returns the closed figure."""
    names = ["mantle", "orogene", "upper", "lower"]
    labels = {"mantle": "Mantle", "orogene": "Orogene", "upper": "Upper crust", "lower": "Lower crust"}
    colors = {"mantle": "#1f77b4", "orogene": "#ff7f0e", "upper": "#d62728", "lower": "#2ca02c"}
    markers = {"mantle": "o", "orogene": "x", "upper": "s", "lower": "^"}

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)

    ax = axes[0]
    for name in names:
        xs, ys = [], []
        for h in history:
            d = h.get(name)
            if d:
                xs.append(d["206/204"])
                ys.append(d["207/204"])
        if xs:
            ax.plot(xs, ys, marker=markers[name], ms=4, color=colors[name], label=labels[name])
    ax.set_xlabel("206Pb/204Pb")
    ax.set_ylabel("207Pb/204Pb")
    ax.set_title("(A) 207Pb/204Pb–206Pb/204Pb")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[1]
    for name in names:
        xs, ys = [], []
        for h in history:
            d = h.get(name)
            if d:
                xs.append(d["206/204"])
                ys.append(d["208/204"])
        if xs:
            ax.plot(xs, ys, marker=markers[name], ms=4, color=colors[name], label=labels[name])
    ax.set_xlabel("206Pb/204Pb")
    ax.set_ylabel("208Pb/204Pb")
    ax.set_title("(B) 208Pb/204Pb–206Pb/204Pb")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[2]
    for name in names:
        xs, ys = [], []
        for h in history:
            d = h.get(name)
            if d:
                xs.append(h["t"])
                ys.append(d["206/204"])
        if xs:
            ax.plot(xs, ys, marker=markers[name], ms=4, color=colors[name], label=labels[name])
    ax.set_xlabel("Time (Ga)")
    ax.set_ylabel("206Pb/204Pb")
    ax.set_title("(C) 206Pb/204Pb vs time")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    fig.suptitle("Plumbotectonics Version I growth curves (Zartman & Doe, 1981)", fontsize=15)
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    fig.savefig(out_png, dpi=600, bbox_inches="tight")
    if out_pdf:
        os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
        fig.savefig(out_pdf, bbox_inches="tight")
    plt.close(fig)
    return fig
