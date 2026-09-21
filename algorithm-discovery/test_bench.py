import unittest

import numpy as np

from bench import BudgetExhausted, BudgetedBBOB, run_lshade, run_scipy


class BudgetTests(unittest.TestCase):
    def test_known_solution_and_exact_boundary(self):
        obj = BudgetedBBOB(1, 1, 5, 3)
        # This validation uses the hidden optimum only in the test, never in an optimizer.
        xopt = np.asarray(obj._problem.optimum.x)
        obj(xopt)
        self.assertLessEqual(obj.error, 1e-10)
        obj(np.zeros(5))
        obj(np.ones(5))
        with self.assertRaises(BudgetExhausted):
            obj(np.zeros(5))
        self.assertEqual(obj.nfev, 3)
        self.assertEqual(obj._problem.state.evaluations, 3)

    def test_dplus1_halton_stops_at_objective_boundary(self):
        obj = BudgetedBBOB(3, 1, 5, 37)
        run_scipy(obj, 1, {"strategy": "best1bin", "updating": "immediate", "init_size": "d+1"})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)

    def test_scipy_stops_at_objective_boundary(self):
        obj = BudgetedBBOB(3, 1, 5, 37)
        run_scipy(obj, 1, {"strategy": "best1bin", "popsize": 5, "updating": "immediate"})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)

    def test_direct_respects_strict_budget(self):
        from bench import run_direct
        obj = BudgetedBBOB(3, 1, 5, 37)
        run_direct(obj, 1, {"locally_biased": True, "eps": 1e-4})
        self.assertLessEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, obj.nfev)

    def test_cma_respects_strict_budget(self):
        from bench import run_cma

        obj = BudgetedBBOB(3, 1, 5, 37)
        run_cma(obj, 1, {"sigma_frac": 0.3, "popsize_mult": 1.0})
        self.assertLessEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, obj.nfev)

    def test_lshade_stops_at_objective_boundary(self):
        obj = BudgetedBBOB(3, 1, 5, 37)
        run_lshade(obj, 1, {"lambda_per_d": 4})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)


class CandidateTests(unittest.TestCase):
    def test_even_population_schedule_is_balanced_and_antithetic(self):
        from collections import Counter
        from candidate import BalancedAntitheticBest1

        rng = np.random.default_rng(7)
        strategy = BalancedAntitheticBest1()
        population = rng.normal(size=(20, 5))
        for candidate in range(20):
            strategy(candidate, population, rng=rng)
        counts = Counter(j for pair in strategy._schedule for j in pair)
        self.assertEqual(set(counts.values()), {2})
        for candidate in range(0, 20, 2):
            a, b = strategy._schedule[candidate]
            self.assertEqual(strategy._schedule[candidate + 1], (b, a))
            self.assertNotIn(a, (candidate, candidate + 1))
            self.assertNotIn(b, (candidate, candidate + 1))

    def test_rejection_transform_contracts_overrejected_axis(self):
        from candidate import rejection_whitening_transform

        steps = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
        rejected = np.array([True, True, False, False])
        transform = rejection_whitening_transform(steps, rejected)
        self.assertLess(np.linalg.norm(transform @ np.array([1.0, 0.0])),
                        np.linalg.norm(transform @ np.array([0.0, 1.0])))

    def test_rejde_respects_strict_budget(self):
        from bench import run_rejde

        obj = BudgetedBBOB(3, 1, 5, 37)
        run_rejde(obj, 1, {"popsize": 5, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)

    def test_pairde_respects_strict_budget(self):
        from bench import run_pairde

        obj = BudgetedBBOB(3, 1, 5, 37)
        run_pairde(obj, 1, {"popsize": 5, "init": "halton", "mutation": (0.5, 1.0), "recombination": 0.7})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)

    def test_seqde_respects_strict_budget(self):
        from bench import run_seqde

        obj = BudgetedBBOB(3, 1, 5, 37)
        stats = run_seqde(obj, 1, {"pop_per_d": 2, "mutation": (0.5, 1.0), "recombination": 0.7, "active": True})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)
        self.assertGreaterEqual(stats["aborts"], 0)

    def test_switchf_resamples_after_unchanged_prefix(self):
        from candidate import PrefixResampleBest1

        rng = np.random.default_rng(9)
        strategy = PrefixResampleBest1(active=True, switch_fraction=0.25)
        population = rng.normal(size=(10, 5))
        for candidate in range(4):
            strategy(candidate, population.copy(), rng=rng)
        self.assertEqual(strategy.resamples, 1)

    def test_conditioned_halton_is_full_rank_and_conditioned(self):
        from candidate import conditioned_halton_population
        x = conditioned_halton_population(10, np.full(10, -5.0), np.full(10, 5.0), seed=7, condition_limit=20.0)
        z = (x - x.mean(axis=0)) / 10.0
        singular = np.linalg.svd(z, compute_uv=False)
        self.assertEqual(np.linalg.matrix_rank(z), 10)
        self.assertLessEqual((singular[0] / singular[-1]) ** 2, 20.0 + 1e-10)
        self.assertLessEqual(len(x), 40)

    def test_switchf_respects_strict_budget(self):
        from bench import run_switchf

        obj = BudgetedBBOB(3, 1, 5, 37)
        run_switchf(obj, 1, {"popsize": 2, "init": "halton", "active": True})
        self.assertEqual(obj.nfev, 37)
        self.assertEqual(obj._problem.state.evaluations, 37)

    def test_seqde_zero_success_prefix_resamples(self):
        from candidate import run_sequential_best1

        class AlwaysWorse:
            dimension=2; budget=20; nfev=0
            lb=np.full(2,-5.0); ub=np.full(2,5.0)
            def __call__(self, x):
                self.nfev += 1
                return float(self.nfev)

        obj = AlwaysWorse()
        stats = run_sequential_best1(obj, seed=3, pop_per_d=2, active=True)
        self.assertGreater(stats["aborts"], 0)


if __name__ == "__main__":
    unittest.main()
