"""
Связывает воедино: определение формата -> конвертация (если .doc) ->
формато-специфичный парсер -> нормализация -> маппинг в JSON инструкции.

Это единственная функция, которую должен вызывать внешний код — она не знает про FastAPI/HTTP вообще.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from .converters import detect_format, ensure_docx
from .extraction.narrative import extract_narrative
from .extraction.normalize import normalize
from .extraction.section_mapping import build_instruction_json
from .extraction.tables import extract_tables
from .parsers.docx_parser import parse_docx
from .parsers.pdf_parser import parse_pdf


def parse_tech_passport(path: str, original_filename: str | None = None) -> dict:
    """
    path — путь к файлу на диске (.doc / .docx / .pdf)
    original_filename — как называть источник в meta.source_file
    """
    fmt = detect_format(path)
    display_name = original_filename or Path(path).name

    with tempfile.TemporaryDirectory(prefix="tp_convert_") as tmpdir:
        if fmt == ".doc":
            docx_path = ensure_docx(path, workdir=tmpdir)
            raw = parse_docx(docx_path)
            source_format = "doc"
        elif fmt == ".docx":
            raw = parse_docx(path)
            source_format = "docx"
        elif fmt == ".pdf":
            raw = parse_pdf(path)
            source_format = "pdf"
        else:
            raise ValueError(f"Неожиданный формат: {fmt}")

        data = normalize(raw, source_file=display_name, source_format=source_format)
        result = build_instruction_json(data)
        # Полный текст документа по разделам — для AI / сборки без «заглушек»
        result["source_narrative"] = extract_narrative(raw)
        # Структурированные таблицы (headers/rows) — для вставки в инструкцию
        result["source_tables"] = extract_tables(raw)
        return result
