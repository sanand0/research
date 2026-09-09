import importlib.util
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

margin = load('c003_margin_null', 'c003_margin_null.py')
confirm = load('c003_confirmation_627', 'c003_confirmation_627.py')


def test_ipf_preserves_support_and_margins():
    support = np.array([[1,1,0],[1,0,1],[0,1,1]], dtype=bool)
    row = np.array([3.0, 4.0, 5.0])
    col = np.array([4.0, 3.0, 5.0])
    w = np.array([[2.0,1.0,9.0],[1.0,9.0,3.0],[9.0,2.0,2.0]])
    x, _ = margin.balance_to_margins(w, row, col, support)
    assert np.allclose(x.sum(axis=1), row, rtol=1e-9, atol=1e-9)
    assert np.allclose(x.sum(axis=0), col, rtol=1e-9, atol=1e-9)
    assert np.array_equal(x > 0, support)


def test_empirical_p_is_directional_and_never_zero():
    null = [1,2,3,4]
    assert margin.empirical_p(0.5, null, 'lower') == 0.2
    assert margin.empirical_p(4.5, null, 'upper') == 0.2


def test_confirmation_source_guard_and_unique_censuses():
    years, plots = confirm.load_plots()
    assert len(years) == 10
    assert len(plots) == 5
    assert all(int(d['eligible'].sum()) >= 4 for d in plots.values())


def test_pseudo_extreme_flags_are_conservative():
    b = np.arange(999, dtype=float)
    cv = np.arange(999, dtype=float)[::-1]
    flags = confirm.pseudo_extreme_flags(b, cv)
    assert flags.sum() <= 25
