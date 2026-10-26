import unittest
from asof_validator import validate_asof

class AsOfTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate_asof("2026-10-27T09:05:00+09:00", "2026-10-27T09:04:00+09:00", 62000)["valid"])
    def test_future(self):
        self.assertEqual(validate_asof("2026-10-27T09:05:00+09:00", "2026-10-27T09:06:00+09:00", 62000)["reason"], "future_observation")
    def test_stale(self):
        self.assertEqual(validate_asof("2026-10-27T09:30:00+09:00", "2026-10-27T09:05:00+09:00", 62000)["reason"], "stale_observation")
    def test_previous_day(self):
        self.assertEqual(validate_asof("2026-10-27T09:05:00+09:00", "2026-10-26T15:30:00+09:00", 62000)["reason"], "different_jst_date")
    def test_missing_timezone(self):
        self.assertEqual(validate_asof("2026-10-27T09:05:00", "2026-10-27T09:04:00+09:00", 62000)["reason"], "invalid_timestamp")
    def test_invalid_value(self):
        self.assertEqual(validate_asof("2026-10-27T09:05:00+09:00", "2026-10-27T09:04:00+09:00", float("nan"))["reason"], "invalid_market_value")

if __name__ == "__main__":
    unittest.main()
