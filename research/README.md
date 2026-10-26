# Market-regime research (offline only)

Goal: compare SIGNALX prediction outcomes across Nikkei 225 market regimes without changing production scoring.

Required data (only from an authorized source): signal timestamp JST, symbol, AI POWER at decision time, market observation timestamp JST, market return known at decision time, and realized returns after 1/3/5 trading days.

Safety: no future leakage; never join a closing market return to a morning signal. Reject missing/stale observations and duplicate keys. Separate market-wide and symbol-specific effects. Group by AI POWER bands and market regime; show sample sizes, win rates and mean/median returns. Use chronological out-of-sample validation before proposing scoring changes. Do not treat Yahoo Finance unofficial endpoint as approved for automated collection. No production, Supabase, trading, notification or research DB writes.
