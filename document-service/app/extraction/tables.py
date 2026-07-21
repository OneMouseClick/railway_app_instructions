"""Extract structured tables from RawDocument for AI / assembler."""

from __future__ import annotations

import re
from typing import Any

from ..parsers.base import RawDocument, RawTable

_TABLE_CAP_RE = re.compile(
    r"таблица\s+(\d+(?:\.\d+)*)\s*[–\-:.]?\s*(.*)$",
    re.IGNORECASE,
)


def _normalize_rows(table: RawTable) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table.rows:
        cells = [(" ".join(str(c).split()) if c is not None else "") for c in row]
        if any(cells):
            rows.append(cells)
    if not rows:
        return []
    # выравниваем ширину по максимальному числу колонок
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]


def _split_headers(rows: list[list[str]]) -> tuple[list[str], list[list[str]]]:
    if not rows:
        return [], []
    if len(rows) == 1:
        return [], rows
    headers = rows[0]
    body = rows[1:]
    # если «шапка» почти пустая — считаем всё данными
    if sum(1 for h in headers if h.strip()) < 2:
        return [], rows
    return headers, body


def extract_tables(raw: RawDocument, *, max_rows: int = 60) -> list[dict[str, Any]]:
    """
    Возвращает список:
    {number, title, headers, rows} — формат, совместимый с assembler Table.
    """
    result: list[dict[str, Any]] = []
    seen: set[str] = set()

    for table in raw.tables():
        rows = _normalize_rows(table)
        if not rows:
            continue

        caption = (table.caption or "").strip()
        number = ""
        title_tail = caption
        match = _TABLE_CAP_RE.search(caption) if caption else None
        if match:
            number = match.group(1).strip()
            title_tail = (match.group(2) or "").strip()

        # Без номера «Таблица N.M» — обычно шапка/мусор (инвентарный номер и т.п.)
        if not number:
            continue

        title = (
            f"Таблица {number} – {title_tail}" if title_tail
            else f"Таблица {number}"
        )
        if number in seen:
            continue
        seen.add(number)

        headers, body = _split_headers(rows)
        if not body:
            continue

        result.append(
            {
                "number": number,
                "title": title,
                "headers": headers,
                "rows": body[:max_rows],
            }
        )

    return result
