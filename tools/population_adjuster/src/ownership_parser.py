from __future__ import annotations

import re
from pathlib import Path

from file_io import read_text


TAG_BLOCK_RE = re.compile(r"\b([A-Z0-9]{2,4})\s*=\s*\{")
OWN_CONTROL_BLOCK_RE = re.compile(r"\b(own_control_[A-Za-z0-9_]+)\s*=\s*\{")
LOCATION_TOKEN_RE = re.compile(r"\b[a-z0-9_]+\b")


def _extract_brace_block(text: str, brace_open_idx: int) -> str:
    depth = 1
    i = brace_open_idx + 1
    while i < len(text) and depth > 0:
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    return text[brace_open_idx + 1 : i - 1]


def _parse_tag_locations_in_text(text: str) -> dict[str, set[str]]:
    by_tag: dict[str, set[str]] = {}

    for m in TAG_BLOCK_RE.finditer(text):
        tag = m.group(1)
        block_text = _extract_brace_block(text, m.end() - 1)

        owned: set[str] = set()
        for om in OWN_CONTROL_BLOCK_RE.finditer(block_text):
            own_block = _extract_brace_block(block_text, om.end() - 1)
            owned.update(LOCATION_TOKEN_RE.findall(own_block))

        if owned:
            by_tag[tag] = owned

    return by_tag


def _collect_country_files(start_dir: Path) -> list[Path]:
    if not start_dir.exists():
        return []
    return sorted(start_dir.glob("*10_countries*.txt"))


def parse_owned_locations_by_tag(game_start_dir: Path, mod_start_dir: Path) -> dict[str, set[str]]:
    merged: dict[str, set[str]] = {}

    # we have to load the game files first
    # and then inject the edited mod files over it so we can recognise
    # any pop changes over adjusted countries
    game_files = _collect_country_files(game_start_dir)
    mod_files = _collect_country_files(mod_start_dir)
    total = len(game_files) + len(mod_files)
    done = 0
    for path in game_files:
        merged.update(_parse_tag_locations_in_text(read_text(path)))
        done += 1
        print(f"  [{done}/{total}] {path.name}")
    for path in mod_files:
        merged.update(_parse_tag_locations_in_text(read_text(path)))
        done += 1
        print(f"  [{done}/{total}] {path.name} (mod override)")

    return merged
