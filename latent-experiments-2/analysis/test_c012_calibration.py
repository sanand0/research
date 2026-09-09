from pathlib import Path
import importlib.util
import numpy as np

P = Path(__file__).with_name('c012_calibrate.py')
spec = importlib.util.spec_from_file_location('c012_calibrate', P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_lab_is_replication_unit_not_participant_precision():
    effects = np.array([0.10, 0.10, 0.10, -0.20])
    ses = np.array([0.001, 1.0, 1.0, 1.0])
    mu, _, _ = m.pool_lab_effects(effects, ses)
    assert np.isclose(mu, 0.025)


def test_replication_rule_rejects_one_lab_driven_signal():
    effects = np.array([0.40, -0.01, -0.01, -0.01])
    ses = np.ones(4) * 0.02
    passed, detail = m.passes_rule(effects, ses)
    assert not passed
    assert detail['positive_labs'] == 1


def test_replication_rule_accepts_consistent_positive_signal():
    effects = np.array([0.10, 0.12, 0.08, 0.11])
    ses = np.ones(4) * 0.02
    passed, detail = m.passes_rule(effects, ses)
    assert passed
    assert min(detail['leave_one_lab_out_effects']) > 0
