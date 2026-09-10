# -*- coding: utf-8 -*-
"""Run the Zartman & Doe (1981) Version I model and print the growth history."""
from plumbotectonics.version1 import run

if __name__ == "__main__":
    hist, mantle, ups, los = run()
    print("t (Ga)  Mantle              Orogene             Upper               Lower")
    for h in hist:
        def fmt(d):
            if not d:
                return "-"
            return f"{d['206/204']:.2f}/{d['207/204']:.2f}/{d['208/204']:.2f}"
        print(f"{h['t']:.1f}  {fmt(h['mantle']):<19} {fmt(h['orogene']):<19} {fmt(h['upper']):<19} {fmt(h['lower'])}")
