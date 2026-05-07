from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Rule:
    name: str
    operation: str
    value: float
    locations: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    subcontinents: list[str] = field(default_factory=list)
    continents: list[str] = field(default_factory=list)
    areas: list[str] = field(default_factory=list)
    provinces: list[str] = field(default_factory=list)
    pop_types: list[str] = field(default_factory=list)
    cultures: list[str] = field(default_factory=list)
    religions: list[str] = field(default_factory=list)
    exclude_locations: list[str] = field(default_factory=list)
    exclude_regions: list[str] = field(default_factory=list)
    exclude_areas: list[str] = field(default_factory=list)
    exclude_provinces: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parser for PDX script files
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r'#[^\n]*'           # line comment
    r'|"[^"]*"'          # quoted string
    r'|[^\s#"={}]+'      # bare token
    r'|[={}]'            # punctuation
)


def _tokenize(text: str) -> list[str]:
    return [m.group() for m in _TOKEN_RE.finditer(text) if not m.group().startswith("#")]


def _parse_block(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse a { ... } block starting just after the opening brace.
    Returns (dict, new_pos) where new_pos is after the closing brace."""
    result: dict[str, object] = {}
    while pos < len(tokens):
        tok = tokens[pos]
        if tok == "}":
            return result, pos + 1
        # expect: key = value  or  key = { ... }
        key = tok.strip('"')
        pos += 1
        if pos >= len(tokens) or tokens[pos] != "=":
            raise ValueError(f"Expected '=' after key '{key}'")
        pos += 1  # skip '='
        if pos >= len(tokens):
            raise ValueError(f"Missing value for key '{key}'")
        if tokens[pos] == "{":
            pos += 1
            items: list[str] = []
            while pos < len(tokens) and tokens[pos] != "}":
                items.append(tokens[pos].strip('"'))
                pos += 1
            pos += 1  # skip '}'
            result[key] = items
        else:
            result[key] = tokens[pos].strip('"')
            pos += 1
    raise ValueError("Unexpected end of file inside block")


def _parse_file(text: str) -> list[tuple[str, dict]]:
    """Return list of (rule_name, fields_dict) parsed from a PDX-script file."""
    tokens = _tokenize(text)
    entries: list[tuple[str, dict]] = []
    pos = 0
    while pos < len(tokens):
        name = tokens[pos].strip('"')
        pos += 1
        if pos >= len(tokens) or tokens[pos] != "=":
            raise ValueError(f"Expected '=' after rule name '{name}'")
        pos += 1
        if pos >= len(tokens) or tokens[pos] != "{":
            raise ValueError(f"Expected '{{' for rule '{name}'")
        pos += 1
        block, pos = _parse_block(tokens, pos)
        entries.append((name, block))
    return entries


# ---------------------------------------------------------------------------
# API that is expected by population_adjuster.py
# ---------------------------------------------------------------------------

_LIST_KEYS = {
    "locations", "tags", "regions", "subcontinents",
    "continents", "areas", "provinces",
    "pop_types", "cultures", "religions",
}


def _to_list(val: object) -> list[str]:
    if val is None:
        return []
    if isinstance(val, list):
        return [str(v) for v in val]
    return [str(val)]


def load_rules_from_dir(pops_dir: Path) -> list[Rule]:
    """Load all *.txt files from pops_dir, sorted by filename, and return merged rule list."""
    rules: list[Rule] = []
    txt_files = sorted(pops_dir.glob("*.txt"))
    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8")
        entries = _parse_file(text)
        for name, fields in entries:
            # PDX-style: operation keyword IS the key (multiply/add/set)
            # we kinda want to mimic it as much as possible
            operation: str | None = None
            value: float = 0.0
            for op_key in ("multiply", "add", "set"):
                if op_key in fields:
                    operation = op_key
                    value = float(str(fields[op_key]))
                    break
            if operation is None:
                raise ValueError(
                    f"Rule '{name}' in {txt_file.name} must specify one of: multiply, add, set"
                )
            rules.append(Rule(
                name=name,
                operation=operation,
                value=value,
                locations=_to_list(fields.get("locations")),
                tags=_to_list(fields.get("tags")),
                regions=_to_list(fields.get("regions")),
                subcontinents=_to_list(fields.get("subcontinents")),
                continents=_to_list(fields.get("continents")),
                areas=_to_list(fields.get("areas")),
                provinces=_to_list(fields.get("provinces")),
                pop_types=_to_list(fields.get("pop_types")),
                cultures=_to_list(fields.get("cultures")),
                religions=_to_list(fields.get("religions")),
                exclude_locations=_to_list(fields.get("exclude_locations")),
                exclude_regions=_to_list(fields.get("exclude_regions")),
                exclude_areas=_to_list(fields.get("exclude_areas")),
                exclude_provinces=_to_list(fields.get("exclude_provinces")),
            ))
    return rules
