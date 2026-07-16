"""
HTTP-обвязка сервиса парсинга техпаспортов.

POST /parse — принимает multipart-файл (doc/docx/pdf), возвращает JSON
со структурой, повторяющей заголовки инструкции (см.
app/extraction/section_mapping.py).

Запуск:
    uvicorn app.main:app --reload --port 8000

Пример вызова:
    curl -F "file=@ТП_ООО_МеталлСнаб.pdf" http://localhost:8000/parse
"""


from __future__ import annotations
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path

from .converters import ConversionError, UnsupportedFormatError
from .pipeline import parse_tech_passport

app = FastAPI(
    title="TP Parser Service",
    description="Извлекает структурированные данные из техпаспорта ж.д. пути "
                "необщего пользования (doc/docx/pdf) в JSON, повторяющий структуру "
                "заголовков инструкции о порядке обслуживания и организации движения.",
    version="0.1.0",
)


MAX_FILE_SIZE = 50 * 1024 * 1024


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/parse")
async def parse_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in (".doc", ".docx", ".pdf"):
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла '{suffix}'. Ожидается .doc, .docx или .pdf.",
        )

    # Проверяем размер файла
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)} МБ"
        )

    with tempfile.TemporaryDirectory(prefix="tp_upload_") as tmpdir:
        tmp_path = Path(tmpdir) / (file.filename or f"upload{suffix}")
        tmp_path.write_bytes(content)

        try:
            result = parse_tech_passport(str(tmp_path), original_filename=file.filename)
        except (UnsupportedFormatError, ConversionError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Ошибка разбора файла: {exc}") from exc

    return JSONResponse(content=result)