from __future__ import annotations

from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def read_text_lines(path: Path) -> list[str]:
    return read_text(path).splitlines()


def normalize_lines_for_write(lines: list[str]) -> list[str]:
    text = "\n".join(lines).rstrip("\n")
    if text == "":
        return []
    return text.splitlines()


def write_text_lines(path: Path, lines: list[str]) -> None:
    normalized = normalize_lines_for_write(lines)
    write_text(path, "\n".join(normalized) + "\n")
