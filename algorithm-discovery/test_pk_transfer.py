import unittest
import numpy as np

from pk_transfer import (
    ALGORITHMS,
    BudgetedPK,
    DIMENSION,
    make_protocol,
    simulate_expm,
    simulate_ivp,
    RUNNERS,
)


class PKTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = make_protocol()
        cls.truth_u = np.asarray(cls.protocol["subjects"][0]["unit_truth"], float)

    def test_matrix_exponential_matches_solve_ivp(self):
        theta = np.array(list(self.protocol["subjects"][0]["physical_truth"].values()), float)
        a = simulate_expm(theta)
        b = simulate_ivp(theta)
        np.testing.assert_allclose(a, b, rtol=1e-9, atol=1e-10)

    def test_truth_has_zero_objective_and_parameter_error(self):
        obj = BudgetedPK(self.truth_u, 3)
        self.assertLess(obj(self.truth_u), 1e-24)
        self.assertLess(obj.parameter_error(self.truth_u), 1e-14)

    def test_all_algorithms_obey_strict_budget(self):
        for name, (family, cfg) in ALGORITHMS.items():
            with self.subTest(name=name):
                obj = BudgetedPK(self.truth_u, 37)
                RUNNERS[family](obj, 1, cfg)
                self.assertLessEqual(obj.nfev, 37)
                self.assertEqual(obj.state.evaluations, obj.nfev)


if __name__ == "__main__":
    unittest.main()
