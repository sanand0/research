import json
import tempfile
import unittest
from pathlib import Path

from live import (
    FreshQuadratic,
    commit_prediction,
    load_prediction_problems,
    problem_key,
)


class LiveExperimentTests(unittest.TestCase):
    def test_quadratic_snapshots_respect_budget(self):
        obj = FreshQuadratic(5, 100.0, True, 123, 250)
        x = [0.0] * 5
        for _ in range(250):
            obj(x)
        obj.fill_snapshots()
        self.assertEqual(obj.nfev, 250)
        self.assertIn(50, obj.snapshots)
        self.assertNotIn(100, obj.snapshots)

    def test_prediction_is_persisted_and_repeat_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "live.jsonl"
            problem = problem_key(5, 100.0, True, 123)
            commitment = commit_prediction(path, problem, ["scipy-p2"], 50, "p2 may win")
            self.assertEqual(len(commitment), 64)
            records = [json.loads(x) for x in path.read_text().splitlines()]
            self.assertEqual(records[0]["type"], "prediction")
            self.assertEqual(records[0]["commitment_sha256"], commitment)
            self.assertEqual(len(load_prediction_problems(path)), 1)
            with self.assertRaises(SystemExit):
                commit_prediction(path, problem, ["scipy-p2"], 50, "try again")


if __name__ == "__main__":
    unittest.main()
