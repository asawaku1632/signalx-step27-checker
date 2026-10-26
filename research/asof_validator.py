"""Fail-closed as-of market observation validator. Offline, no network or database."""
from datetime import datetime, timedelta, timezone
import math

JST = timezone(timedelta(hours=9))

def parse_jst(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None or dt.utcoffset() != timedelta(hours=9):
        return None
    return dt.astimezone(JST)

def validate_asof(signal_at_jst, market_observed_at_jst, market_value, max_age_minutes=20):
    signal = parse_jst(signal_at_jst)
    observed = parse_jst(market_observed_at_jst)
    if signal is None or observed is None:
        return {"valid": False, "reason": "invalid_timestamp"}
    if not isinstance(max_age_minutes, (int, float)) or not math.isfinite(max_age_minutes) or max_age_minutes < 0:
        return {"valid": False, "reason": "invalid_max_age"}
    try:
        value = float(market_value)
    except (TypeError, ValueError):
        return {"valid": False, "reason": "invalid_market_value"}
    if not math.isfinite(value) or value <= 0:
        return {"valid": False, "reason": "invalid_market_value"}
    if observed > signal:
        return {"valid": False, "reason": "future_observation"}
    if observed.date() != signal.date():
        return {"valid": False, "reason": "different_jst_date"}
    age_minutes = (signal - observed).total_seconds() / 60
    if age_minutes > max_age_minutes:
        return {"valid": False, "reason": "stale_observation", "age_minutes": round(age_minutes, 3)}
    return {"valid": True, "reason": "asof_pass", "age_minutes": round(age_minutes, 3)}
