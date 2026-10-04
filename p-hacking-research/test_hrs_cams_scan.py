import unittest
from pathlib import Path

import pandas as pd

import hrs_cams_scan as h


class TestHrsCamsScan(unittest.TestCase):
    def test_registry_is_frozen_31_activity_family(self):
        r = h.read_registry(Path("hrs-cams-activity-registry.csv"))
        self.assertEqual(len(r), 31)
        book = r.set_index("variable").loc["A3_01"]
        self.assertEqual(book["label"], "READ BOOKS")
        self.assertEqual(book["period"], "week")

    @unittest.skipUnless(h.CAMS.exists(), "official HRS/CAMS data not installed")
    def test_local_cams_matches_official_record_count_and_registry(self):
        cams = pd.read_stata(h.CAMS, convert_categoricals=False)
        self.assertEqual(len(cams), 3866)
        for variable in h.read_registry()["variable"]:
            self.assertIn(variable, cams.columns)

    def test_hhidpn(self):
        self.assertEqual(h.make_hhidpn("010001", "010"), 10001010)
        self.assertEqual(h.make_hhidpn(10001, 10), 10001010)

    def test_any_time(self):
        s = pd.Series([0, 0.0, 0.25, 1, 12, None])
        got = h.any_time(s)
        self.assertEqual(got.iloc[:5].tolist(), [0.0, 0.0, 1.0, 1.0, 1.0])
        self.assertTrue(pd.isna(got.iloc[5]))

    def test_married(self):
        s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, None])
        got = h.married(s)
        self.assertEqual(got.iloc[:8].tolist(), [1, 1, 1, 0, 0, 0, 0, 0])
        self.assertTrue(pd.isna(got.iloc[8]))

    def test_ndi_survival(self):
        d = pd.Series(
            pd.to_datetime(["2005-01-01", "2014-01-01", None])
        )
        duration, event = h.survival_from_ndi(
            d,
            baseline=pd.Timestamp("2001-09-01"),
            cutoff=pd.Timestamp("2012-12-31"),
        )
        self.assertEqual(event.tolist(), [1, 0, 0])
        self.assertGreater(duration.iloc[0], 3)
        self.assertGreater(duration.iloc[1], 11)
        self.assertAlmostEqual(duration.iloc[1], duration.iloc[2], places=8)

    def test_bh_adjust(self):
        got = h.bh_adjust(pd.Series([0.001, 0.01, 0.04, 0.5]))
        self.assertEqual([round(x, 3) for x in got], [0.004, 0.02, 0.053, 0.5])

    def test_committed_primary_results(self):
        results = pd.read_csv(
            "results/hrs_cams_activity_headline_factory.csv"
        )
        self.assertEqual(len(results), 31 * 2 * 2)
        primary = results[
            (results["model"] == "paper_like")
            & (results["sample"] == "exposure_specific")
        ]
        self.assertEqual((primary["status"] == "ok").sum(), 28)
        self.assertEqual((primary["p"] < 0.05).sum(), 20)
        self.assertEqual((primary["q_bh"] < 0.05).sum(), 18)

        modeled = primary[primary["status"] == "ok"].sort_values("p")
        book = modeled[modeled["is_books"]].iloc[0]
        rank = modeled.reset_index(drop=True).index[
            modeled.reset_index(drop=True)["is_books"]
        ][0] + 1
        self.assertEqual(rank, 11)
        self.assertAlmostEqual(book["hr"], 0.8159712782, places=8)
        self.assertAlmostEqual(book["q_bh"], 0.0125255797, places=8)

        functional = results[
            (results["model"] == "functional")
            & (results["sample"] == "exposure_specific")
        ]
        self.assertEqual((functional["q_bh"] < 0.05).sum(), 17)


if __name__ == "__main__":
    unittest.main()
