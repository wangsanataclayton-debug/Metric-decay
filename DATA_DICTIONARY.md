# Data dictionary (empirical pipeline)

## Claim categories
FACT | EMPIRICAL RESULT | ESTIMATE | INFERENCE | HYPOTHESIS | THEORETICAL CLAIM | SYNTHETIC RESULT | LIMITATION

## Acquired / targeted sources

| Variable | Source | Direct/Proxy | Notes |
|----------|--------|--------------|-------|
| Mkt-RF, SMB, HML, RMW, CMA, RF | French Data Library | Direct | Daily/monthly factors |
| Momentum | French MOM | Direct | |
| Industry portfolio returns | French 49 Ind | Direct | Cross-section for ACH/dim |
| VIX | FRED VIXCLS (Cboe) | Direct | Cite Cboe/FRED |
| SOFR, EFFR, NFCI, STLFSI4 | FRED | Direct | Stress/liquidity controls |
| ETF OHLCV | Stooq `*.us` daily | Direct prices | Not historical index membership |
| LOB P/V levels | LOBSTER samples | Direct | Sample day only; not stress dates |
| Institutional weights | SEC 13F EDGAR | Proxy | Ingestion stub; LOW-FREQ PROXY |
| Sentiment / Sent_AI | — | DATA NOT AVAILABLE as AI signal | Replace with GDELT tone PROXY or omit |

## Derived research variables
- `spread`, `rel_spread`, `obi` — from LOB best/levels
- `avg_abs_corr`, `eff_rank`, `participation_ratio`, `pc1_share` — from return panels
- persistence / W1 / ORC — computed objects, not raw downloads

## Point cloud (minimal defensible)
Prefer: rolling asset features `[r, σ, β_mkt, volume_z]` or LOB vector `[Pbid(1:K), Vbid(1:K), Pask(1:K), Vask(1:K)]`.
Omit Sent_AI until an observable series is validated.
