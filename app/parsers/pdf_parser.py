"""
Парсинг техпаспорта в формате .pdf.

В отличие от .docx, PDF-бланк техпаспорта не хранит структуру
"абзац -> таблица" явно: pdfplumber видит только координаты символов.
Табличная сетка на этих бланках (боковые поля "Инв.№", вертикальные
подписи, рамки со штампом) при автодетекте таблиц (extract_tables)
разваливается и даёт мусор.

Поэтому вместо восстановления сетки используется другой путь, который на
практике для этого типа бланков надёжнее:

1. Берется линейный текст страницы (extract_text) — в нём, несмотря на
   потерю столбцов, сохраняется порядок содержимого ячеек.
2. Нарезается текст по заголовкам вида "Таблица 3.2 – ...".
3. Каждый такой фрагмент кладется как RawTable с ОДНОЙ псевдострокой,
   содержащей весь блок текста целиком (rows = [[blob]]).

Дальше извлечение конкретных значений из этого блока — задача
регэксп-экстракторов уровня normalize.py, которые уже умеют работать
с текстом таблицы, а не с её геометрией.
"""
from __future__ import annotations

import re

import pdfplumber

from .base import RawDocument, RawParagraph, RawTable, clean_text

_TABLE_CAPTION_RE = re.compile(r"Таблица\s+\d+\.\d+\s*[-–—].*")

# Строки, с которых типично начинается свободный описательный текст сразу
# после последней таблицы на странице (характеристики грузовых фронтов,
# заключительные фразы техпаспорта и т.п.). Если такая строка встречается
# внутри хвоста последней найденной таблицы — обрезается таблица по ней,
# а остаток отдается отдельным абзацем, иначе описательный текст ошибочно
# склеивается с последней таблицей на странице.
_PARAGRAPH_BREAK_RE = re.compile(
    r"(Технико-технологическая характеристика|"
    r"Технический паспорт составлен|"
    r"Данный технический паспорт|"
    r"Инженер геодезист|"
    r"Главный инженер|"
    r"Ведущий инженер|"
    r"Изм\.\s*Кол\.уч\.\s*Лист)"  # повторяющийся штамп бланка в подвале страницы
)


def parse_pdf(path: str) -> RawDocument:
    raw = RawDocument()

    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue
            _split_page_into_blocks(text, page_num, raw)

    return raw


def _split_page_into_blocks(text: str, page_num: int, raw: RawDocument) -> None:
    lines = text.split("\n")

    caption_positions: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        if _TABLE_CAPTION_RE.match(line.strip()):
            caption_positions.append((i, line.strip()))

    if not caption_positions:
        # На странице нет табличных блоков — считаем весь текст абзацем
        # (актуально для титульного листа, приложений с сертификатами и т.п.)
        joined = clean_text(" ".join(lines))
        if joined:
            raw.blocks.append(RawParagraph(text=joined, page_or_index=page_num))
        return

    # Текст до первой найденной подписи таблицы — обычный абзац
    pre = clean_text(" ".join(lines[: caption_positions[0][0]]))
    if pre:
        raw.blocks.append(RawParagraph(text=pre, page_or_index=page_num))

    for idx, (line_idx, caption) in enumerate(caption_positions):
        end = (
            caption_positions[idx + 1][0]
            if idx + 1 < len(caption_positions)
            else len(lines)
        )
        block_lines = lines[line_idx + 1 : end]
        blob = clean_text(" ".join(block_lines))

        break_m = _PARAGRAPH_BREAK_RE.search(blob)
        if break_m:
            table_part, para_part = blob[: break_m.start()], blob[break_m.start() :]
        else:
            table_part, para_part = blob, None

        raw.blocks.append(
            RawTable(caption=caption, rows=[[table_part]], page_or_index=page_num)
        )
        if para_part:
            raw.blocks.append(RawParagraph(text=para_part, page_or_index=page_num))
