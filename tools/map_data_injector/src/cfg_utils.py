from __future__ import annotations

import configparser
from pathlib import Path

# in case whover is running this has their game directory in a diff spot, just edit cfg
def read_game_map_data_from_cfg(cfg_path: Path) -> Path:
    # Expected format:
    # [paths]
    # game_map_data = <absolute path to game/in_game/map_data>
    parser = configparser.ConfigParser()
    parser.read(cfg_path, encoding="utf-8")

    if not parser.has_section("paths"):
        raise ValueError(f"Missing [paths] section in cfg: {cfg_path}")
    if not parser.has_option("paths", "game_map_data"):
        raise ValueError(f"Missing paths.game_map_data in cfg: {cfg_path}")

    configured = parser.get("paths", "game_map_data").strip()
    if not configured:
        raise ValueError(f"Empty paths.game_map_data in cfg: {cfg_path}")
    return Path(configured)