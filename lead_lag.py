"""Lead-lag estimation scaffold. Do NOT carry synthetic 220-tick claim into empirics."""
from __future__ import annotations

import numpy as np
import pandas as pd


def lead_lag_corr(signal: pd.Series, stress: pd.Series, tau_min: int = -500, tau_max: int = 500) -> pd.DataFrame:
    s = signal.align(stress, join="inner")
    x, y = s[0].to_numpy(dtype=float), s[1].to_numpy(dtype=float)
    rows = []
    for tau in range(tau_min, tau_max + 1):
        if tau < 0:
            a, b = x[-tau:], y[: len(y) + tau]
        elif tau > 0:
            a, b = x[: len(x) - tau], y[tau:]
        else:
            a, b = x, y
        if len(a) < 30 or np.std(a) == 0 or np.std(b) == 0:
            corr = np.nan
        else:
            corr = float(np.corrcoef(a, b)[0, 1])
        rows.append({"tau": tau, "corr": corr, "n": len(a)})
    out = pd.DataFrame(rows)
    return out
