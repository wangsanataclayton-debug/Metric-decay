"""Persistent homology wrappers. Falls back with clear DATA/LIB NOT AVAILABLE."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PersistenceResult:
    diagrams: list  # list of (birth, death) arrays per homology dim
    total_persistence: dict
    max_persistence: dict
    entropy: dict
    backend: str
    notes: str


def _entropy(pers: np.ndarray) -> float:
    lengths = pers[:, 1] - pers[:, 0]
    lengths = lengths[np.isfinite(lengths) & (lengths > 0)]
    if lengths.size == 0:
        return float("nan")
    p = lengths / lengths.sum()
    return float(-np.sum(p * np.log(p)))


def compute_persistence(X: np.ndarray, maxdim: int = 1, metric: str = "euclidean") -> PersistenceResult:
    """X: n_points x d. Vietoris–Rips via ripser if installed, else gudhi, else raise."""
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 4:
        raise ValueError("Need point cloud with n>=4")

    diagrams = []
    backend = "none"
    notes = ""

    try:
        from ripser import ripser

        out = ripser(X, maxdim=maxdim, metric=metric)
        diagrams = out["dgms"]
        backend = "ripser"
    except Exception:
        try:
            import gudhi as gd

            rips = gd.RipsComplex(points=X, max_edge_length=np.inf)
            st = rips.create_simplex_tree(max_dimension=maxdim + 1)
            st.compute_persistence()
            diagrams = [np.array(st.persistence_intervals_in_dimension(d)) for d in range(maxdim + 1)]
            backend = "gudhi"
        except Exception as e:
            raise RuntimeError(
                "LIB NOT AVAILABLE: install ripser or gudhi to compute persistence. "
                f"Detail: {e}"
            ) from e

    tot, mx, ent = {}, {}, {}
    for d, dg in enumerate(diagrams):
        dg = np.asarray(dg, dtype=float)
        if dg.size == 0:
            tot[d] = 0.0
            mx[d] = 0.0
            ent[d] = float("nan")
            continue
        finite = dg[np.isfinite(dg[:, 1])]
        lengths = finite[:, 1] - finite[:, 0] if finite.size else np.array([])
        tot[d] = float(np.sum(lengths)) if lengths.size else 0.0
        mx[d] = float(np.max(lengths)) if lengths.size else 0.0
        ent[d] = _entropy(finite) if finite.size else float("nan")

    return PersistenceResult(diagrams, tot, mx, ent, backend, notes)


def wasserstein_diagrams(dg1: np.ndarray, dg2: np.ndarray, order: float = 1.0) -> float:
    try:
        from persim import wasserstein
        return float(wasserstein(dg1, dg2, order=order))
    except Exception:
        try:
            import gudhi as gd
            return float(gd.wasserstein_distance(dg1, dg2, order=order))
        except Exception as e:
            raise RuntimeError(f"LIB NOT AVAILABLE for Wasserstein: {e}") from e
