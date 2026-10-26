"""Offline classification of provider response metadata, without fetching prices."""
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))

def classify_chart(payload, observed_at_iso, trade_date):
    """Return a fail-closed reason and counts; never output prices or candidate signals."""
    observed = datetime.fromisoformat(observed_at_iso)
    if observed.tzinfo is None:
        return {"status": "UNAVAILABLE", "reason": "MISSING_OBSERVATION_TIME"}
    observed_jst = observed.astimezone(JST)
    if observed_jst.date().isoformat() != trade_date or not (9*60+5 <= observed_jst.hour*60+observed_jst.minute < 9*60+19):
        return {"status": "UNAVAILABLE", "reason": "OBSERVATION_OUTSIDE_WINDOW"}
    if not isinstance(payload, dict):
        return {"status": "UNAVAILABLE", "reason": "INVALID_RESPONSE"}
    chart = payload.get("chart")
    if not isinstance(chart, dict):
        return {"status": "UNAVAILABLE", "reason": "NO_CHART"}
    if chart.get("error"):
        return {"status": "UNAVAILABLE", "reason": "PROVIDER_CHART_ERROR"}
    results = chart.get("result")
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        return {"status": "UNAVAILABLE", "reason": "NO_RESULT"}
    result = results[0]
    times = result.get("timestamp")
    if not isinstance(times, list):
        return {"status": "UNAVAILABLE", "reason": "NO_TIMESTAMP_ARRAY"}
    indicators = result.get("indicators")
    quotes = indicators.get("quote") if isinstance(indicators, dict) else None
    if not isinstance(quotes, list) or not quotes or not isinstance(quotes[0], dict):
        return {"status": "UNAVAILABLE", "reason": "NO_QUOTE_ARRAY"}
    slots = set()
    for t in times:
        if not isinstance(t, (int, float)) or isinstance(t, bool):
            continue
        dt = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(JST)
        if dt.date().isoformat() == trade_date:
            slots.add(dt.strftime("%H:%M"))
    if "09:00" not in slots:
        reason = "MISSING_0900_BAR"
    elif "09:05" not in slots:
        reason = "MISSING_0905_BAR"
    else:
        reason = "BARS_PRESENT_NOT_PRICE_VALIDATED"
    return {"status": "DIAGNOSTIC_ONLY", "reason": reason, "timestamp_count": len(times),
            "has_0900": "09:00" in slots, "has_0905": "09:05" in slots}
