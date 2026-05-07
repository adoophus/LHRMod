from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from file_io import read_text


DEFINE_POP_RE = re.compile(r"^\s*define_pop\s*=\s*\{(.*)\}\s*$")
KV_RE = re.compile(r"([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_.-]+)")


@dataclass
class PopEntry:
    pop_type: str
    size: float
    culture: str
    religion: str


@dataclass
class PopsData:
    order: list[str]
    raw_blocks: dict[str, str]
    parsed_blocks: dict[str, list[PopEntry]]


def _extract_location_blocks(text: str) -> tuple[list[str], dict[str, str]]:
    start = text.find("locations={")
    if start == -1:
        raise ValueError("locations={ not found in pops file")

    body = text[start + len("locations={") :]
    order: list[str] = []
    blocks: dict[str, str] = {}

    i = 0
    n = len(body)
    while i < n:
        if body[i] == "}":
            break

        key_match = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*\{", body[i:])
        if not key_match:
            i += 1
            continue

        key = key_match.group(1)
        block_start = i + key_match.start()
        j = i + key_match.end()
        depth = 1

        while j < n and depth > 0:
            ch = body[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            j += 1

        block = body[block_start:j].strip()
        order.append(key)
        blocks[key] = "\n".join(line.rstrip() for line in block.splitlines()).strip()
        i = j

    return order, blocks


def _parse_pop_entries(block_text: str) -> list[PopEntry]:
    entries: list[PopEntry] = []
    for line in block_text.splitlines():
        m = DEFINE_POP_RE.match(line)
        if not m:
            continue
        pairs = {k: v for k, v in KV_RE.findall(m.group(1))}
        if not {"type", "size", "culture", "religion"}.issubset(pairs):
            continue
        entries.append(
            PopEntry(
                pop_type=pairs["type"],
                size=float(pairs["size"]),
                culture=pairs["culture"],
                religion=pairs["religion"],
            )
        )
    return entries


def parse_pops_file(path: Path) -> PopsData:
    text = read_text(path)
    order, raw_blocks = _extract_location_blocks(text)
    parsed = {k: _parse_pop_entries(v) for k, v in raw_blocks.items()}
    return PopsData(order=order, raw_blocks=raw_blocks, parsed_blocks=parsed)


def _fmt_size(size: float) -> str:
    return f"{size:.3f}"


def serialize_block(key: str, entries: list[PopEntry]) -> str:
    lines = [f"{key} = {{"]
    for e in entries:
        lines.append(
            "\tdefine_pop = {\ttype = "
            f"{e.pop_type}\tsize = {_fmt_size(e.size)}\tculture = {e.culture}\treligion = {e.religion} "
            "}"
        )
    lines.append("}")
    return "\n".join(lines)


def pops_signature(entries: list[PopEntry]) -> tuple[tuple[str, float, str, str], ...]:
    return tuple((e.pop_type, round(e.size, 6), e.culture, e.religion) for e in entries)
