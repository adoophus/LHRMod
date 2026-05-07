from __future__ import annotations
from pathlib import Path
from file_io import normalize_lines_for_write, read_text_lines, write_text_lines

def parse_adjacency_key(row: str) -> tuple[str, str] | None:
    if not row.strip() or row.lstrip().startswith("#"):
        return None
    cols = row.split(";")
    if len(cols) < 2:
        return None
    left = cols[0].strip().lower()
    right = cols[1].strip().lower()
    if not left or not right:
        return None
    return left, right


def merge_adjacencies(base_path: Path, injector_path: Path, output_path: Path) -> bool:
    base_lines = read_text_lines(base_path)
    injector_lines = read_text_lines(injector_path)

    if not base_lines:
        raise ValueError(f"Base adjacencies file is empty: {base_path}")
    if not injector_lines:
        raise ValueError(f"Injector adjacencies file is empty: {injector_path}")

    header = base_lines[0]
    injector_data = injector_lines[1:] if injector_lines[0] == header else injector_lines

    injector_rows: list[str] = []
    injector_keys: set[tuple[str, str]] = set()
    for row in injector_data:
        key = parse_adjacency_key(row)
        if key is None:
            continue
        injector_rows.append(row)
        injector_keys.add(key)

    filtered_base = [header]
    removed_count = 0

    # this is for the From;To key
    for row in base_lines[1:]:
        key = parse_adjacency_key(row)
        if key is not None and key in injector_keys:
            removed_count += 1
            continue
        filtered_base.append(row)

    while filtered_base and filtered_base[-1] == "":
        filtered_base.pop()

    merged = filtered_base + injector_rows

    normalized_merged = normalize_lines_for_write(merged)
    if output_path.exists() and read_text_lines(output_path) == normalized_merged:
        print("adjacencies.csv: up to date")
        return False

    write_text_lines(output_path, merged)
    print(
        "adjacencies.csv: "
        f"removed {removed_count} duplicate base rows, appended {len(injector_rows)} rows"
    )
    return True