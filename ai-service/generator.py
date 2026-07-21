"""Instruction generation: GigaChat RAG, document narrative, or facts fallback."""

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

_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "ОБЩАЯ ХАРАКТЕРИСТИКА ПУТИ НЕОБЩЕГО ПОЛЬЗОВАНИЯ": (
        "общая характеристика",
        "общие сведения",
        "характеристика пути",
    ),
    "ПОРЯДОК ПОДАЧИ И УБОРКИ ВАГОНОВ": (
        "подачи и уборки",
        "подача и уборка",
        "порядок подачи",
    ),
    "МАНЕВРОВАЯ РАБОТА": ("маневро",),
    "ЗАКРЕПЛЕНИЕ ВАГОНОВ": ("закреплени",),
    "ТЕХНИКА БЕЗОПАСНОСТИ": ("техника безопасности", "охрана труда", "требования безопасности"),
}


def _creds() -> str:
    return os.getenv("GIGACHAT_CREDENTIALS", "").strip()


def _force_mock() -> bool:
    return os.getenv("AI_MOCK", "false").lower() in ("1", "true", "yes")


def _narrative(passport_data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = passport_data.get("source_narrative") or []
    return [x for x in raw if isinstance(x, dict) and str(x.get("text") or "").strip()]


def _narrative_substance(items: list[dict[str, Any]]) -> bool:
    total = sum(len(str(x.get("text") or "")) for x in items)
    return total >= 400 or len(items) >= 3


def _summarize_passport(passport_data: dict[str, Any]) -> str:
    meta = passport_data.get("meta") or {}
    bits = [
        f"станция: {meta.get('station_name') or 'н/д'}",
        f"организация: {meta.get('company_name') or 'н/д'}",
        f"пути: {meta.get('path_numbers') or 'н/д'}",
    ]
    return "; ".join(bits)


def _match_section_title(title: str) -> str | None:
    low = title.lower()
    for canonical, aliases in _SECTION_ALIASES.items():
        if any(a in low for a in aliases):
            return canonical

    # Numbered railway instruction outline: «РАЗДЕЛ 2…», «2.3. …», «Приложение …»
    if "раздел 1" in low or low.startswith("1."):
        return SECTIONS[0]
    if "раздел 2" in low or low.startswith("2."):
        return SECTIONS[1]
    if "раздел 3" in low or low.startswith("3."):
        return SECTIONS[2]
    if "раздел 4" in low or low.startswith("4."):
        return SECTIONS[3]
    if "раздел 5" in low or low.startswith("5.") or "охран" in low:
        return SECTIONS[4]
    return None


def from_narrative(passport_data: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    """Build instruction sections from the uploaded document's own text."""
    meta = passport_data.get("meta") or {}
    station = meta.get("station_name") or "Неизвестная станция"

    buckets: dict[str, list[str]] = {name: [] for name in SECTIONS}
    extras: list[str] = []

    for item in items:
        title = str(item.get("title") or "Раздел").strip()
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        body = f"{title}\n\n{text}" if title else text
        canonical = _match_section_title(title)
        if canonical:
            buckets[canonical].append(body)
        else:
            extras.append(body)

    document_sections: dict[str, str] = {}
    for name in SECTIONS:
        if buckets[name]:
            document_sections[name] = "\n\n".join(buckets[name])

    # If almost nothing mapped — distribute whole narrative across canonical sections
    if len(document_sections) < 2:
        document_sections = {}
        chunks = [f"{t}\n\n{x}" for t, x in ((i.get("title"), i.get("text")) for i in items) if x]
        if not chunks:
            chunks = ["Текст исходного документа не извлечён."]
        per = max(1, (len(chunks) + len(SECTIONS) - 1) // len(SECTIONS))
        idx = 0
        for name in SECTIONS:
            part = chunks[idx : idx + per]
            idx += per
            if part:
                document_sections[name] = "\n\n---\n\n".join(part)
            if idx >= len(chunks):
                break
    elif extras:
        document_sections["ДОПОЛНИТЕЛЬНО / ПРИЛОЖЕНИЯ"] = "\n\n---\n\n".join(extras)

    return {
        "status": "success",
        "station": station,
        "document_sections": document_sections,
        "validation_errors": {},
        "mode": "document_narrative",
    }


def from_facts(passport_data: dict[str, Any]) -> dict[str, Any]:
    """Compose sections from structured available leaves (tech passport facts)."""
    meta = passport_data.get("meta") or {}
    station = meta.get("station_name") or "Неизвестная станция"
    company = meta.get("company_name") or ""

    facts: list[str] = []
    for key, value in passport_data.items():
        if not key.startswith("section_") or not isinstance(value, dict):
            continue
        for leaf_id, leaf in value.items():
            if not isinstance(leaf, dict) or not leaf.get("available"):
                continue
            data = leaf.get("data")
            source = leaf.get("source") or ""
            facts.append(f"[{leaf_id}] {json.dumps(data, ensure_ascii=False)} (источник: {source})")

    facts_block = "\n".join(facts) if facts else "Структурированные факты техпаспорта почти не извлечены."

    document_sections = {}
    for section in SECTIONS:
        document_sections[section] = (
            f"{section}\n\n"
            f"Организация: {company or 'н/д'}. Станция примыкания: {station}.\n\n"
            f"На основании извлечённых данных исходного документа:\n{facts_block}\n\n"
            f"Раздел подготовлен в режиме фактов (без LLM). "
            f"Для полноценной генерации задайте GIGACHAT_CREDENTIALS и AI_MOCK=false."
        )

    return {
        "status": "success",
        "station": station,
        "document_sections": document_sections,
        "validation_errors": {},
        "mode": "facts",
    }


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
            f"Это MOCK-режим (AI_MOCK=true)."
        )

    return {
        "status": "success",
        "station": station,
        "document_sections": document_sections,
        "validation_errors": {},
        "mode": "mock",
    }


def _build_section_context(passport_data: dict[str, Any], section_name: str) -> str:
    """Compact context for LLM: meta + matching narrative chunks + available facts."""
    meta = passport_data.get("meta") or {}
    parts = [
        f"станция: {meta.get('station_name') or 'н/д'}",
        f"организация: {meta.get('company_name') or 'н/д'}",
        f"пути: {meta.get('path_numbers') or 'н/д'}",
        f"целевой раздел: {section_name}",
    ]

    aliases = _SECTION_ALIASES.get(section_name, ())
    narrative_bits: list[str] = []
    for item in _narrative(passport_data):
        title = str(item.get("title") or "")
        text = str(item.get("text") or "")
        low = title.lower()
        if any(a in low for a in aliases) or _match_section_title(title) == section_name:
            narrative_bits.append(f"### {title}\n{text[:3500]}")
        if len(narrative_bits) >= 4:
            break
    if not narrative_bits:
        for item in _narrative(passport_data)[:3]:
            narrative_bits.append(
                f"### {item.get('title')}\n{str(item.get('text') or '')[:2000]}"
            )

    if narrative_bits:
        parts.append("Фрагменты исходного документа:\n" + "\n\n".join(narrative_bits))

    facts: list[str] = []
    for key, value in passport_data.items():
        if not key.startswith("section_") or not isinstance(value, dict):
            continue
        for leaf_id, leaf in value.items():
            if isinstance(leaf, dict) and leaf.get("available"):
                facts.append(f"{leaf_id}: {json.dumps(leaf.get('data'), ensure_ascii=False)}")
            if len(facts) >= 25:
                break
    if facts:
        parts.append("Структурированные факты:\n" + "\n".join(facts))

    return "\n\n".join(parts)


def gigachat_generate(passport_data: dict[str, Any]) -> dict[str, Any]:
    """Call GigaChat directly (no Qdrant / local embeddings required)."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_gigachat.chat_models import GigaChat

    creds = _creds()
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS").strip() or "GIGACHAT_API_PERS"
    llm = GigaChat(
        credentials=creds,
        verify_ssl_certs=False,
        scope=scope,
        temperature=0.3,
        timeout=180,
    )

    meta = passport_data.get("meta") or {}
    station_name = meta.get("station_name") or "Неизвестная станция"

    document_sections: dict[str, str] = {}
    validation_errors: dict[str, str] = {}

    system = (
        "Ты — ведущий инженер-технолог железнодорожного транспорта. "
        "Пиши раздел местной инструкции официально-деловым стилем: развёрнуто, "
        "со ссылками на нормы там, где уместно. Отвечай только текстом раздела. "
        "Не используй Markdown: без **, *, #, ##, списков-тире в markdown-синтаксисе. "
        "Подзаголовки пиши обычной строкой (например: «1.1. Местоположение примыкания»). "
        "Не ссылайся на таблицы и приложения — они будут вставлены отдельно из техпаспорта."
    )

    for section in SECTIONS:
        context = _build_section_context(passport_data, section)
        try:
            resp = llm.invoke(
                [
                    SystemMessage(content=system),
                    HumanMessage(
                        content=(
                            f"Сгенерируй текст раздела «{section}» "
                            f"для станции «{station_name}».\n\n{context}"
                        )
                    ),
                ]
            )
            text = getattr(resp, "content", None) or str(resp)
            document_sections[section] = text.strip() if isinstance(text, str) else str(text)
        except Exception as exc:  # noqa: BLE001
            log.exception("GigaChat section failed: %s", section)
            document_sections[section] = "[ОШИБКА ГЕНЕРАЦИИ GIGACHAT]"
            validation_errors[section] = str(exc)

    return {
        "status": "success" if not validation_errors else "completed_with_errors",
        "station": station_name,
        "document_sections": document_sections,
        "validation_errors": validation_errors,
        "mode": "gigachat",
    }


def real_generate(passport_data: dict[str, Any]) -> dict[str, Any]:
    """Prefer lightweight GigaChat; fall back to full RAG engine if available."""
    try:
        return gigachat_generate(passport_data)
    except Exception:
        log.exception("Lightweight GigaChat failed — trying RAG engine")

    from ai_engine import StationInstructionAI

    creds = _creds()
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    ai = StationInstructionAI(gigachat_credentials=creds, qdrant_url=qdrant_url)

    meta = passport_data.get("meta") or {}
    station_name = meta.get("station_name", "Неизвестная станция")

    narrative = _narrative(passport_data)
    enriched: dict[str, Any] = dict(passport_data)
    if narrative:
        enriched = {
            **passport_data,
            "source_narrative_excerpt": [
                {"title": n.get("title"), "text": str(n.get("text") or "")[:2500]}
                for n in narrative[:12]
            ],
        }

    document_sections: dict[str, str] = {}
    validation_errors: dict[str, str] = {}

    for section in SECTIONS:
        try:
            document_sections[section] = ai.generate_section(section, enriched)
        except Exception as exc:  # noqa: BLE001
            log.exception("AI section failed: %s", section)
            document_sections[section] = "[ОШИБКА ГЕНЕРАЦИИ СЕРВИСОМ]"
            validation_errors[section] = str(exc)

    return {
        "status": "success" if not validation_errors else "completed_with_errors",
        "station": station_name,
        "document_sections": document_sections,
        "validation_errors": validation_errors,
        "mode": "gigachat_rag",
    }


def generate_instruction(passport_data: dict[str, Any]) -> dict[str, Any]:
    narrative = _narrative(passport_data)

    if _force_mock():
        log.info("AI_MOCK=true — deterministic mock generator")
        return mock_generate(passport_data)

    creds = _creds()
    if creds and creds != "YOUR_GIGACHAT_TOKEN_HERE":
        try:
            log.info("Using GigaChat RAG generator")
            return real_generate(passport_data)
        except Exception:
            log.exception("GigaChat failed — falling back to document/facts mode")

    if _narrative_substance(narrative):
        log.info(
            "Using document narrative (%s sections, ~%s chars)",
            len(narrative),
            sum(len(str(x.get("text") or "")) for x in narrative),
        )
        return from_narrative(passport_data, narrative)

    log.info("Using structured facts generator")
    return from_facts(passport_data)


def debug_dump(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)[:500]
