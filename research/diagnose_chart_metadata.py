"""Offline 09:05 provider metadata diagnosis. No network or price persistence."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
ALLOWED_FIELDS = {"status", "reason", "timestamp_count", "has_0900", "has_0905"}

def classify_chart(payload, observed_at_iso, trade_date):
    try:
        observed = datetime.fromisoformat(observed_at_iso)
    except (TypeError, ValueError):
        return {"status":"UNAVAILABLE","reason":"INVALID_OBSERVATION_TIME"}
    if observed.tzinfo is None or observed.utcoffset() is None:
        return {"status":"UNAVAILABLE","reason":"MISSING_OBSERVATION_TIME"}
    observed_jst = observed.astimezone(JST)
    if observed_jst.date().isoformat() != trade_date or not (545 <= observed_jst.hour*60+observed_jst.minute < 559):
        return {"status":"UNAVAILABLE","reason":"OBSERVATION_OUTSIDE_WINDOW"}
    if not isinstance(payload, dict):
        return {"status":"UNAVAILABLE","reason":"INVALID_RESPONSE"}
    chart = payload.get("chart")
    if not isinstance(chart, dict):
        return {"status":"UNAVAILABLE","reason":"NO_CHART"}
    if chart.get("error"):
        return {"status":"UNAVAILABLE","reason":"PROVIDER_CHART_ERROR"}
    results = chart.get("result")
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        return {"status":"UNAVAILABLE","reason":"NO_RESULT"}
    result = results[0]
    times = result.get("timestamp")
    if not isinstance(times, list):
        return {"status":"UNAVAILABLE","reason":"NO_TIMESTAMP_ARRAY"}
    indicators = result.get("indicators")
    quotes = indicators.get("quote") if isinstance(indicators, dict) else None
    if not isinstance(quotes, list) or not quotes or not isinstance(quotes[0], dict):
        return {"status":"UNAVAILABLE","reason":"NO_QUOTE_ARRAY"}
    slots = set()
    for t in times:
        if isinstance(t, (int, float)) and not isinstance(t, bool):
            try:
                dt = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(JST)
                if dt.date().isoformat() == trade_date:
                    slots.add(dt.strftime("%H:%M"))
            except (OverflowError, OSError, ValueError):
                continue
    if "09:00" not in slots:
        reason = "MISSING_0900_BAR"
    elif "09:05" not in slots:
        reason = "MISSING_0905_BAR"
    else:
        reason = "BARS_PRESENT_NOT_PRICE_VALIDATED"
    return {"status":"DIAGNOSTIC_ONLY","reason":reason,"timestamp_count":len(times),
            "has_0900":"09:00" in slots,"has_0905":"09:05" in slots}

def main():
    parser=argparse.ArgumentParser(description="Inspect an authorized local chart JSON; print safe metadata only.")
    parser.add_argument("json_path", type=Path)
    parser.add_argument("--observed-at",required=True,help="ISO-8601 timestamp with UTC offset")
    parser.add_argument("--trade-date",required=True,help="YYYY-MM-DD")
    args=parser.parse_args()
    payload=json.loads(args.json_path.read_text(encoding="utf-8"))
    result=classify_chart(payload,args.observed_at,args.trade_date)
    print(json.dumps({k:v for k,v in result.items() if k in ALLOWED_FIELDS},sort_keys=True))

if __name__=="__main__":
    main()
