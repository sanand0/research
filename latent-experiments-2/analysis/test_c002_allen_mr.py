import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('allen', Path(__file__).with_name('c002_allen_mr.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_fixed_subset_is_deterministic_and_nested():
    ids = list(range(100, 180))
    a = mod.fixed_subset(ids, 32, 123)
    b = mod.fixed_subset(ids, 32, 123)
    c = mod.fixed_subset(ids, 16, 123)
    assert a == b
    assert set(c).issubset(a)
    assert len(a) == 32


def test_confirmation_session_is_rejected():
    claim = {'discovery_sessions': [1, 2], 'confirmation_sessions': [3]}
    try:
        mod.assert_discovery(3, claim)
    except ValueError:
        pass
    else:
        raise AssertionError('confirmation session was not rejected')
