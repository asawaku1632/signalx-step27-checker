# SIGNALX market-learning integration audit — 2026-10-26

## Code findings (read-only inspection)
- `app/lib/marketLearning.ts`: market score is derived from average stock AI POWER and price changes. Optional Nikkei/TOPIX inputs contribute absolute-level labels, not intraday direction; summary writes to `market_learning_logs`.
- `app/lib/learning/database.ts`: `getLatestMarketPattern` and `getLatestMarketBonus` select the newest market-learning row by trade date; no freshness or decision-time guard is visible in these queries.
- `app/lib/learning/marketLearning.ts`: learned bonus is selected when confidence >= 50, otherwise fixed bonus.
- `app/lib/learning/scanEngine.ts`: both latest market pattern and bonus are supplied to `runAiPipeline`.
- `app/api/market/pattern/route.ts`: derives market pattern from current stock scan counts, not a licensed Nikkei intraday feed.

## Risks to verify before any integration
1. A prior-day market-learning row may be applied to a new morning scan without explicit as-of provenance. Whether this is intended is not yet established.
2. Market learning bonuses based on outcomes must not use outcomes unavailable at the prediction timestamp.
3. Nikkei absolute-level categories (HIGH/MIDDLE/LOW) are not the same as up/down market regimes.
4. The offline `research/compare.py` requires CSV data whose market returns are proven known at decision time. Its current schema does NOT enforce this; never treat its output as prospective evidence until timestamps and leakage checks are added.
5. No production data writes, no scoring changes, no notification changes. Data licensing must be established before any continuous market collection.

## Next safe milestone
Add an offline validator requiring signal_at_jst, market_observed_at_jst, source, source license, and observation age, then run synthetic unit tests. Afterward map authorized historical SIGNALX results via a read-only export. Compare 1/3/5 trading-day outcomes with chronological holdout; do not activate bonuses based on exploratory comparisons.
