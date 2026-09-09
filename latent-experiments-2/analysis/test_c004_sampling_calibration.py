import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('c004', Path(__file__).with_name('c004_sampling_calibration.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_reweighting_fixes_between_stratum_but_not_preferential_day_bias():
    old = mod.N_REPS
    mod.N_REPS = 30
    try:
        unbiased = mod.summarize(False)
        preferential = mod.summarize(True)
    finally:
        mod.N_REPS = old
    assert abs(unbiased['reweighted_mean_relative_bias']) < 0.08
    assert unbiased['naive_mean_relative_bias'] > 0.20
    assert preferential['reweighted_mean_relative_bias'] > 0.25
