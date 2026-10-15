"""Correlation, PCA, effective rank, ACH measures — empirical only."""
from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_corr_stats(returns: pd.DataFrame, window: int) -> pd.DataFrame:
    """returns: T x N. Output time series of dependence summaries."""
    cols = ["avg_abs_corr", "median_corr", "corr_dispersion", "pc1_share",
            "eff_rank", "participation_ratio", "n_obs"]
    rows = []
    idx = []
    vals = returns.to_numpy(dtype=float)
    T, N = vals.shape
    for t in range(window - 1, T):
        block = vals[t - window + 1 : t + 1]
        if np.isnan(block).any():
            # drop incomplete columns for this window
            mask = ~np.isnan(block).any(axis=0)
            block = block[:, mask]
        if block.shape[1] < 3:
            continue
        c = np.corrcoef(block, rowvar=False)
        iu = np.triu_indices_from(c, k=1)
        pair = c[iu]
        # eigenvalues of corr
        ev = np.linalg.eigvalsh(c)
        ev = np.clip(ev[::-1], 0, None)  # desc
        s = ev.sum()
        p = ev / s if s > 0 else ev
        p = p[p > 0]
        rows.append({
            "avg_abs_corr": float(np.mean(np.abs(pair))),
            "median_corr": float(np.median(pair)),
            "corr_dispersion": float(np.std(pair)),
            "pc1_share": float(ev[0] / s) if s > 0 else np.nan,
            "eff_rank": float(np.exp(-np.sum(p * np.log(p)))),
            "participation_ratio": float((ev.sum() ** 2) / np.sum(ev ** 2)) if np.sum(ev ** 2) > 0 else np.nan,
            "n_obs": int(block.shape[0]),
        })
        idx.append(returns.index[t])
    return pd.DataFrame(rows, index=idx)


def ach_mean_abs_corr(signal_matrix: np.ndarray) -> float:
    """R_t = mean |corr| over pairs of columns (strategies/assets)."""
    c = np.corrcoef(signal_matrix, rowvar=False)
    iu = np.triu_indices_from(c, k=1)
    return float(np.mean(np.abs(c[iu])))
