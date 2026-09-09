import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location('c002_mr', Path(__file__).with_name('c002_mr_calibrate.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_subcritical_recovery_under_subsampling():
    x = mod.simulate_matched(m=0.8, mean_activity=2.0, length=50_000, seed=1)
    y = mod.subsample(x, probability=0.25, seed=2)
    out = mod.estimate_m(y, kmax=100)
    assert out['applicable']
    assert abs(out['m'] - 0.8) < 0.06


def test_near_critical_recovery_under_subsampling():
    x = mod.simulate_matched(m=0.98, mean_activity=2.0, length=80_000, seed=3)
    y = mod.subsample(x, probability=0.25, seed=4)
    out = mod.estimate_m(y, kmax=150)
    assert out['applicable']
    assert abs(out['m'] - 0.98) < 0.04


def test_poisson_null_fails_applicability_gate():
    rng = np.random.default_rng(5)
    x = rng.poisson(2.0, 50_000)
    out = mod.estimate_m(x, kmax=100)
    assert not out['applicable']
