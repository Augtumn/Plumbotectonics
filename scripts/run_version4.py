# -*- coding: utf-8 -*-
"""Run the calibrated Haines & Zartman (1988) Version IV model.

Prints the comparison against Table 4 and saves it as
``outputs/results/version4_comparison.csv``.

The output is a long table: one row per (reservoir, ratio), sharing the
``reservoir`` / ``ratio`` / ``model`` columns with ``version1_history.csv``.
"""
import csv
import os

from plumbotectonics.version4 import run, ratios

TARGETS = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper": [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower": [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub": [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]
HEADER = ["reservoir", "ratio", "model", "table", "abs_diff"]


def comparison_rows(result):
    """Yield one row per (reservoir, ratio)."""
    for name, target in TARGETS.items():
        values = [ratios(result[name])[key] for key in KEYS]
        for key, value, expected in zip(KEYS, values, target):
            yield [name, key, f"{value:.6f}", f"{expected:.6f}", f"{value - expected:.9f}"]


def main():
    rows = list(comparison_rows(run(dp=0.14)))

    print(f"{'reservoir':<9} {'ratio':<12} {'model':>11} {'table':>11} {'abs_diff':>13}")
    for row in rows:
        print(f"{row[0]:<9} {row[1]:<12} {row[2]:>11} {row[3]:>11} {row[4]:>13}")
    print(f"\nmax |abs_diff| = {max(abs(float(r[4])) for r in rows):.6f}")

    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "version4_comparison.csv")
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADER)
        writer.writerows(rows)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
