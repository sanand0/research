import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "state", Path(__file__).with_name("c002_state_switch_calibrate.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_schedule_shape_rejected():
    try:
        mod.simulate_piecewise([[0.9] * mod.N_MODULES], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("bad schedule was accepted")
