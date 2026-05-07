from __future__ import annotations

import argparse
import sys
from pathlib import Path


SHARED_SRC = Path(__file__).resolve().parents[2] / "shared_util" / "src"
if str(SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(SHARED_SRC))

from adjacencies_merge import merge_adjacencies
from cfg_utils import read_cfg
from location_templates_merge import merge_location_templates


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    injector_root = script_dir.parent
    tools_dir = injector_root.parent
    injector_map_data = injector_root / "map_data"
    cfg_path = tools_dir / "lhrmod.cfg"

    parser = argparse.ArgumentParser(
        description=(
            "Merge vanilla EU5 map_data files with LHRMod tools/map_data_injector overrides."
        )
    )
    parser.add_argument(
        "--game-map-data",
        type=Path,
        default=None,
        help="Optional override for vanilla game/in_game/map_data directory.",
    )
    parser.add_argument(
        "--mod-map-data",
        type=Path,
        default=None,
        help="Optional override for LHRMod/in_game/map_data directory.",
    )

    args = parser.parse_args()

    cfg = read_cfg(cfg_path)
    game_map_data = args.game_map_data or (cfg["game_root"] / "in_game" / "map_data")
    mod_map_data = args.mod_map_data or (cfg["mod_root"] / "in_game" / "map_data")

    if not game_map_data.exists():
        raise FileNotFoundError(f"Vanilla map_data path not found: {game_map_data}")
    if not mod_map_data.exists():
        raise FileNotFoundError(f"Mod map_data path not found: {mod_map_data}")
    if not injector_map_data.exists():
        raise FileNotFoundError(f"Injector map_data path not found: {injector_map_data}")

    location_updated = merge_location_templates(
        base_path=game_map_data / "location_templates.txt",
        injector_path=injector_map_data / "location_templates.txt",
        output_path=mod_map_data / "location_templates.txt",
    )
    adjacencies_updated = merge_adjacencies(
        base_path=game_map_data / "adjacencies.csv",
        injector_path=injector_map_data / "adjacencies.csv",
        output_path=mod_map_data / "adjacencies.csv",
    )

    if location_updated or adjacencies_updated:
        print("Updated mod map_data files:")
        if location_updated:
            print(f"- {mod_map_data / 'location_templates.txt'}")
        if adjacencies_updated:
            print(f"- {mod_map_data / 'adjacencies.csv'}")
    else:
        print("All map_data outputs are already up to date.")


if __name__ == "__main__":
    main()