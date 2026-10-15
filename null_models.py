"""Null models for topology vs conventional structure. SYNTHETIC labels when generating."""
from __future__ import annotations

import numpy as np


def null_volatility_only(returns: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Preserve column vols; destroy dependence (independent Gaussian). SYNTHETIC / METHOD VALIDATION ONLY."""
    vol = np.nanstd(returns, axis=0, ddof=1)
    vol = np.where(vol > 0, vol, 1.0)
    return rng.normal(0, 1, size=returns.shape) * vol


def null_correlation_only(returns: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Gaussian with empirical correlation (higher-order destroyed). SYNTHETIC / METHOD VALIDATION ONLY."""
    x = np.nan_to_num(returns, nan=0.0)
    x = (x - x.mean(0)) / (x.std(0, ddof=1) + 1e-12)
    c = np.corrcoef(x, rowvar=False)
    c = np.nan_to_num(c, nan=0.0)
    np.fill_diagonal(c, 1.0)
    # nearest PSD
    ev, evec = np.linalg.eigh(c)
    ev = np.clip(ev, 1e-8, None)
    c_psd = evec @ np.diag(ev) @ evec.T
    return rng.multivariate_normal(np.zeros(c_psd.shape[0]), c_psd, size=returns.shape[0])


def null_permutation(returns: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Shuffle time index. SYNTHETIC / METHOD VALIDATION ONLY."""
    out = returns.copy()
    idx = rng.permutation(out.shape[0])
    return out[idx]


def null_time_shift(returns: np.ndarray, rng: np.random.Generator, max_shift: int = 20) -> np.ndarray:
    """Independent circular shifts per column. SYNTHETIC / METHOD VALIDATION ONLY."""
    out = returns.copy()
    T = out.shape[0]
    for j in range(out.shape[1]):
        s = int(rng.integers(1, max_shift + 1))
        out[:, j] = np.roll(out[:, j], s)
    return out
