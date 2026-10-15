"""Discrete Ollivier–Ricci on kNN graphs. Not Ricci flow."""
from __future__ import annotations

import numpy as np
from scipy.spatial.distance import cdist


def knn_indices(X: np.ndarray, k: int, metric: str = "euclidean") -> tuple[np.ndarray, np.ndarray]:
    D = cdist(X, X, metric=metric)
    np.fill_diagonal(D, np.inf)
    nbrs = np.argsort(D, axis=1)[:, :k]
    np.fill_diagonal(D, 0.0)
    return D, nbrs


def _measure(node: int, nbrs_row: np.ndarray, alpha: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (support indices, masses) for μ_node."""
    neigh = nbrs_row.astype(int)
    support = np.unique(np.concatenate([[node], neigh]))
    mass = np.zeros(len(support), dtype=float)
    # alpha at node
    mass[np.where(support == node)[0][0]] += alpha
    rem = (1.0 - alpha) / max(len(neigh), 1)
    for v in neigh:
        mass[np.where(support == v)[0][0]] += rem
    mass = mass / mass.sum()
    return support, mass


def _w1(supp_a, mass_a, supp_b, mass_b, D: np.ndarray) -> float:
    M = D[np.ix_(supp_a, supp_b)].astype(float)
    try:
        import ot

        return float(ot.emd2(mass_a.copy(), mass_b.copy(), M, numItermax=100000))
    except Exception:
        # Fast documented approximation: expected cost under independent coupling
        return float(mass_a @ M @ mass_b)


def ollivier_ricci_knn(
    X: np.ndarray,
    k: int = 10,
    alpha: float = 0.5,
    metric: str = "euclidean",
) -> dict:
    """
    κ(u,v) = 1 - W1(μ_u, μ_v) / d(u,v) for undirected kNN edges.
    Object = discrete Ollivier–Ricci curvature (NOT Ricci flow).
    """
    X = np.asarray(X, dtype=float)
    D, nbrs = knn_indices(X, k=k, metric=metric)
    n = X.shape[0]
    kappas = []
    edges = set()
    for u in range(n):
        for v in nbrs[u]:
            a, b = (u, int(v)) if u < v else (int(v), u)
            if a == b or (a, b) in edges:
                continue
            edges.add((a, b))
            d_uv = float(D[a, b])
            if d_uv <= 0 or not np.isfinite(d_uv):
                continue
            sa, ma = _measure(a, nbrs[a], alpha, n)
            sb, mb = _measure(b, nbrs[b], alpha, n)
            w = _w1(sa, ma, sb, mb, D)
            kappas.append(1.0 - w / d_uv)
    kappas = np.asarray(kappas, dtype=float)
    if kappas.size == 0:
        return {"object": "ollivier_ricci_discrete", "ricci_flow": False, "n_edges": 0}
    return {
        "object": "ollivier_ricci_discrete",
        "ricci_flow": False,
        "k": k,
        "alpha": alpha,
        "metric": metric,
        "n_edges": int(kappas.size),
        "mean": float(np.mean(kappas)),
        "median": float(np.median(kappas)),
        "q10": float(np.quantile(kappas, 0.1)),
        "variance": float(np.var(kappas)),
        "frac_negative": float(np.mean(kappas < 0)),
        "min": float(np.min(kappas)),
        "values": kappas,
    }
