| research_variable    | dataset           | direct_or_proxy           | frequency     | historical_coverage   | quality                                 | missingness                  |
|:---------------------|:------------------|:--------------------------|:--------------|:----------------------|:----------------------------------------|:-----------------------------|
| bid/ask/sizes (LOB)  | LOBSTER samples   | DATA NOT AVAILABLE (auto) | event         | n/a                   | INSUFFICIENT                            | n/a                          |
| spread/OBI/depth     | LOBSTER           | derived if LOB acquired   | event         | blocked               | INACCESSIBLE publicly for stress days   | n/a                          |
| ETF OHLCV            | Yahoo Finance     | Direct                    | daily         | 2007-2024             | usable                                  | XLRE starts 2015             |
| ETF returns          | derived Yahoo     | Derived                   | daily         | 2007-2024             | usable                                  | first row NA                 |
| industry returns     | French 49 Ind     | Direct                    | daily         | long history→2024+    | usable                                  | -99.99→NA                    |
| FF5/MOM factors      | French library    | Direct                    | daily         | long history          | usable                                  | low                          |
| VIX                  | FRED VIXCLS       | Direct                    | daily         | 1990+                 | usable                                  | weekends/holidays absent     |
| financial stress     | FRED NFCI/STLFSI4 | Direct/proxy              | weekly/daily  | series-dependent      | usable                                  | varies                       |
| repo rates           | FRED SOFR/EFFR    | Direct                    | daily         | SOFR from 2018        | usable                                  | pre-2018 SOFR NA             |
| avg corr / eff rank  | derived ind49/ETF | Derived                   | rolling daily | 2007-2024             | usable                                  | window warmup                |
| persistence/W1/ORC   | computed objects  | Derived                   | windowed      | needs point clouds    | code ready; empirics pending LOB/panels | n/a                          |
| holdings similarity  | SEC 13F           | PROXY (low-freq)          | quarterly     | EDGAR public          | ingestion stub only                     | not downloaded               |
| Sent_AI              | —                 | DATA NOT AVAILABLE        | —             | —                     | omit or GDELT PROXY later               | n/a                          |
| hist. S&P membership | CRSP/WRDS         | DATA NOT AVAILABLE here   | daily         | —                     | INACCESSIBLE without WRDS               | survivorship risk if ignored |