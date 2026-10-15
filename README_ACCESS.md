# SEC 13F access notes

- Provider: U.S. SEC EDGAR
- Form: 13F-HR (institutional holdings, quarterly)
- Official: https://www.sec.gov/edgar
- Bulk: EDGAR full-index by quarter; information tables in XML (older: tab-delimited)
- Identifiers: CUSIP + shares + market value; map to tickers via CRSP/OpenFIGI
- Licensing: public U.S. government data; respect SEC fair-access User-Agent rules
- Suitability: PROXY — institutional portfolio cosine similarity, not HFT/ACH directly
- Status: DATA NOT DOWNLOADED in bulk in this pass (rate limits + large parse job)

Required User-Agent example:
  Sample Research academic@example.edu metric-decay-pipeline
