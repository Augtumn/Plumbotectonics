# -*- coding: utf-8 -*-
"""Run the Zartman & Doe (1981) Version I model.

Prints the 11-cycle growth history and saves it as
``outputs/results/version1_history.csv``.
"""
import csv
import os

from plumbotectonics.version1 import run

RESERVOIRS = ("mantle", "orogene", "upper", "lower")
RATIOS = ("206/204", "207/204", "208/204")
HEADER = ["cycle", "t_Ga"] + [
    f"{reservoir}_{ratio}" for reservoir in RESERVOIRS for ratio in RATIOS
]


def _fmt(d):
    if not d:
        return "-"
    return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"


def _csv_row(index, entry):
    row = [index + 1, f"{entry['t']:.1f}"]
    for reservoir in RESERVOIRS:
        data = entry.get(reservoir)
        for ratio in RATIOS:
            row.append("" if not data else f"{data[ratio]:.4f}")
    return row


def main():
    history, _, _, _ = run()

    print("t (Ga)  Mantle              Orogene             Upper               Lower")
    for entry in history:
        print(
            f"{entry['t']:.1f}  {_fmt(entry['mantle']):<19} {_fmt(entry['orogene']):<19} "
            f"{_fmt(entry['upper']):<19} {_fmt(entry['lower'])}"
        )

    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "version1_history.csv")
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        for index, entry in enumerate(history):
            writer.writerow(_csv_row(index, entry))
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
