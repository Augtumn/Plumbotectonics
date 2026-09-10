# -*- coding: utf-8 -*-
"""Run the calibrated Version IV model and save a comparison table."""
import os
import pandas as pd
from plumbotectonics.version4 import run, ratios

TARGETS = {
    "mantle": [18.473, 15.482, 37.729, 10.006, 2.7276, 27.29188],
    "upper": [19.325, 15.727, 39.071, 11.077, 3.8833, 43.016],
    "lower": [17.623, 15.351, 38.753, 6.4903, 6.0518, 39.278],
    "sub": [18.318, 15.110, 38.101, 9.1292, 3.8932, 35.512],
}
KEYS = ["206/204", "207/204", "208/204", "238U/204Pb", "232Th/238U", "232Th/204Pb"]

if __name__ == "__main__":
    result = run(dp=0.14)
    rows = []
    for name, target in TARGETS.items():
        values = [ratios(result[name])[k] for k in KEYS]
        for key, value, tgt in zip(KEYS, values, target):
            rows.append({"reservoir": name, "ratio": key, "model": value, "table": tgt, "abs_diff": value - tgt})
    df = pd.DataFrame(rows)
    out = os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "version4_comparison.csv")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(df.to_string(index=False))
    print(f"\nSaved: {out}")
