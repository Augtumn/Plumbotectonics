# -*- coding: utf-8 -*-
"""Run the Zartman & Doe (1981) Version I model.

Prints the 11-cycle growth history and saves it as
``outputs/results/version1_history.csv``.

The output is a long table: one row per (cycle, reservoir, ratio), sharing the
``reservoir`` / ``ratio`` / ``model`` columns with ``version4_comparison.csv``.
"""
import csv
import os

from plumbotectonics.version1 import run

RESERVOIRS = ("mantle", "orogene", "upper", "lower")
RATIOS = ("206/204", "207/204", "208/204")
HEADER = ["cycle", "t_Ga", "reservoir", "ratio", "model"]


def _fmt(d):
    if not d:
        return "-"
    return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"


def history_rows(history):
    """Yield one row per (cycle, reservoir, ratio); skip absent reservoirs."""
    for index, entry in enumerate(history, start=1):
        for reservoir in RESERVOIRS:
            data = entry.get(reservoir)
            if not data:
                continue
            for ratio in RATIOS:
                yield [index, f"{entry['t']:.1f}", reservoir, ratio, f"{data[ratio]:.6f}"]


def main():
    history, _, _, _ = run()

    print("t (Ga)  Mantle              Orogene             Upper               Lower")
    for entry in history:
        print(
            f"{entry['t']:.1f}  {_fmt(entry['mantle']):<19} {_fmt(entry['orogene']):<19} "
            f"{_fmt(entry['upper']):<19} {_fmt(entry['lower'])}"
        )

    rows = list(history_rows(history))
    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "version1_history.csv")
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
