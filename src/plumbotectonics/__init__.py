# -*- coding: utf-8 -*-
"""Plumbotectonics models in Python.

This package contains:

- ``version1``: the Zartman & Doe (1981) Version I model.
- ``version4``: the Haines & Zartman (1988) Version IV model.
- ``china``: the Li et al. (2001) regional model for continental China, which
  reuses the Version I algorithm with the paper's own Table 1 and Table 2.
- ``plotting``: publication-style growth-curve plots.
"""

from . import constants  # noqa: F401
from .version1 import run as run_version1  # noqa: F401
from .version4 import run as run_version4, ratios as v4_ratios  # noqa: F401
from . import china  # noqa: F401

__all__ = ["constants", "run_version1", "run_version4", "v4_ratios", "china"]
