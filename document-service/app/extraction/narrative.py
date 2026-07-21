"""Extract readable narrative sections from a raw document for AI / assembler."""

from __future__ import annotations

import re
from typing import Any

from ..parsers.base import RawDocument, RawParagraph, RawTable

_HEADER_RE = re.compile(
    r"^(раздел\s+\d+|глава\s+\d+|приложение\s+[а-яa-z0-9]+|"
    r"общая характеристика|порядок подачи|маневро|закреплени|"
    r"техника безопасности|охрана труда)",
    re.IGNORECASE,
)


def _is_header(text: str) -> bool:
    t = text.strip()
    if not t or len(t) > 180:
        return False
    if t.isupper() and len(t) >= 8:
        return True
    if _HEADER_RE.search(t):
        return True
    # numbered section titles like "1. Общие положения"
    if re.match(r"^\d+(\.\d+)*\.?\s+\S+", t) and len(t) < 120:
        return True
    return False


def _table_to_text(table: RawTable) -> str:
    lines: list[str] = []
    if table.caption:
        lines.append(table.caption)
    for row in table.rows[:40]:
        cells = [c for c in row if c]
        if cells:
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def extract_narrative(raw: RawDocument) -> list[dict[str, Any]]:
    """
    Group paragraphs/tables into {title, text} blocks preserving document order.
    """
    sections: list[dict[str, Any]] = []
    title = "Введение"
    paragraphs: list[str] = []

    def flush() -> None:
        nonlocal paragraphs, title
        text = "\n".join(p for p in paragraphs if p).strip()
        if text:
            sections.append({"title": title, "text": text})
        paragraphs = []

    for block in raw.blocks:
        if isinstance(block, RawParagraph):
            text = (block.text or "").strip()
            if not text:
                continue
            if _is_header(text) and paragraphs:
                flush()
                title = text
            elif _is_header(text) and not paragraphs:
                title = text
            else:
                paragraphs.append(text)
        elif isinstance(block, RawTable):
            table_text = _table_to_text(block)
            if table_text:
                paragraphs.append(table_text)

    flush()

    # drop tiny noise sections
    return [s for s in sections if len(s["text"]) >= 40]
