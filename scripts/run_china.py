# -*- coding: utf-8 -*-
"""Run the Li et al. (2001) China model.

Prints the 11-cycle growth history, compares it against Table 3 and Table 4 of
Li et al. (2001) and writes ``outputs/results/china_comparison.csv``.

Note that Table 3 is NOT a reproduction target that this model meets: it is
printed to 0.01 while the model misses it by up to 0.62.  See docs/validation.md.
"""
import os

import numpy as np
import pandas as pd

from plumbotectonics.china import check_conservation, present_day, run

RESERVOIRS = ("mantle", "lower", "upper")
RATIOS = ("206/204", "207/204", "208/204")
COLUMNS = ["t_Ga", "reservoir", "ratio", "model", "literature", "abs_diff", "rel_error_pct"]

# Li et al. (2001) Table 3, one tuple per cycle, oldest first, holding
# (206Pb/204Pb, 207Pb/204Pb, 208Pb/204Pb) for each reservoir.
TABLE_3 = {
    "mantle": [
        (10.17, 12.07, 30.56), (11.21, 13.20, 31.34), (12.18, 13.95, 32.23),
        (13.06, 14.45, 33.01), (13.89, 14.78, 33.76), (14.66, 15.01, 34.49),
        (15.39, 15.17, 35.20), (16.09, 15.28, 35.90), (16.73, 15.35, 36.57),
        (17.34, 15.40, 37.23), (17.92, 15.44, 37.88),
    ],
    "lower": [
        (10.17, 12.07, 30.56), (10.67, 12.62, 31.17), (11.54, 13.40, 31.96),
        (12.38, 13.98, 32.77), (13.14, 14.36, 33.56), (13.86, 14.63, 34.34),
        (14.55, 14.84, 35.11), (15.22, 14.99, 35.87), (15.87, 15.11, 36.63),
        (16.50, 15.20, 37.39), (17.10, 15.27, 38.14),
    ],
    "upper": [
        (10.17, 12.07, 30.56), (11.44, 13.45, 31.55), (12.55, 14.26, 32.49),
        (13.61, 14.80, 33.44), (14.64, 15.16, 34.39), (15.66, 15.42, 35.35),
        (16.60, 15.57, 36.27), (17.46, 15.66, 37.16), (18.33, 15.72, 38.09),
        (19.13, 15.75, 38.98), (19.86, 15.75, 39.83),
    ],
}

# Li et al. (2001) Table 4, ordered (mantle, lower crust, upper crust)
TABLE_4 = {"238U/204Pb": (8.44, 5.63, 14.98), "Th/U": (3.60, 5.48, 3.47)}


def _finalise(frame):
    """Add absolute and percentage differences against the literature column."""
    model = frame["model"].to_numpy()
    literature = frame["literature"].to_numpy()
    frame["abs_diff"] = model - literature
    frame["rel_error_pct"] = np.abs((model - literature) / literature) * 100.0
    return frame[COLUMNS]


def comparison_frame(history, present):
    """One row per (cycle, reservoir, ratio) plus the six present-day values."""
    records = []
    for index, entry in enumerate(history):
        for reservoir in RESERVOIRS:
            data = entry.get(reservoir)
            if not data:
                # t = 4.0 Ga: no crust existed before the first orogeny, so the
                # paper lists the newly created layers, which are pure mantle
                # material and therefore carry the orogene ratio.
                data = entry["orogene"]
            for ratio, literature in zip(RATIOS, TABLE_3[reservoir][index]):
                records.append({
                    "t_Ga": entry["t"],
                    "reservoir": reservoir,
                    "ratio": ratio,
                    "model": data[ratio],
                    "literature": literature,
                })
    for quantity, values in TABLE_4.items():
        for reservoir, literature in zip(RESERVOIRS, values):
            records.append({
                "t_Ga": 0.0,
                "reservoir": reservoir,
                "ratio": quantity,
                "model": present[reservoir][quantity],
                "literature": literature,
            })
    return _finalise(pd.DataFrame(records))


def _fmt(d):
    if not d:
        return "-"
    return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"


def main():
    history, mantle, upper, lower = run()
    present = present_day(mantle, upper, lower)

    print("t (Ga)  Mantle              Orogene             Upper               Lower")
    for entry in history:
        print(
            f"{entry['t']:.1f}  {_fmt(entry['mantle']):<19} {_fmt(entry['orogene']):<19} "
            f"{_fmt(entry['upper']):<19} {_fmt(entry['lower'])}"
        )

    frame = comparison_frame(history, present)
    frame["model"] = frame["model"].round(6)
    frame["literature"] = frame["literature"].round(6)
    frame["abs_diff"] = frame["abs_diff"].round(6)
    frame["rel_error_pct"] = frame["rel_error_pct"].round(4)

    growth = frame[frame["ratio"].isin(RATIOS)]
    today = frame[~frame["ratio"].isin(RATIOS)]
    for label, part in (("Table 3 (growth curves)", growth),
                        ("Table 4 (present day)", today)):
        residual = part["model"].to_numpy() - part["literature"].to_numpy()
        print(
            f"\n{label}: rows = {len(part)}"
            f"   max |abs_diff| = {np.max(np.abs(residual)):.4f}"
            f"   mean |abs_diff| = {np.mean(np.abs(residual)):.4f}"
            f"   RMSE = {np.sqrt(np.mean(residual ** 2)):.4f}"
            f"   max |rel_error_pct| = {np.max(np.abs(part['rel_error_pct'].to_numpy())):.3f} %"
        )
    inside = np.abs(growth["abs_diff"].to_numpy()) <= 0.005
    print(f"Table 3 values inside the printed precision +-0.005: {inside.sum()} / {len(growth)}")

    last = history[-1]
    ordered = last["upper"]["206/204"] > last["mantle"]["206/204"] > last["lower"]["206/204"]
    print(f"qualitative ordering upper > mantle > lower: {ordered}"
          f"  ({last['upper']['206/204']:.2f} > {last['mantle']['206/204']:.2f}"
          f" > {last['lower']['206/204']:.2f})")
    print("conservation:", {k: f"{v:.1e}" for k, v in
                            check_conservation(mantle, upper, lower).items()})

    out = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "outputs", "results", "china_comparison.csv")
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    # lineterminator: .gitattributes pins eol=lf, and pandas would otherwise
    # write CRLF on Windows, so the working file would not match the blob
    frame.to_csv(out, index=False, encoding="utf-8-sig", lineterminator="\n")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
