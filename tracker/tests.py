from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from tracker.decider import baseline_from, decide
from tracker.sessions import group_sessions
from tracker.stats import backtest, compute_stats


def fake(hours, result="1", kd="1.0", adr="80"):
    return {"stats": {
        "Match Finished At": int(hours * 3600 * 1000),
        "Result": result, "K/D Ratio": kd,
        "ADR": adr, "Map": "de_mirage",
    }}


def nm(hours, won=True, kd=1.0, adr=80.0):
    return {"ts": hours * 3600, "won": won, "kd": kd, "adr": adr, "map": "x"}


def tash(y, mo, d, h):
    return datetime(y, mo, d, h, tzinfo=ZoneInfo("Asia/Tashkent")).timestamp()


NOON = tash(2026, 7, 20, 13)


class SessionTests(SimpleTestCase):
    def test_gap_splits_sessions(self):
        sessions, _ = group_sessions([fake(0), fake(1), fake(5)])
        self.assertEqual([len(s) for s in sessions], [1, 2])

    def test_newest_first_everywhere(self):
        sessions, _ = group_sessions([fake(0), fake(5), fake(6)])
        self.assertEqual(len(sessions[0]), 2)
        self.assertGreater(sessions[0][0]["ts"], sessions[0][1]["ts"])

    def test_active_within_2h(self):
        _, active = group_sessions([fake(10)], now=11 * 3600)
        self.assertIsNotNone(active)

    def test_fresh_queue_after_2h(self):
        _, active = group_sessions([fake(10)], now=12.5 * 3600)
        self.assertIsNone(active)

    def test_ms_to_seconds(self):
        sessions, _ = group_sessions([fake(1)])
        self.assertEqual(sessions[0][0]["ts"], 3600)

    def test_missing_adr_is_none(self):
        m = fake(1)
        del m["stats"]["ADR"]
        sessions, _ = group_sessions([m])
        self.assertIsNone(sessions[0][0]["adr"])

    def test_empty(self):
        self.assertEqual(group_sessions([]), ([], None))


class DeciderTests(SimpleTestCase):
    def test_two_losses_hard_stop(self):
        s = [nm(10, won=False), nm(9, won=False)]
        self.assertEqual(decide(s, None, s, NOON)["verdict"], "STOP")

    def test_bank_it(self):
        s = [nm(10, won=True), nm(9, won=False), nm(8, won=True)]
        self.assertEqual(decide(s, None, s, NOON)["verdict"], "BANK IT")

    def test_fresh_queue_clean(self):
        r = decide(None, None, [], NOON)
        self.assertEqual((r["verdict"], r["score"]), ("QUEUE", 100))

    def test_night_penalty(self):
        r = decide(None, None, [], tash(2026, 7, 21, 2))
        self.assertEqual(r["score"], 90)

    def test_fatigue_six_in_24h(self):
        hist = [nm(h) for h in range(10, 4, -1)]
        r = decide(None, None, hist, 11 * 3600)
        self.assertEqual(r["score"], 85)

    def test_low_kd_ratio(self):
        s = [nm(10, won=True, kd=0.7), nm(9, won=False, kd=0.7)]
        r = decide(s, {"kd": 1.0, "adr": 80}, s, NOON)
        self.assertEqual(r["score"], 90)
        self.assertEqual(r["verdict"], "QUEUE")

    def test_baseline_needs_ten(self):
        self.assertIsNone(baseline_from([nm(1)] * 9))
        self.assertIsNotNone(baseline_from([nm(1)] * 10))
        
    
class StatsTests(SimpleTestCase):
    def test_backtest_counts_tilt_spirals(self):
        hist = [nm(i, won=False) for i in range(5, 0, -1)]
        self.assertEqual(backtest(hist)["stop_signals"], 3)
    def test_backtest_no_signal_all_wins(self):
        self. assertEqual(backtest([nm(3), nm(2), nm(1)])["stop_signals"], 0)
    def test_compute_empty(self):
        self.assertIsNone(compute_stats([]))
        
