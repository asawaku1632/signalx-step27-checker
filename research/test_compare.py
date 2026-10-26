import unittest
from compare import analyze

def sample(**changes):
    row = {
        "signal_date": "2026-10-27",
        "signal_at_jst": "2026-10-27T09:05:00+09:00",
        "market_observed_at_jst": "2026-10-27T09:04:00+09:00",
        "market_index_value": "62000",
        "market_source": "authorized-fixture",
        "market_usage_authorized": "true",
        "symbol": "1234",
        "ai_power": "85",
        "market_return_pct": "-0.5",
        "return_1d_pct": "1.2",
        "return_3d_pct": "2.4",
        "return_5d_pct": "-0.2",
    }
    row.update(changes)
    return row

class CompareTests(unittest.TestCase):
    def test_valid_row(self):
        result = analyze([sample()])
        self.assertEqual(result["accepted_rows"], 1)
        self.assertEqual(result["groups"][0]["market_regime"], "down")
    def test_future_rejected(self):
        result = analyze([sample(market_observed_at_jst="2026-10-27T09:06:00+09:00")])
        self.assertEqual(result["rejected_by_reason"]["future_observation"], 1)
    def test_stale_rejected(self):
        result = analyze([sample(market_observed_at_jst="2026-10-27T08:40:00+09:00")])
        self.assertEqual(result["rejected_by_reason"]["stale_observation"], 1)
    def test_unlicensed_rejected(self):
        result = analyze([sample(market_usage_authorized="false")])
        self.assertEqual(result["rejected_by_reason"]["unverified_market_provenance"], 1)
    def test_duplicate_rejected(self):
        result = analyze([sample(), sample()])
        self.assertEqual(result["accepted_rows"], 1)
        self.assertEqual(result["rejected_by_reason"]["duplicate_or_missing_symbol"], 1)
    def test_date_mismatch_rejected(self):
        result = analyze([sample(signal_date="2026-10-26")])
        self.assertEqual(result["rejected_by_reason"]["invalid_signal_date"], 1)

if __name__ == "__main__":
    unittest.main()
