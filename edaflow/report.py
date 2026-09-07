from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReportError(ValueError):
    """Raised when Yosys did not produce a usable statistics report."""


def read_yosys_stats(stats_path: Path, top: str) -> dict[str, int]:
    try:
        raw: dict[str, Any] = json.loads(stats_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReportError(f"Cannot read Yosys statistics: {stats_path}") from exc

    modules = raw.get("modules", {})
    module = modules.get(f"\\{top}") or modules.get(top)
    if not isinstance(module, dict):
        raise ReportError(f"Top module '{top}' is missing from Yosys statistics")

    return {
        "wires": int(module.get("num_wires", 0)),
        "wire_bits": int(module.get("num_wire_bits", 0)),
        "public_wires": int(module.get("num_pub_wires", 0)),
        "public_wire_bits": int(module.get("num_pub_wire_bits", 0)),
        "memories": int(module.get("num_memories", 0)),
        "cells": int(module.get("num_cells", 0)),
    }


def write_summary(
    output_path: Path,
    *,
    design_name: str,
    top: str,
    tool_version: str,
    elapsed_seconds: float,
    stats: dict[str, int],
) -> None:
    lines = [
        "# EDA Flow Run Summary",
        "",
        "| Item | Result |",
        "|---|---:|",
        f"| Status | PASS |",
        f"| Design | `{design_name}` |",
        f"| Top module | `{top}` |",
        f"| Tool | `{tool_version}` |",
        f"| Runtime | {elapsed_seconds:.3f} seconds |",
        f"| Wires | {stats['wires']} |",
        f"| Wire bits | {stats['wire_bits']} |",
        f"| Cells | {stats['cells']} |",
        f"| Memories | {stats['memories']} |",
        "",
        "Generated automatically by `python -m edaflow run configs/counter.yaml`.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

