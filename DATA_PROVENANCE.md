# Data provenance

| Dataset | Provider | URL | Access date (UTC) | License / terms |
|---------|----------|-----|-------------------|-----------------|
| French FF3/FF5/MOM + 49 industries | Kenneth R. French Data Library | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | see `data_manifest.json` | Free research use; cite library |
| VIXCLS, SP500, SOFR, EFFR, NFCI, STLFSI4, TEDRATE, DTWEXBGS | FRED (St. Louis Fed); VIX underlying Cboe | https://fred.stlouisfed.org/ | see manifest | Cite FRED/Cboe; copyrighted series restrictions |
| ETF/equity OHLCV | Yahoo Finance via `yfinance` | https://finance.yahoo.com/ | see `data/metadata/yahoo_etf_download.json` | Yahoo ToS; research convenience sample |
| Stress events | Hand-curated from SEC/CFTC/Fed/academic sources | `data/raw/events/stress_events.json` | repo creation | Cite primary sources listed per event |
| LOBSTER samples | LOBSTER / NASDAQ ITCH | https://lobsterdata.com/info/DataSamples.php | attempted | Auto URL failed (HTML); manual download required |
| Stooq daily | Stooq | https://stooq.com/ | attempted | Bot wall; **not used** |
| SEC 13F | SEC EDGAR | https://www.sec.gov/edgar | stub only | Public; fair-access User-Agent |

Corporate actions: Yahoo `auto_adjust=True` (adjusted prices). French industry returns are research portfolio returns (not single-name CA). FRED levels as published.

Survivorship: Yahoo ETF panel ≠ historical S&P membership. French industries are characteristic portfolios (better for factor/ACH tests than today’s SPX list, but not identical to tradable universe).

Look-ahead: event labels use known crisis dates (ex-post). Predictive code uses expanding windows only.
