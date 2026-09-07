import json
from pathlib import Path

import pytest

from edaflow.report import ReportError, read_yosys_stats, write_summary


def test_reads_top_module_statistics(tmp_path: Path) -> None:
    stats_path = tmp_path / "stats.json"
    stats_path.write_text(
        json.dumps(
            {
                "modules": {
                    "\\event_counter": {
                        "num_wires": 8,
                        "num_wire_bits": 40,
                        "num_pub_wires": 6,
                        "num_pub_wire_bits": 21,
                        "num_memories": 0,
                        "num_cells": 12,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    assert read_yosys_stats(stats_path, "event_counter")["cells"] == 12


def test_rejects_missing_top_module(tmp_path: Path) -> None:
    stats_path = tmp_path / "stats.json"
    stats_path.write_text('{"modules": {}}', encoding="utf-8")
    with pytest.raises(ReportError, match="missing"):
        read_yosys_stats(stats_path, "event_counter")


def test_writes_pass_summary(tmp_path: Path) -> None:
    summary = tmp_path / "summary.md"
    write_summary(
        summary,
        design_name="demo",
        top="top",
        tool_version="Yosys test",
        elapsed_seconds=0.25,
        stats={
            "wires": 5,
            "wire_bits": 10,
            "public_wires": 2,
            "public_wire_bits": 4,
            "memories": 0,
            "cells": 3,
        },
    )
    text = summary.read_text(encoding="utf-8")
    assert "| Status | PASS |" in text
    assert "| Cells | 3 |" in text

