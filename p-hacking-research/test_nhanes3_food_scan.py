import math
import unittest
from pathlib import Path

import pandas as pd

import nhanes3_food_scan as n


class TestRegistry(unittest.TestCase):
    def test_frozen_registry_has_60_named_foods(self):
        registry = n.read_registry(Path("nhanes3-food-registry.csv"))
        self.assertEqual(len(registry), 60)
        chili = registry.set_index("variable").loc["HAN4JS"]
        self.assertEqual((int(chili.start), int(chili.end)), (2093, 2095))
        self.assertIn("Hot red chili peppers", chili.label)

    def test_food_consumer_recode(self):
        s = pd.Series([0, 1, 30, 243, 888, 999, None])
        got = n.food_consumer(s)
        self.assertEqual(got.tolist()[:4], [0.0, 1.0, 1.0, 1.0])
        self.assertTrue(got.iloc[4:].isna().all())

    def test_education_group(self):
        s = pd.Series([0, 1, 8, 9, 11, 12, 17, 88, 99])
        got = n.education_group(s)
        self.assertEqual(got.tolist()[:7], [0, 1, 1, 2, 2, 3, 3])
        self.assertTrue(got.iloc[7:].isna().all())

    def test_marital_group(self):
        s = pd.Series([1, 2, 3, 4, 5, 6, 7, 88, 99])
        got = n.marital_group(s)
        self.assertEqual(got.tolist()[:7], [1, 1, 1, 2, 2, 2, 3])
        self.assertTrue(got.iloc[7:].isna().all())

    def test_bh_adjust(self):
        got = n.bh_adjust(pd.Series([0.001, 0.01, 0.04, 0.5]))
        self.assertEqual([round(x, 3) for x in got], [0.004, 0.02, 0.053, 0.5])


if __name__ == "__main__":
    unittest.main()
