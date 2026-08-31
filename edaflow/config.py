from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml


class ConfigError(ValueError):
    """Raised when a flow configuration is incomplete or invalid."""


@dataclass(frozen=True)
class FlowConfig:
    name: str
    top: str
    sources: tuple[Path, ...]
    output_dir: Path
    flatten: bool
    project_root: Path


def load_config(config_path: Path) -> FlowConfig:
    config_path = config_path.resolve()
    if not config_path.is_file():
        raise ConfigError(f"Configuration file does not exist: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML: {exc}") from exc

    project_root = config_path.parent.parent
    design = raw.get("design", {})
    flow = raw.get("flow", {})

    name = str(design.get("name", "")).strip()
    top = str(design.get("top", "")).strip()
    source_values = design.get("sources", [])
    output_value = str(flow.get("output_dir", "")).strip()

    if not name:
        raise ConfigError("design.name is required")
    if not top:
        raise ConfigError("design.top is required")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", top):
        raise ConfigError("design.top must be a valid Verilog identifier")
    if not isinstance(source_values, list) or not source_values:
        raise ConfigError("design.sources must contain at least one RTL file")
    if not output_value:
        raise ConfigError("flow.output_dir is required")

    sources = tuple((project_root / str(item)).resolve() for item in source_values)
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise ConfigError("Missing RTL source(s): " + ", ".join(missing))

    output_dir = (project_root / output_value).resolve()
    try:
        output_dir.relative_to(project_root)
    except ValueError as exc:
        raise ConfigError("flow.output_dir must stay inside the project") from exc

    return FlowConfig(
        name=name,
        top=top,
        sources=sources,
        output_dir=output_dir,
        flatten=bool(flow.get("flatten", True)),
        project_root=project_root,
    )
