import unittest
from datetime import datetime, timezone
from diagnose_chart_metadata import classify_chart

def stamp(hour, minute):
    return int(datetime(2026,10,26,hour,minute,tzinfo=timezone.utc).timestamp()) # JST = UTC+9

class ChartMetadataTests(unittest.TestCase):
    def test_no_result(self):
        r=classify_chart({"chart":{"result":None,"error":None}},"2026-10-26T09:08:00+09:00","2026-10-26")
        self.assertEqual(r["reason"],"NO_RESULT")
    def test_missing_timestamp_array(self):
        r=classify_chart({"chart":{"result":[{"indicators":{"quote":[{}]}}]}},"2026-10-26T09:08:00+09:00","2026-10-26")
        self.assertEqual(r["reason"],"NO_TIMESTAMP_ARRAY")
    def test_missing_quote_array(self):
        r=classify_chart({"chart":{"result":[{"timestamp":[]}]}},"2026-10-26T09:08:00+09:00","2026-10-26")
        self.assertEqual(r["reason"],"NO_QUOTE_ARRAY")
    def test_missing_0905_bar(self):
        payload={"chart":{"result":[{"timestamp":[stamp(0,0)],"indicators":{"quote":[{}]}}]}}
        self.assertEqual(classify_chart(payload,"2026-10-26T09:08:00+09:00","2026-10-26")["reason"],"MISSING_0905_BAR")
    def test_both_bars_diagnostic_only(self):
        payload={"chart":{"result":[{"timestamp":[stamp(0,0),stamp(0,5)],"indicators":{"quote":[{}]}}]}}
        r=classify_chart(payload,"2026-10-26T09:08:00+09:00","2026-10-26")
        self.assertEqual(r["reason"],"BARS_PRESENT_NOT_PRICE_VALIDATED")
        self.assertEqual(r["status"],"DIAGNOSTIC_ONLY")
    def test_observation_outside_window(self):
        self.assertEqual(classify_chart({},"2026-10-26T15:30:00+09:00","2026-10-26")["reason"],"OBSERVATION_OUTSIDE_WINDOW")

if __name__=="__main__":
    unittest.main()
