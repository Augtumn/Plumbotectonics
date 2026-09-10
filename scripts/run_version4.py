# -*- coding: utf-8 -*-
"""Run the calibrated Haines & Zartman (1988) Version IV model.

Prints the comparison against Table 4 of Haines & Zartman (1988) and writes
``outputs/results/version4_comparison.csv`` with the same schema as
``version1_comparison.csv``.
"""
import os

import numpy as np
import pandas as pd

from plumbotectonics.version4 import run, ratios

RESERVOIRS = ("mantle", "upper", "lower", "sub")
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]
COLUMNS = ["t_Ga", "reservoir", "ratio", "model", "literature", "abs_diff", "rel_error_pct"]

# Haines & Zartman (1988), Table 4: ending isotopic ratios for the major
# reservoirs, in the order of KEYS.
TABLE_4 = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper": [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower": [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub": [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}


def _finalise(frame):
    """Add absolute and percentage differences against the literature column."""
    model = frame["model"].to_numpy()
    literature = frame["literature"].to_numpy()
    frame["abs_diff"] = model - literature
    frame["rel_error_pct"] = np.abs((model - literature) / literature) * 100.0
    return frame[COLUMNS]


def comparison_frame(result):
    """One row per (reservoir, ratio) at the present day."""
    records = []
    for reservoir in RESERVOIRS:
        values = ratios(result[reservoir])
        for key, literature in zip(KEYS, TABLE_4[reservoir]):
            records.append({
                "t_Ga": 0.0,
                "reservoir": reservoir,
                "ratio": key,
                "model": values[key],
                "literature": literature,
            })
    return _finalise(pd.DataFrame(records))


def main():
    frame = comparison_frame(run(dp=0.14))
    frame["model"] = frame["model"].round(6)
    frame["literature"] = frame["literature"].round(6)
    frame["abs_diff"] = frame["abs_diff"].round(6)
    frame["rel_error_pct"] = frame["rel_error_pct"].round(4)

    residual = frame["model"].to_numpy() - frame["literature"].to_numpy()
    print(frame.to_string(index=False))
    print(
        f"\nrows = {len(frame)}   max |abs_diff| = {np.max(np.abs(residual)):.6f}"
        f"   max |rel_error_pct| = {np.max(np.abs(frame['rel_error_pct'].to_numpy())):.4f} %"
        f"   RMSE = {np.sqrt(np.mean(residual ** 2)):.6f}"
    )

    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "version4_comparison.csv")
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    frame.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
