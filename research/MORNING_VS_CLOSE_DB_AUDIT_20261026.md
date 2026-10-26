# Morning vs closing: read-only production audit (2026-10-26)

No production writes, provider calls, or price exports.

## Morning final check
| Date | Observations | Valid 09:05 prices | MISSING_CANDLES |
|---|---:|---:|---:|
| 2026-10-21 | 5 | 0 | 0 (reason not recorded) |
| 2026-10-22 | 5 | 0 | 0 (reason not recorded) |
| 2026-10-23 | 5 | 0 | 5 |
| 2026-10-26 | 5 | 0 | 5 |

## Independent closing research (policy PRIOR_DAY_TOP5_CLOSE_V1)
| Date | Entries | closePrice populated | complete true |
|---|---:|---:|---:|
| 2026-10-21 | 5 | 5 | 5 |
| 2026-10-22 | 5 | 5 | 2 |
| 2026-10-23 | 5 | 5 | 4 |
| 2026-10-26 | 5 | 5 | 5 |

These are database field-presence counts, not independently verified price accuracy. The independent closing research has 20/20 populated closePrice values and 16/20 completed outcomes. All 20 morning price0905 values are missing. Therefore do not infer that all closing quotes failed simply because all morning-vs-close joins were incomplete.

2026-10-27 morning_final_check_runs was PENDING with no morning observations at audit time.

## Root cause status
The production Yahoo 5-minute fetch throws MISSING_FIVE_MINUTE_CANDLES when the chart timestamp array or quote array is absent. The saved records do not preserve which part was absent. This is not enough to attribute failure to a delayed 09:05 bar, and historical after-the-fact queries cannot prove what the 09:08 response contained.

## Next authorized research step
With licensing and privacy review, add *metadata-only* upstream diagnostics to a separate research branch, recording HTTP status class, chart.error presence, timestamp/quote-array existence, timestamp range and 09:00/09:05 bar presence. Do not deploy, backfill, rerun production cron, or promote into AI scoring before validation.
