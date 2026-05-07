from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from file_io import read_text


TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|=|\{|\}")


@dataclass
class Node:
    name: str
    items: list[str] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)


def _parse_node(tokens: list[str], idx: int) -> tuple[Node, int]:
    name = tokens[idx]
    idx += 1
    if tokens[idx] != "=":
        raise ValueError(f"Expected '=' after {name}")
    idx += 1
    if tokens[idx] != "{":
        raise ValueError(f"Expected '{{' after {name}=")
    idx += 1

    node = Node(name=name)
    while idx < len(tokens):
        tok = tokens[idx]
        if tok == "}":
            idx += 1
            break

        if idx + 2 < len(tokens) and tokens[idx + 1] == "=" and tokens[idx + 2] == "{":
            child, idx = _parse_node(tokens, idx)
            node.children.append(child)
            continue

        if tok not in {"=", "{"}:
            node.items.append(tok)
        idx += 1

    return node, idx


def _flatten_locations(node: Node, out: dict[str, set[str]]) -> set[str]:
    locations = set(node.items)
    for child in node.children:
        locations.update(_flatten_locations(child, out))

    if node.name in out:
        out[node.name].update(locations)
    else:
        out[node.name] = set(locations)
    return locations


def parse_definitions_locations(definitions_path: Path) -> dict[str, set[str]]:
    text = read_text(definitions_path)
    tokens = TOKEN_RE.findall(text)

    idx = 0
    roots: list[Node] = []
    while idx < len(tokens):
        if idx + 2 < len(tokens) and tokens[idx + 1] == "=" and tokens[idx + 2] == "{":
            node, idx = _parse_node(tokens, idx)
            roots.append(node)
            continue
        idx += 1

    result: dict[str, set[str]] = {}
    for root in roots:
        _flatten_locations(root, result)
    return result
