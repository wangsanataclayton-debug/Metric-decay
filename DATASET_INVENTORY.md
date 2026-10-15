# Dataset inventory

| Dataset | Provider | Frequency | Period | Variables | Cost | Access | Original source | Suitability |
|---------|----------|-----------|--------|-----------|------|--------|-----------------|-------------|
| French FF5/FF3/MOM | Ken French | daily/monthly | 1963+/1926+ | factors, RF | Free | Downloaded | French Data Library | DIRECTLY_USABLE |
| French 49 Industries | Ken French | daily | 1926–2026-08 | industry returns | Free | Downloaded | French Data Library | DIRECTLY_USABLE |
| FRED VIXCLS et al. | FRED/Cboe/Fed | daily/weekly | series-dependent | VIX, stress, rates | Free | Downloaded | FRED | DIRECTLY_USABLE |
| Yahoo ETF/equity OHLCV | Yahoo | daily | 2007–2024 | OHLCV | Free | Downloaded | Yahoo Finance | USABLE_WITH_TRANSFORM |
| Stress events | Curated | event | 2007–2021 | dates/windows | Free | In-repo | SEC/CFTC/Fed/papers | USABLE_WITH_TRANSFORM |
| LOBSTER samples | LOBSTER | event-time | sample day | LOB levels | Free sample / paid full | Auto failed | NASDAQ ITCH via LOBSTER | INSUFFICIENT (auto); manual still possible |
| Stooq ETF | Stooq | daily | — | OHLCV | Free | Blocked | Stooq | INSUFFICIENT |
| SEC 13F | SEC EDGAR | quarterly | historical | holdings | Free | Stub only | SEC | PROXY / not bulk-downloaded |
| FI-2010 | Ntakaris et al. | LOB snapshots | Jun 2010 Nordic | 10-level LOB | Free academic | Not downloaded this pass | Helsinki/NASDAQ Nordic | USABLE_WITH_TRANSFORM if fetched |
| CRSP/WRDS constituents | WRDS | daily | — | membership | Subscription | INACCESSIBLE here | CRSP | INACCESSIBLE |
| Sent_AI | — | — | — | — | — | — | — | DATA NOT AVAILABLE |

See also `docs/DATA_AVAILABILITY_MATRIX.csv` and `data_manifest.json`.
