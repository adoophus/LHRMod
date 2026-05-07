from __future__ import annotations

import argparse
import sys
from pathlib import Path


SHARED_SRC = Path(__file__).resolve().parents[2] / "shared_util" / "src"
if str(SHARED_SRC) not in sys.path:
    sys.path.insert(0, str(SHARED_SRC))

from definitions_parser import parse_definitions_locations
from cfg_utils import read_cfg
from file_io import read_text, write_text
from ownership_parser import parse_owned_locations_by_tag
from pops_parser import PopEntry, parse_pops_file, pops_signature, serialize_block
from rules_loader import Rule, load_rules_from_dir


def resolve_locations(
    rule: Rule,
    groups: dict[str, set[str]],
    owned_by_tag: dict[str, set[str]],
) -> set[str]:
    selected: set[str] = set(rule.locations)

    for tag in rule.tags:
        selected.update(owned_by_tag.get(tag, set()))

    for group_name in (
        list(rule.regions)
        + list(rule.subcontinents)
        + list(rule.continents)
        + list(rule.areas)
        + list(rule.provinces)
    ):
        selected.update(groups.get(group_name, set()))

    excluded: set[str] = set(rule.exclude_locations)
    for group_name in (
        list(rule.exclude_regions)
        + list(rule.exclude_areas)
        + list(rule.exclude_provinces)
    ):
        excluded.update(groups.get(group_name, set()))

    return selected - excluded


def pop_matches_filters(pop: PopEntry, rule: Rule) -> bool:
    if rule.pop_types and pop.pop_type not in rule.pop_types:
        return False
    if rule.cultures and pop.culture not in rule.cultures:
        return False
    if rule.religions and pop.religion not in rule.religions:
        return False
    return True


def apply_rule_to_pop(pop: PopEntry, rule: Rule) -> bool:
    if not pop_matches_filters(pop, rule):
        return False

    original = pop.size
    if rule.operation == "multiply":
        pop.size = pop.size * rule.value
    elif rule.operation == "add":
        pop.size = pop.size + rule.value
    elif rule.operation == "set":
        pop.size = rule.value
    else:
        raise ValueError(
            f"Unsupported operation '{rule.operation}' in rule '{rule.name}'. "
            "Use multiply, add, or set."
        )

    if pop.size < 0:
        pop.size = 0.0
    return round(original, 6) != round(pop.size, 6)


def build_output_text(
    base_order: list[str],
    base_raw_blocks: dict[str, str],
    changed_blocks: dict[str, str],
) -> str:
    lines: list[str] = ["locations={", ""]

    for key in base_order:
        if key in changed_blocks:
            continue
        lines.append(base_raw_blocks[key])

    if changed_blocks:
        lines.append("")
        lines.append("# LHRMod injected entries from tools/population_adjuster")
        lines.append("# Existing keys above were removed if overridden here.")
        lines.append("")

        ordered_changed = [k for k in base_order if k in changed_blocks]
        ordered_changed.extend(k for k in sorted(changed_blocks) if k not in base_raw_blocks)

        for key in ordered_changed:
            lines.append(changed_blocks[key])

    lines.append("")
    lines.append("}")
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate merged 06_pops.txt with population adjustments appended at bottom."
    )
    parser.add_argument(
        "--cfg",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "lhrmod.cfg",
        help="Path to lhrmod.cfg (default: tools/lhrmod.cfg)",
    )
    args = parser.parse_args()

    cfg_values = read_cfg(args.cfg)
    game_root = cfg_values["game_root"]
    mod_root = cfg_values["mod_root"]
    pops_dir = Path(__file__).resolve().parents[1] / "pops"

    base_pops_path = game_root / "main_menu" / "setup" / "start" / "06_pops.txt"
    out_pops_path = mod_root / "main_menu" / "setup" / "start" / "06_pops.txt"
    definitions_path = game_root / "in_game" / "map_data" / "definitions.txt"
    game_start_dir = game_root / "main_menu" / "setup" / "start"
    mod_start_dir = mod_root / "main_menu" / "setup" / "start"

    print(f"Reading pops: {base_pops_path}")
    pops_data = parse_pops_file(base_pops_path)
    print(f"  {len(pops_data.order)} location blocks loaded")

    print(f"Reading definitions: {definitions_path}")
    groups = parse_definitions_locations(definitions_path)
    print(f"  {len(groups)} groups loaded")

    print("Reading country ownership files...")
    owned_by_tag = parse_owned_locations_by_tag(game_start_dir, mod_start_dir)
    print(f"  {len(owned_by_tag)} tags loaded")

    rules = load_rules_from_dir(pops_dir)
    if not rules:
        print(f"No rules found in {pops_dir}; nothing to do.")
        return

    mutable_blocks = {
        k: [PopEntry(e.pop_type, e.size, e.culture, e.religion) for e in v]
        for k, v in pops_data.parsed_blocks.items()
    }

    touched_locations: set[str] = set()
    total_changed_entries = 0

    for rule in rules:
        targets = resolve_locations(rule, groups, owned_by_tag)
        changed_by_rule = 0
        target_hits = 0

        for loc in targets:
            if loc not in mutable_blocks:
                continue
            target_hits += 1
            for pop in mutable_blocks[loc]:
                if apply_rule_to_pop(pop, rule):
                    changed_by_rule += 1
                    touched_locations.add(loc)

        total_changed_entries += changed_by_rule
        print(
            f"{rule.name}: targeted {target_hits} locations, changed {changed_by_rule} pop entries"
        )

    changed_blocks: dict[str, str] = {}
    for key in touched_locations:
        if pops_signature(mutable_blocks[key]) != pops_signature(pops_data.parsed_blocks[key]):
            changed_blocks[key] = serialize_block(key, mutable_blocks[key])

    print("Building output...")
    output_text = build_output_text(pops_data.order, pops_data.raw_blocks, changed_blocks)

    if out_pops_path.exists() and read_text(out_pops_path) == output_text:
        print("06_pops.txt: up to date")
        return

    write_text(out_pops_path, output_text)
    print(
        "06_pops.txt: wrote "
        f"{len(changed_blocks)} overridden location blocks (changed entries: {total_changed_entries})"
    )
    print(f"Output: {out_pops_path}")


if __name__ == "__main__":
    main()
