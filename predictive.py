"""Predictive regression scaffolds — incremental info tests vs conventional vars."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import roc_auc_score, r2_score


def aligned_design(df: pd.DataFrame, y_col: str, x_cols: list[str], h: int = 1):
    y = df[y_col].shift(-h)
    X = df[x_cols]
    d = pd.concat([y, X], axis=1).dropna()
    return d.iloc[:, 0], d.iloc[:, 1:]


def ols_predict(df, y_col, x_cols, h=1):
    y, X = aligned_design(df, y_col, x_cols, h)
    # expanding-window OOS (no random split)
    preds = np.full(len(y), np.nan)
    min_train = max(100, 5 * len(x_cols))
    for t in range(min_train, len(y)):
        model = LinearRegression().fit(X.iloc[:t], y.iloc[:t])
        preds[t] = model.predict(X.iloc[[t]])[0]
    mask = ~np.isnan(preds)
    return {"r2_oos": float(r2_score(y.to_numpy()[mask], preds[mask])) if mask.sum() > 10 else np.nan, "n": int(mask.sum())}


def logit_event(df, event_col, x_cols, h=5):
    # event_col: 1 if stress within next h days already encoded, or build from binary
    y, X = aligned_design(df, event_col, x_cols, h=0)
    if y.nunique() < 2:
        return {"auc": np.nan, "note": "need both classes"}
    preds = np.full(len(y), np.nan)
    min_train = max(100, 5 * len(x_cols))
    for t in range(min_train, len(y)):
        if y.iloc[:t].nunique() < 2:
            continue
        model = LogisticRegression(max_iter=200).fit(X.iloc[:t], y.iloc[:t])
        preds[t] = model.predict_proba(X.iloc[[t]])[0, 1]
    mask = ~np.isnan(preds)
    return {"auc": float(roc_auc_score(y.to_numpy()[mask], preds[mask])) if mask.sum() > 10 else np.nan}
