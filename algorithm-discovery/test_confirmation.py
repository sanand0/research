import unittest
from confirm_bbob import ALGORITHMS, RUNNERS
from bench import BudgetedBBOB


class ConfirmationConfigTests(unittest.TestCase):
    def test_frozen_algorithms_respect_budget(self):
        for name, (family, cfg) in ALGORITHMS.items():
            with self.subTest(name=name):
                obj = BudgetedBBOB(1, 1, 5, 400)
                RUNNERS[family](obj, 1, cfg)
                self.assertLessEqual(obj.nfev, 400)
                self.assertEqual(obj._problem.state.evaluations, obj.nfev)


if __name__ == "__main__":
    unittest.main()
