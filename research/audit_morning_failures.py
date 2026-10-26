"""Offline, fail-closed audit of archived morning-final-check records.

No network, database, or production mutations. Input is an authorized JSON export
of morning_final_check_runs; avoid personal data and do not commit exports.
"""
import json
import sys
from collections import Counter
from pathlib import Path

def audit(records):
    counts = Counter()
    for run in records:
        day = run.get("trade_date")
        for item in run.get("morning_observations") or []:
            status = item.get("quoteStatus") or "MISSING_STATUS"
            reason = item.get("quoteReason") or "MISSING_REASON"
            price = item.get("price0905")
            valid_price = isinstance(price, (int, float)) and not isinstance(price, bool) and 0 < price < float("inf")
            if status == "OBSERVED" and valid_price:
                counts["observed_with_price"] += 1
            else:
                counts["excluded_from_0905_analysis"] += 1
                counts["morning:" + status + ":" + reason] += 1
        for item in run.get("closing_results") or []:
            if item.get("complete") is True:
                counts["closing_complete"] += 1
            else:
                counts["closing_incomplete"] += 1
                counts["closing:" + str(item.get("reason") or "MISSING_REASON")] += 1
        if not isinstance(day, str) or not day:
            counts["missing_trade_date"] += 1
    return {"research_only": True, "no_imputation": True, "counts": dict(sorted(counts.items()))}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python research/audit_morning_failures.py <local-export.json>")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("Expected a JSON array of archived run objects")
    print(json.dumps(audit(data), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
