from __future__ import annotations

import argparse
from pathlib import Path

from adjacencies_merge import merge_adjacencies
from cfg_utils import read_game_map_data_from_cfg
from location_templates_merge import merge_location_templates


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    injector_root = script_dir.parent
    injector_map_data = injector_root / "map_data"
    default_mod_map_data = injector_root.parents[1] / "in_game" / "map_data"
    cfg_path = injector_root / "inject_map_data.cfg"

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
        default=default_mod_map_data,
        type=Path,
        help=(
            "Path to LHRMod/in_game/map_data directory. "
            f"Default: {default_mod_map_data}"
        ),
    )

    args = parser.parse_args()

    game_map_data = args.game_map_data
    if game_map_data is None:
        game_map_data = read_game_map_data_from_cfg(cfg_path)

    if not game_map_data.exists():
        raise FileNotFoundError(f"Vanilla map_data path not found: {game_map_data}")
    if not args.mod_map_data.exists():
        raise FileNotFoundError(f"Mod map_data path not found: {args.mod_map_data}")
    if not injector_map_data.exists():
        raise FileNotFoundError(f"Injector map_data path not found: {injector_map_data}")

    location_updated = merge_location_templates(
        base_path=game_map_data / "location_templates.txt",
        injector_path=injector_map_data / "location_templates.txt",
        output_path=args.mod_map_data / "location_templates.txt",
    )
    adjacencies_updated = merge_adjacencies(
        base_path=game_map_data / "adjacencies.csv",
        injector_path=injector_map_data / "adjacencies.csv",
        output_path=args.mod_map_data / "adjacencies.csv",
    )

    if location_updated or adjacencies_updated:
        print("Updated mod map_data files:")
        if location_updated:
            print(f"- {args.mod_map_data / 'location_templates.txt'}")
        if adjacencies_updated:
            print(f"- {args.mod_map_data / 'adjacencies.csv'}")
    else:
        print("All map_data outputs are already up to date.")


if __name__ == "__main__":
    main()