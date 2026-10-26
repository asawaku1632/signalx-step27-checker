# Morning 09:05 quote failure: evidence-based diagnosis (2026-10-26)

Research only. Do not modify production, notifications, scoring, cron or trading decisions.

## Verified production data (SELECT-only)

- 2026-10-21, 22, 23, 26: five frozen candidates each; zero non-null `price0905` values (20/20 excluded).
- 2026-10-23 and 26: 10/10 observations have `quoteReason=MISSING_CANDLES`.
- 2026-10-21 and 22: 10/10 observations lack `quoteStatus` and `quoteReason`; do not infer the underlying cause.
- All 20 closing comparisons have `complete=false`, `reason=MISSING_OR_MISMATCHED_CLOSE`.

## Verified source-code behavior

Source: `app/lib/research/morningFinalCheckRunner.ts` and `morningFinalCheck.mjs` in `asawaku1632/signal-x`.

1. `openingBars` fetches `query1.finance.yahoo.com/v8/finance/chart/{code}.T?range=1d&interval=5m` with an 8-second timeout.
2. `MISSING_FIVE_MINUTE_CANDLES` is thrown if `data.timestamp` is **not an array** or `data.indicators.quote[0]` is absent. This is mapped to `MISSING_CANDLES`. It does **not** prove that a particular 09:00/09:05 bar is absent.
3. If arrays exist but the required 09:00/09:05 bars or their price/volume values are invalid, `decideAtNineOhFive` returns `UNAVAILABLE` and the runner labels `INVALID_OR_MISSING_OPENING_BAR`.
4. The classifier correctly reads the **09:05 OPEN**, not the 09:05 close (which would not be known at 09:08). No future candle should be substituted.
5. Closing comparison requires both a valid 09:05 observation and a matching complete archived closing result. The current closing failures may be downstream of the missing morning prices; do not conclude the closing feed itself is broken without an independent check.

## Next safe checks

- In a separately approved, licensed research feed, log *metadata only*: HTTP status, Yahoo chart.error code (sanitized), existence/length of timestamp and quote arrays, first/last bar time JST, presence of 09:00/09:05 bars, observation time JST, and provider freshness/delay metadata. Do not store raw licensed price data without rights.
- Differentiate `NO_RESULT`, `NO_TIMESTAMP_ARRAY`, `NO_QUOTE_ARRAY`, `MISSING_0900_BAR`, `MISSING_0905_BAR`, `INVALID_0900_BAR`, `INVALID_0905_OPEN`, `UPSTREAM_HTTP_ERROR`, `UPSTREAM_TIMEOUT`, and `OBSERVATION_TOO_EARLY`.
- Do not retry production morning captures, backfill unavailable prices as though they were observed at 09:08, or infer success from a later-day chart.
- Confirm data-provider usage rights and timestamp-as-of validity before integrating any market data into AI scoring.

**Status:** Root cause not established. Diagnostic plan only; no production fix or new live collection authorized.
