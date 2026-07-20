from django.test import SimpleTestCase
from tracker.sessions import group_sessions



def fake(hours, result="1", kd="1.0", adr="80"):
    return {"stats": {
        "Match Finished At": int(hours * 3600 * 1000),
        "Result": result, "K/D Ratio": kd,
        "ADR": adr, "Map": "de_mirage",
    }}


class SessionTests(SimpleTestCase):
    def test_gap_splits_sessions(self):
        sessions, _ = group_sessions([fake(0), fake(1), fake(5)])
        self.assertEqual([len(s) for s in sessions], [1, 2])

    def test_newest_first_everywhere(self):
        sessions, _ = group_sessions([fake(0), fake(5), fake(6)])
        self.assertEqual(len(sessions[0]), 2)  # newest session first
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