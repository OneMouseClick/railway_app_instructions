"""
Парсинг техпаспорта в формате .docx.

Обходим тело документа (document.xml body) строго по порядку
следования элементов <w:p> (абзац) и <w:tbl> (таблица), а не отдельно
"все параграфы" и "все таблицы" (как это делает python-docx по
умолчанию через .paragraphs/.tables) — иначе теряется связь
"эта таблица подписана вот этим абзацем прямо над ней".

Отдельный нюанс: не все проектные организации пишут подпись таблицы
одной строкой вида 'Таблица 3.2 – Толщина балластного слоя'. Шаблон с
маркировкой техпаспорта 'ТЧГП' разносит это на два абзаца подряд:

    Толщина балластного слоя
    Таблица 3.2

— то есть непосредственно перед таблицей стоит абзац, содержащий
ТОЛЬКО номер таблицы, а название находится в абзаце ПЕРЕД ним. Ниже
это учитывается: если последний абзац перед таблицей — это "голый"
номер, заголовок докручивается из абзаца, стоявшего перед ним.
"""
from __future__ import annotations

import re

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import RawDocument, RawParagraph, RawTable, clean_text

_BARE_TABLE_NUMBER_RE = re.compile(r"^Таблица\s+(\d+\.\d+)\.?\s*$", re.IGNORECASE)


def _build_caption(recent_paragraphs: list[str]) -> str | None:
    if not recent_paragraphs:
        return None
    last = recent_paragraphs[-1]
    bare_m = _BARE_TABLE_NUMBER_RE.match(last)
    if not bare_m:
        return last
    # заголовок таблицы — предыдущий абзац, если это не подпись другой
    # таблицы (случай двух таблиц подряд без промежуточного текста)
    if len(recent_paragraphs) >= 2:
        title = recent_paragraphs[-2]
        if _BARE_TABLE_NUMBER_RE.match(title) or re.match(r"^Таблица\s+\d", title, re.IGNORECASE):
            title = ""
    else:
        title = ""
    return f"Таблица {bare_m.group(1)} – {title}"


def parse_docx(path: str) -> RawDocument:
    document = Document(path)
    raw = RawDocument()

    # храним только последние 2 абзаца — этого достаточно, чтобы собрать
    # подпись что в "однострочном", что в "двухабзацном" формате шаблона
    recent_paragraphs: list[str] = []
    idx = 0

    body = document.element.body
    for child in body.iterchildren():
        idx += 1
        if child.tag.endswith("}p"):
            para = Paragraph(child, document)
            text = clean_text(para.text)
            if text:
                raw.blocks.append(RawParagraph(text=text, page_or_index=idx))
                recent_paragraphs.append(text)
                recent_paragraphs = recent_paragraphs[-2:]
        elif child.tag.endswith("}tbl"):
            table = Table(child, document)
            rows: list[list[str]] = []
            for row in table.rows:
                cells = [clean_text(c.text) for c in row.cells]
                rows.append(cells)
            caption = _build_caption(recent_paragraphs)
            raw.blocks.append(
                RawTable(caption=caption, rows=rows, page_or_index=idx)
            )
            # подпись не переиспользуем для следующей таблицы, если между
            # ними не было текста (две таблицы подряд)
            recent_paragraphs = []

    return raw
