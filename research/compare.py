import csv
import json
import math
import sys
from collections import defaultdict

FIELDS = ("signal_date", "symbol", "ai_power", "market_return_pct", "return_1d_pct", "return_3d_pct", "return_5d_pct")
HORIZONS = ("return_1d_pct", "return_3d_pct", "return_5d_pct")

def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None

def analyze(rows):
    groups = defaultdict(list)
    rejected = 0
    for row in rows:
        power = number(row.get("ai_power"))
        market = number(row.get("market_return_pct"))
        if power is None or market is None or not 0 <= power <= 100:
            rejected += 1
            continue
        band = "80+" if power >= 80 else "60-79" if power >= 60 else "0-59"
        regime = "up" if market > 0 else "down" if market < 0 else "flat"
        groups[(band, regime)].append(row)
    report = []
    for (band, regime), members in sorted(groups.items()):
        result = {"ai_power_band": band, "market_regime": regime, "count": len(members)}
        for horizon in HORIZONS:
            values = [number(row.get(horizon)) for row in members]
            values = [v for v in values if v is not None]
            result[horizon] = {"n": len(values), "mean_pct": round(sum(values) / len(values), 3) if values else None, "win_rate_pct": round(100 * sum(v > 0 for v in values) / len(values), 2) if values else None, "minimum_30_met": len(values) >= 30}
        report.append(result)
    return {"research_only": True, "rejected_rows": rejected, "groups": report}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python research/compare.py authorized_input.csv")
    with open(sys.argv[1], encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not set(FIELDS).issubset(reader.fieldnames or []):
            raise SystemExit("Missing required CSV columns")
        print(json.dumps(analyze(reader), ensure_ascii=False, indent=2))
