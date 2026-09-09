import csv
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location("c012_semantic_gate", HERE / "c012_semantic_gate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def write_lab(path: Path, skin_col: str, hr_var: str):
    fields = ["ID_full", "Lc", *MOD.SKIN_SITES, *MOD.HR_VARS]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        w.writeheader()
        for lc in ("r", "b"):
            for i in range(10):
                row = {k: "" for k in fields}
                row.update({"ID_full": "x", "Lc": lc, skin_col: "32.0", hr_var: "70"})
                w.writerow(row)


def test_semantic_gate_stops_without_common_measurement(tmp_path):
    for lab, skin, hr in [
        (1, "Tsk_J", "HRave"),
        (3, "Tsk_A", "HRave"),
        (5, "Tsk_K", "HRinst"),
        (7, "Tsk_H", "HRinst"),
    ]:
        write_lab(tmp_path / f"env_physiological_lab{lab}.csv", skin, hr)
    out = MOD.build_result(tmp_path)
    assert out["semantic_gate_pass"] is False
    assert out["common_skin_sites"] == []
    assert out["common_hr_variables_with_any_terminal_round_in_every_lab"] == []
    assert out["hue_effect_computed"] is False


def test_semantic_gate_can_pass_with_shared_skin_site(tmp_path):
    for lab in MOD.DISCOVERY_LABS:
        write_lab(tmp_path / f"env_physiological_lab{lab}.csv", "Tsk_H", "HRave")
    out = MOD.build_result(tmp_path)
    assert out["semantic_gate_pass"] is True
    assert out["common_skin_sites"] == ["hand"]
