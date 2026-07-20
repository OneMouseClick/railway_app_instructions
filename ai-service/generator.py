"""Instruction generation: real GigaChat RAG or deterministic mock for E2E."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

log = logging.getLogger(__name__)

SECTIONS = [
    "ОБЩАЯ ХАРАКТЕРИСТИКА ПУТИ НЕОБЩЕГО ПОЛЬЗОВАНИЯ",
    "ПОРЯДОК ПОДАЧИ И УБОРКИ ВАГОНОВ",
    "МАНЕВРОВАЯ РАБОТА",
    "ЗАКРЕПЛЕНИЕ ВАГОНОВ",
    "ТЕХНИКА БЕЗОПАСНОСТИ",
]


def _use_mock() -> bool:
    flag = os.getenv("AI_MOCK", "true").lower()
    if flag in ("1", "true", "yes"):
        return True
    creds = os.getenv("GIGACHAT_CREDENTIALS", "")
    return not creds or creds == "YOUR_GIGACHAT_TOKEN_HERE"


def _summarize_passport(passport_data: dict[str, Any]) -> str:
    meta = passport_data.get("meta") or {}
    bits = [
        f"станция: {meta.get('station_name') or 'н/д'}",
        f"организация: {meta.get('company_name') or 'н/д'}",
        f"пути: {meta.get('path_numbers') or 'н/д'}",
    ]
    return "; ".join(bits)


def mock_generate(passport_data: dict[str, Any]) -> dict[str, Any]:
    meta = passport_data.get("meta") or {}
    station = meta.get("station_name") or "Неизвестная станция"
    summary = _summarize_passport(passport_data)

    document_sections = {}
    for section in SECTIONS:
        document_sections[section] = (
            f"{section}\n\n"
            f"Настоящий раздел инструкции подготовлен автоматически для станции «{station}».\n"
            f"Исходные данные техпаспорта: {summary}.\n\n"
            f"Раздел содержит базовые требования к организации движения и обслуживанию "
            f"пути необщего пользования. При наличии полного LLM-контура текст "
            f"заменяется результатом RAG-генерации."
        )

    return {
        "status": "success",
        "station": station,
        "document_sections": document_sections,
        "validation_errors": {},
        "mode": "mock",
    }


def real_generate(passport_data: dict[str, Any]) -> dict[str, Any]:
    from ai_engine import StationInstructionAI

    creds = os.getenv("GIGACHAT_CREDENTIALS", "")
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    ai = StationInstructionAI(gigachat_credentials=creds, qdrant_url=qdrant_url)

    meta = passport_data.get("meta") or {}
    station_name = meta.get("station_name", "Неизвестная станция")

    document_sections: dict[str, str] = {}
    validation_errors: dict[str, str] = {}

    for section in SECTIONS:
        try:
            document_sections[section] = ai.generate_section(section, passport_data)
        except Exception as exc:  # noqa: BLE001
            log.exception("AI section failed: %s", section)
            document_sections[section] = "[ОШИБКА ГЕНЕРАЦИИ СЕРВИСОМ]"
            validation_errors[section] = str(exc)

    return {
        "status": "success" if not validation_errors else "completed_with_errors",
        "station": station_name,
        "document_sections": document_sections,
        "validation_errors": validation_errors,
        "mode": "gigachat",
    }


def generate_instruction(passport_data: dict[str, Any]) -> dict[str, Any]:
    if _use_mock():
        log.info("AI_MOCK enabled — using deterministic generator")
        return mock_generate(passport_data)
    log.info("Using GigaChat RAG generator")
    return real_generate(passport_data)


def debug_dump(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)[:500]
