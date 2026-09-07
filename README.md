# EDA Flow Automation

## Verification status

`PYTHONPATH=. python -m pytest -q` was executed in this repair environment and completed with 10 passing tests. Yosys synthesis and Verilator lint were not executed here because those tools were not installed in this environment.

## Repository

This repository contains the RTL/testbench/automation sources for the project. Review fixes are summarized in the package-level `CHANGES.md`.

# Python/Tcl EDA Flow Automation

[![EDA Flow CI](https://github.com/balaji-tanniru/eda-flow-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/balaji-tanniru/eda-flow-automation/actions/workflows/ci.yml)

I built this project to automate a small RTL synthesis flow. A YAML file describes the design, Python validates the inputs and controls the run, and Tcl sends the synthesis steps to Yosys.

The example design is a parameterized SystemVerilog event counter. The same flow can run another design by changing the YAML configuration.

## Flow

1. Read and validate the YAML configuration.
2. Check that the RTL files and top module are provided.
3. Pass the design information from Python to Tcl.
4. Run RTL synthesis and design checks in Yosys.
5. Generate a synthesized netlist, log, statistics and summary report.
6. Repeat the same tests automatically in GitHub Actions.

## Tools

- Python 3.10 or newer
- Tcl
- Yosys
- SystemVerilog
- Pytest
- GitHub Actions

## Quick Start

On Ubuntu or WSL, install the required system tools:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv tcl yosys git make
```

Create the Python environment:

```bash
bash scripts/setup.sh
```

Run the tests and synthesis flow:

```bash
.venv/bin/python -m pytest
.venv/bin/python -m edaflow validate configs/counter.yaml
.venv/bin/python -m edaflow run configs/counter.yaml
```

The main outputs appear under `build/event_counter/`:

- `netlist.v` - synthesized Verilog netlist
- `stats.json` - machine-readable design statistics
- `synthesis.log` - complete Yosys run log
- `summary.md` - short human-readable result
- `run.json` - run status and output manifest

The short proof files are also copied to `reports/` so they can be committed to GitHub.

## Configuration Example

```yaml
design:
  name: parameterized_event_counter
  top: event_counter
  sources:
    - rtl/event_counter.sv

flow:
  output_dir: build/event_counter
  flatten: true
```

## Verified Result

The checked-in report under `reports/` was generated from a real run. GitHub Actions repeats the unit tests and synthesis flow after every push.

## What This Project Demonstrates

- Python automation and input validation
- Tcl-based EDA tool control
- SystemVerilog RTL processing
- Linux command-line workflow
- Reproducible reports and logs
- Unit, integration and CI testing
