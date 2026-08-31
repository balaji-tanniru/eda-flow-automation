from pathlib import Path

import pytest

from edaflow.config import ConfigError, load_config


def test_load_example_config() -> None:
    config = load_config(Path("configs/counter.yaml"))
    assert config.name == "parameterized_event_counter"
    assert config.top == "event_counter"
    assert config.flatten is True
    assert config.sources[0].name == "event_counter.sv"


def test_rejects_missing_source(tmp_path: Path) -> None:
    configs = tmp_path / "configs"
    configs.mkdir()
    path = configs / "bad.yaml"
    path.write_text(
        """
design:
  name: broken
  top: missing
  sources: [rtl/missing.sv]
flow:
  output_dir: build/broken
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="Missing RTL source"):
        load_config(path)


def test_rejects_output_outside_project(tmp_path: Path) -> None:
    rtl = tmp_path / "rtl"
    configs = tmp_path / "configs"
    rtl.mkdir()
    configs.mkdir()
    (rtl / "top.sv").write_text("module top; endmodule\n", encoding="utf-8")
    path = configs / "bad-output.yaml"
    path.write_text(
        """
design:
  name: safe_design
  top: top
  sources: [rtl/top.sv]
flow:
  output_dir: ../outside
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="must stay inside"):
        load_config(path)

