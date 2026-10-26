import unittest
from audit_morning_failures import audit

class MorningAuditTests(unittest.TestCase):
    def test_missing_candles_and_close_are_not_success(self):
        result = audit([{"trade_date":"2026-10-26","morning_observations":[
            {"quoteStatus":"UNAVAILABLE","quoteReason":"MISSING_CANDLES","price0905":None}],
            "closing_results":[{"complete":False,"reason":"MISSING_OR_MISMATCHED_CLOSE"}]}])
        self.assertEqual(result["counts"]["excluded_from_0905_analysis"],1)
        self.assertEqual(result["counts"]["closing_incomplete"],1)
        self.assertNotIn("observed_with_price",result["counts"])

    def test_missing_status_with_price_is_still_excluded(self):
        result=audit([{"trade_date":"2026-10-21","morning_observations":[{"price0905":100}]}])
        self.assertEqual(result["counts"]["excluded_from_0905_analysis"],1)

    def test_observed_valid_price(self):
        result=audit([{"trade_date":"2026-10-26","morning_observations":[
            {"quoteStatus":"OBSERVED","price0905":100.5}],
            "closing_results":[{"complete":True}]}])
        self.assertEqual(result["counts"]["observed_with_price"],1)
        self.assertEqual(result["counts"]["closing_complete"],1)

if __name__=="__main__":
    unittest.main()
