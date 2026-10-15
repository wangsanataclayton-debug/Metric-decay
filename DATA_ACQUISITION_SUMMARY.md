# DATA ACQUISITION SUMMARY

## Successfully acquired
- Kenneth French: FF5/FF3 daily, MOM daily, FF5 monthly, 49 Industry Portfolios daily → processed panels
- FRED: VIXCLS, SP500, DTWEXBGS, SOFR, EFFR, TEDRATE, NFCI, STLFSI4
- Yahoo Finance daily OHLCV: SPY/QQQ/IWM/DIA/sector ETFs/GME/AMC (2007–2024)
- **FI-2010 LOB** via DeepLOB mirror (Nordic, June 2010, 10-level features) → `data/raw/fi2010`, processed sample with spread/OBI/depth
- GDELT GKG latest dump → tone PROXY sample (`gdelt_tone_proxy_sample.csv`)
- Stress event database + rolling dependence (ind49 & ETF)
- Monthly topology/ORC/W1 series on industry point clouds + figures/tables
- FI-2010 LOB geometry probe (persistence + discrete ORC)

## Acquired with limitations
- Yahoo ETF panel ≠ CRSP historical constituents
- FI-2010 is Nordic June 2010 — **not** US Flash Crash / COVID microstructures
- GDELT tone is a **PROXY**, not manuscript `Sent_AI`
- Topology series uses documented approximations (monthly sampling, ≤25 landmarks)

## Could not acquire
- LOBSTER usable files via automated URL (HTML stubs) — manual download still required for NASDAQ samples
- Stooq (JS bot wall)
- Full LOB on US stress-event days; WRDS/CRSP; OptionMetrics; bulk 13F (stub only)

## Best high-frequency / LOB dataset obtained
- **FI-2010** (DIRECTLY_USABLE for LOB method tests). Best US LOB path remains manual LOBSTER samples + academic subscription for event days.

## Best cross-sectional dataset
- **French 49 Industry Portfolios (daily)**

## Best institutional-convergence dataset
- **SEC 13F stub only** (EDGAR public; bulk not ingested)

## Best event-study datasets
- Daily: French industries + Yahoo + VIX/FRED around curated events
- LOB geometry: FI-2010 (method), not matched to US event calendar

## Variables still missing
- US stress-day bid/ask depth; historical index membership; bulk 13F weights; option surfaces; validated long AI-sentiment history

## Empirical hypotheses now testable
- Daily eff-dimension / ACH-style corr vs stress (event studies produced)
- Daily discrete ORC / persistence / W1 on industry clouds (series + figs)
- LOB-state topology on FI-2010 (real LOB, non-US)
- Incremental prediction vs VIX (expanding-window OLS run)
- Null models for mean |corr|

## First-pass empirical notes (ESTIMATE / EMPIRICAL RESULT — not manuscript claims)
- Event-study eff_rank falls into stress for several crises (see `fig10_event_effrank.png`) — requires null-model confirmation before interpretation
- Expanding-window models: adding `eff_rank` did **not** raise OOS R² for VIX vs PC1/corr alone (`table08_predictive.json`) — topology daily features may be redundant with conventional dependence at this horizon
- FI-2010 LOB ORC mean ≈ 0.28 over probed windows (`fi2010_lob_topology_summary.json`)

## Hypotheses still requiring data
- US tick/LOB metric decay before Flash Crash-class events
- Algorithmic strategy homogenisation beyond industry/ETF proxies
- True Sent_AI channel

## Major methodological risks
- Daily topology ≈ correlation/vol channel (nulls mandatory)
- Approximations in TDA/ORC sampling
- Ex-post event labels; ETF survivorship; FI-2010 market mismatch
- Discrete ORC ≠ Ricci flow
