import datetime as dt
import json
import math
import socket
import time
import urllib.error
import urllib.request

JST = dt.timezone(dt.timedelta(hours=9))
HOSTS = ("query1.finance.yahoo.com", "query2.finance.yahoo.com")
def now():
    return dt.datetime.now(dt.timezone.utc).astimezone(JST)

def run():
    attempts = []
    checked = now()
    for host in HOSTS:
        url = f"https://{host}/v8/finance/chart/%5EN225?range=1d&interval=1m"
        for n in range(1, 4):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                with urllib.request.urlopen(request, timeout=12) as response:
                    status = response.status
                    raw = response.read(2000001)
                attempts.append({"host": host, "attempt": n, "http": status})
                if len(raw) > 2000000:
                    return result(checked, attempts, "invalid", "response_too_large")
                try:
                    data = json.loads(raw)
                    chart = data["chart"]["result"]
                    if not isinstance(chart, list) or len(chart) != 1:
                        raise ValueError("result_count")
                    item = chart[0]
                    if item["meta"]["symbol"] != "^N225":
                        raise ValueError("symbol_mismatch")
                    timestamps = item["timestamp"]
                    closes = item["indicators"]["quote"][0]["close"]
                    if not timestamps or len(timestamps) != len(closes):
                        raise ValueError("bars_invalid")
                    stamp, close = timestamps[-1], closes[-1]
                    if type(stamp) is not int or type(close) not in (int, float) or not math.isfinite(close) or close <= 0:
                        raise ValueError("latest_bar_invalid")
                    observed = dt.datetime.fromtimestamp(stamp, dt.timezone.utc).astimezone(JST)
                    age = (now() - observed).total_seconds() / 60
                    state = "invalid" if age < 0 else "stale" if observed.date() != now().date() or age > 20 else "observed"
                    return result(checked, attempts, state, None, observed.isoformat(), close, round(age, 2), stamp)
                except (ValueError, KeyError, IndexError, TypeError, OverflowError) as e:
                    return result(checked, attempts, "invalid", type(e).__name__)
            except urllib.error.HTTPError as e:
                attempts.append({"host": host, "attempt": n, "http": e.code, "error": "http"})
                if e.code in (403, 429):
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                reason = getattr(e, "reason", e)
                kind = "dns" if isinstance(reason, socket.gaierror) else "timeout" if isinstance(reason, (TimeoutError, socket.timeout)) else "network"
                attempts.append({"host": host, "attempt": n, "http": None, "error": kind})
            if n < 3:
                time.sleep(n)
    return result(checked, attempts, "unavailable", "all_endpoints_failed")

def result(checked, attempts, state, error, observed=None, close=None, age=None, timestamp=None):
    return {"executed_at_jst": checked.isoformat(), "symbol_expected": "^N225", "attempts": attempts, "data_acquired": observed is not None, "latest_unix_timestamp": timestamp, "latest_observed_at_jst": observed, "latest_close": close, "elapsed_minutes": age, "step27": state, "error": error, "research_only": True, "database_saved": False}

if __name__ == "__main__":
    report = run()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    with open("step27-result.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
