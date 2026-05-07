from __future__ import annotations

import configparser
from pathlib import Path


def read_cfg(cfg_path: Path) -> dict[str, Path]:
    """Read [paths] section from lhrmod.cfg, returning game_root and mod_root as Paths."""
    parser = configparser.ConfigParser()
    parser.read(cfg_path, encoding="utf-8")

    if not parser.has_section("paths"):
        raise ValueError(f"Missing [paths] section in cfg: {cfg_path}")

    required = ["game_root", "mod_root"]
    values: dict[str, Path] = {}
    for key in required:
        if not parser.has_option("paths", key):
            raise ValueError(f"Missing paths.{key} in cfg: {cfg_path}")
        val = parser.get("paths", key).strip()
        if not val:
            raise ValueError(f"Empty paths.{key} in cfg: {cfg_path}")
        values[key] = Path(val)
    return values
