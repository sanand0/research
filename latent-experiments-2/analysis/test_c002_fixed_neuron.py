import importlib.util
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "fixed", Path(__file__).with_name("c002_fixed_neuron_calibrate.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_subset_probabilities_are_fixed_and_bounded():
    w = mod.neuron_weights(1)
    subset = np.arange(32)
    q = mod.subset_probabilities(subset, w)
    assert q.shape == (mod.N_MODULES,)
    assert np.all((q >= 0) & (q <= 1))
    assert q[0] > 0
    assert np.all(q[1:] == 0)


def test_module_index_roundtrip():
    for x in [0, 63, 64, 127, 511]:
        g, j = mod.module_for_neuron(x)
        assert g * mod.MODULE_SIZE + j == x
