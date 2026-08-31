from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .config import FlowConfig
from .report import read_yosys_stats, write_summary


class FlowError(RuntimeError):
    """Raised when the external synthesis flow fails."""


def find_tool(requested: str | None, candidates: list[str], label: str) -> str:
    candidates = [requested] if requested else candidates
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    raise FlowError(f"{label} was not found. Install it or provide its path.")


def _write_manifest(config: FlowConfig) -> Path:
    manifest = config.output_dir / "sources.txt"
    manifest.write_text(
        "\n".join(str(path) for path in config.sources) + "\n",
        encoding="utf-8",
    )
    return manifest


def run_flow(
    config: FlowConfig,
    yosys_command: str | None = None,
    tclsh_command: str | None = None,
) -> Path:
    yosys = find_tool(yosys_command, ["yosys", "yowasp-yosys"], "Yosys")
    tclsh = find_tool(tclsh_command, ["tclsh"], "Tcl")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _write_manifest(config)
    script = config.project_root / "scripts" / "synth.tcl"
    if not script.is_file():
        raise FlowError(f"Tcl flow script is missing: {script}")

    env = os.environ.copy()
    env.update(
        {
            "EDA_TOP": config.top,
            "EDA_SOURCE_MANIFEST": str(manifest),
            "EDA_OUTPUT_DIR": str(config.output_dir),
            "EDA_FLATTEN": "1" if config.flatten else "0",
            "EDA_YOSYS": yosys,
        }
    )

    version_result = subprocess.run(
        [yosys, "-V"], capture_output=True, text=True, check=False
    )
    raw_version = (version_result.stdout or version_result.stderr).strip().splitlines()[0]
    version_match = re.search(r"Yosys\s+[0-9][0-9A-Za-z.+-]*", raw_version)
    tool_version = version_match.group(0) if version_match else raw_version

    start = time.perf_counter()
    result = subprocess.run(
        [tclsh, str(script)],
        cwd=config.project_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = time.perf_counter() - start

    log_path = config.output_dir / "synthesis.log"
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise FlowError(
            f"Synthesis failed with exit code {result.returncode}. See {log_path}"
        )

    stats_path = config.output_dir / "stats.json"
    stats = read_yosys_stats(stats_path, config.top)
    summary_path = config.output_dir / "summary.md"
    write_summary(
        summary_path,
        design_name=config.name,
        top=config.top,
        tool_version=tool_version,
        elapsed_seconds=elapsed,
        stats=stats,
    )

    run_record = {
        "status": "PASS",
        "design": config.name,
        "top": config.top,
        "tool": tool_version,
        "elapsed_seconds": round(elapsed, 6),
        "statistics": stats,
        "outputs": {
            "netlist": "netlist.v",
            "statistics": "stats.json",
            "log": "synthesis.log",
            "summary": "summary.md",
        },
    }
    run_path = config.output_dir / "run.json"
    run_path.write_text(
        json.dumps(run_record, indent=2) + "\n", encoding="utf-8"
    )

    proof_dir = config.project_root / "reports"
    proof_dir.mkdir(exist_ok=True)
    shutil.copy2(summary_path, proof_dir / "latest_summary.md")
    shutil.copy2(run_path, proof_dir / "latest_run.json")
    return summary_path


def clean_flow(config: FlowConfig) -> None:
    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)
