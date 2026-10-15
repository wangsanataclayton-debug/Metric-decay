# Research gap report — what we can actually test

## Here is what we can actually test with the data available

### Testable now (daily frequency)
1. **Q1 (partial):** Effective dimensionality / common-factor concentration via French 49 industries + ETF returns (eff rank, participation ratio, PC1 share, ACH-style mean |corr|).
2. **Q2 (partial):** Topological/geometric decay on **daily** point clouds (asset or industry feature vectors) — persistence, W₁ on diagrams, rolling dependence — **not** tick LOB manifolds.
3. **Q3 (partial / weak):** Ollivier–Ricci on kNN graphs of daily cross-sections around stress dates in `stress_events.json`. **Cannot** test LOB-level curvature before Flash Crash without paid LOB.
4. **Q4 (partial):** Incremental information of topology vs VIX, pairwise corr, volume — daily only.

### Not testable with acquired data
- Tick/LOB metric decay on 2010-05-06, 2020-03, etc. → **DATA NOT AVAILABLE** freely.
- Historical S&P 500 membership panel → need WRDS/CRSP.
- True algorithmic strategy convergence → 13F is only a **LOW-FREQUENCY PROXY** (stub; bulk not downloaded).
- `Sent_AI` → **DATA NOT AVAILABLE**; omit or replace with validated text tone later.
- Claim of Ricci-flow singularities → flow not implemented (discrete ORC only).

### Methodological risks
- Daily topology may just proxy volatility/correlation (null models required).
- ETF survivorship / composition drift.
- Event dates are ex-post (look-ahead for “prediction” framing).
- Computational approximations (subsampling) must be documented when used.
