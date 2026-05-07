from __future__ import annotations

import re
from pathlib import Path

from file_io import normalize_lines_for_write, read_text_lines, write_text_lines


ENTRY_KEY_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=")
LEGACY_VANILLA_MARKER = "START VANILLA"


def parse_location_keys(lines: list[str]) -> set[str]:
    # keys are the location IDs on lines like: some_id = { whatever }
    keys: set[str] = set()
    for line in lines:
        match = ENTRY_KEY_RE.match(line)
        if match:
            keys.add(match.group(1))
    return keys


def get_location_injector_overrides(lines: list[str]) -> list[str]:
    for idx, line in enumerate(lines):
        if LEGACY_VANILLA_MARKER in line:
            return lines[:idx]
    return lines


def merge_location_templates(base_path: Path, injector_path: Path, output_path: Path) -> bool:
    base_lines = read_text_lines(base_path)
    injector_lines = get_location_injector_overrides(read_text_lines(injector_path))

    injector_keys = parse_location_keys(injector_lines)

    filtered_base: list[str] = []
    removed_count = 0
    
    # any base entries that we see are removed if we have that key in our list
    # we will readd the modified one later at the bottom
    for line in base_lines:
        match = ENTRY_KEY_RE.match(line)
        if match and match.group(1) in injector_keys:
            removed_count += 1
            continue
        filtered_base.append(line)

    while filtered_base and filtered_base[-1] == "":
        filtered_base.pop()

    merged = filtered_base + [
        "",
        "# LHRMod injected entries from tools/map_data_injector/map_data/location_templates.txt",
    ]
    merged.extend(injector_lines)

    normalized_merged = normalize_lines_for_write(merged)
    if output_path.exists() and read_text_lines(output_path) == normalized_merged:
        print("location_templates.txt: up to date")
        return False

    write_text_lines(output_path, merged)
    print(
        "location_templates.txt: "
        f"removed {removed_count} duplicate base entries, appended {len(injector_lines)} lines"
    )
    return True