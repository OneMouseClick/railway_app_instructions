"""Extract structured tables from RawDocument for AI / assembler."""

from __future__ import annotations

import re
from typing import Any

from ..parsers.base import RawDocument, RawTable

_TABLE_CAP_RE = re.compile(
    r"таблица\s+(\d+(?:\.\d+)*)\s*[–\-:.]?\s*(.*)$",
    re.IGNORECASE,
)

# Подколонки типичной двухрядной шапки ГОСТ-таблиц
_SUBHEADER_TOKENS = {
    "от",
    "до",
    "полная",
    "полезная",
    "право",
    "лево",
    "право / лево",
    "тип",
    "кол-во",
    "количество",
}

# Служебные колонки, которые в инструкции только портят вёрстку
_DROP_HEADER_RE = re.compile(
    r"^(подпись|ф\.?\s*и\.?\s*о\.?.*|дата внесения изменений)$",
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
    width = max(len(r) for r in rows)
    return [r + [""] * (width - len(r)) for r in rows]


def _is_subheader_row(row: list[str], header_row: list[str]) -> bool:
    """Вторая строка шапки: «от/до/полная…» или повтор «№ пути»."""
    nonempty = [c.strip().lower() for c in row if c.strip()]
    if not nonempty:
        return False
    token_hits = sum(1 for c in nonempty if c in _SUBHEADER_TOKENS or c.startswith("от ") or c.startswith("до "))
    if token_hits >= 1 and token_hits >= max(1, len(nonempty) // 3):
        return True
    # повтор заголовков первой строки (merged cells в Word)
    same = sum(
        1
        for a, b in zip(row, header_row)
        if a.strip() and b.strip() and a.strip().lower() == b.strip().lower()
    )
    if same >= max(2, len(nonempty) // 2) and any(c in _SUBHEADER_TOKENS for c in nonempty):
        return True
    if row[0].strip().lower() in {"№ пути", "№", "n пути"} and any(
        c in _SUBHEADER_TOKENS for c in nonempty
    ):
        return True
    return False


def _merge_two_header_rows(top: list[str], bottom: list[str]) -> list[str]:
    """Склеивает двухрядную шапку: Граница путей + от → «Граница от»."""
    merged: list[str] = []
    for i, (a, b) in enumerate(zip(top, bottom)):
        a, b = a.strip(), b.strip()
        prev_top = top[i - 1].strip() if i > 0 else ""
        if not a and not b:
            merged.append("")
        elif not a:
            merged.append(b)
        elif not b or b.lower() == a.lower():
            merged.append(a)
        elif a.lower() == prev_top.lower() and b.lower() in _SUBHEADER_TOKENS:
            # продолжение объединённой ячейки: берём родителя + уточнение
            merged.append(f"{a} ({b})")
        elif b.lower() in _SUBHEADER_TOKENS:
            merged.append(f"{a} ({b})")
        else:
            merged.append(b)
    return merged


def _drop_useless_columns(
    headers: list[str], body: list[list[str]]
) -> tuple[list[str], list[list[str]]]:
    if not headers:
        return headers, body

    keep: list[int] = []
    for idx, header in enumerate(headers):
        h = header.strip()
        if not h:
            # пустой заголовок — оставляем, только если в колонке есть данные
            if any((row[idx].strip() if idx < len(row) else "") for row in body):
                keep.append(idx)
            continue
        if _DROP_HEADER_RE.match(h):
            continue
        # колонка «Подпись» без данных
        if "подпис" in h.lower() and not any(
            (row[idx].strip() if idx < len(row) else "") for row in body
        ):
            continue
        keep.append(idx)

    if not keep:
        return headers, body

    new_headers = [headers[i] for i in keep]
    new_body = [[(row[i] if i < len(row) else "") for i in keep] for row in body]
    return new_headers, new_body


def _split_headers(rows: list[list[str]]) -> tuple[list[str], list[list[str]]]:
    if not rows:
        return [], []
    if len(rows) == 1:
        return [], rows

    if _is_subheader_row(rows[1], rows[0]):
        headers = _merge_two_header_rows(rows[0], rows[1])
        body = rows[2:]
        if not body:
            return headers, []
        return headers, body

    headers = rows[0]
    body = rows[1:]
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

        # Без номера «Таблица N.M» — обычно шапка/мусор
        if not number:
            continue

        title = f"Таблица {number} – {title_tail}" if title_tail else f"Таблица {number}"
        if number in seen:
            continue
        seen.add(number)

        headers, body = _split_headers(rows)
        if not body:
            continue
        headers, body = _drop_useless_columns(headers, body)
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
