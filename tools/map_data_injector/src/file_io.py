from __future__ import annotations

from pathlib import Path


def read_text_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def normalize_lines_for_write(lines: list[str]) -> list[str]:
    text = "\n".join(lines).rstrip("\n")
    if text == "":
        return []
    return text.splitlines()


def write_text_lines(path: Path, lines: list[str]) -> None:
    normalized = normalize_lines_for_write(lines)
    path.write_text("\n".join(normalized) + "\n", encoding="utf-8")