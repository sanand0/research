import unittest

import pandas as pd

import nhanes_pilot as n


class TestMortalityParser(unittest.TestCase):
    def test_parse_fixed_width_line(self):
        line = list(" " * 48)
        line[0:6] = "31127 "
        line[14] = "1"
        line[15] = "1"
        line[16:19] = "002"
        line[19] = "0"
        line[20] = "1"
        line[42:45] = "123"
        line[45:48] = "120"
        row = n.parse_mortality_line("".join(line))
        self.assertEqual(
            row,
            {
                "SEQN": 31127,
                "ELIGSTAT": 1,
                "MORTSTAT": 1,
                "UCOD_LEADING": "002",
                "DIABETES": 0,
                "HYPERTEN": 1,
                "PERMTH_INT": 123,
                "PERMTH_EXM": 120,
            },
        )


class TestExposureRegistry(unittest.TestCase):
    def test_registry_variables_exist_in_downloaded_2005_files(self):
        tables = {
            name: pd.read_sas(path, format="xport", encoding="latin1")
            for name, path in n.local_tables().items()
        }
        for exposure in n.EXPOSURES:
            self.assertIn(exposure["variable"], tables[exposure["table"]].columns)

    def test_clean_binary(self):
        s = pd.Series([1, 2, 3, 7, 9, None])
        got = n.clean_binary(s, yes=1, no=2)
        self.assertEqual(got.tolist()[:2], [1.0, 0.0])
        self.assertTrue(got.iloc[2:].isna().all())

    def test_clean_range(self):
        s = pd.Series([0, 1, 5, 6, 77, 99, None])
        got = n.clean_range(s, lo=0, hi=5)
        self.assertEqual(got.tolist()[:3], [0.0, 1.0, 5.0])
        self.assertTrue(got.iloc[3:].isna().all())

    def test_recode_smoking(self):
        df = pd.DataFrame(
            {"SMQ020": [2, 1, 1, 1, 7], "SMQ040": [None, 1, 2, 3, 1]}
        )
        got = n.recode_smoking(df)
        self.assertEqual(got.tolist()[:4], [0.0, 2.0, 2.0, 1.0])
        self.assertTrue(pd.isna(got.iloc[4]))

    def test_bh_adjust(self):
        got = n.bh_adjust(pd.Series([0.001, 0.01, 0.04, 0.5]))
        self.assertEqual([round(x, 3) for x in got], [0.004, 0.02, 0.053, 0.5])


if __name__ == "__main__":
    unittest.main()
