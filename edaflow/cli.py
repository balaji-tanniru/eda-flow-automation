from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .report import ReportError
from .runner import FlowError, clean_flow, run_flow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eda-flow", description="Run a reproducible Python/Tcl RTL synthesis flow."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("validate", "clean"):
        command = subparsers.add_parser(name)
        command.add_argument("config", type=Path)

    run = subparsers.add_parser("run")
    run.add_argument("config", type=Path)
    run.add_argument("--yosys", help="Yosys executable name or path")
    run.add_argument("--tclsh", help="Tcl shell executable name or path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "validate":
            print(f"PASS: configuration is valid for top '{config.top}'")
        elif args.command == "clean":
            clean_flow(config)
            print(f"PASS: removed {config.output_dir}")
        else:
            summary = run_flow(config, args.yosys, args.tclsh)
            print(f"PASS: synthesis completed for '{config.name}'")
            print(f"Summary: {summary}")
    except (ConfigError, FlowError, ReportError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0
