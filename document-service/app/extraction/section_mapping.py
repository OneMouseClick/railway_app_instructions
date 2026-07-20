"""
Финальный слой: раскладывает TechPassportData по разделам/подразделам
ТАК ЖЕ, как они озаглавлены в целевой «Инструкции о порядке
обслуживания...» (см. изученные образцы: ОАО «Читаоблгаз»,
ООО «МеталлСнаб», ООО «РОССЫПЬ», ООО «Труд»).

Важное архитектурное решение: заголовки инструкции делятся на две
категории.

1. Заголовки, содержание которых физически рассчитывается или
   переписывается из техпаспорта (границы, длины, устройства,
   грузовые фронты, характеристики верхнего строения пути и т.п.) —
   для них ниже стоят реальные экстракторы.

2. Заголовки, которые описывают ДОГОВОРНОЙ/ОРГАНИЗАЦИОННЫЙ порядок
   работы (кто кому звонит, какой телефон, какой номер формы
   уведомления, ФИО ответственных лиц, порядок закрепления и т.д.) —
   этих данных в техпаспорте нет: техпаспорт описывает
   путь как объект инфраструктуры, а не регламент взаимодействия
   владельца пути со станцией. Для таких заголовков сервис явно
   возвращает available=False с пояснением, а не пытается
   ничего нафантазировать — это должно попадать в модель генерации
   текста из отдельного источника (типового регламента/анкеты
   предприятия), не из техпаспорта.

Формат каждого листа (leaf) — единообразный:
{
  "available": bool,
  "data": {...} | null,
  "source": "техпаспорт: <таблица/раздел>" | null,
  "note": "почему недоступно" (только если available=False)
}
Такой формат легко скармливать модели генерации текста: она получает
компактный набор конкретных значений на каждый заголовок и НЕ видит
шаблонных формулировок — их она должна сгенерировать сама.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..models import TechPassportData

_NOT_IN_TECH_PASSPORT = (
    "Раздел описывает договорной/эксплуатационный регламент "
    "(ответственные лица, номера телефонов, формы уведомлений, порядок "
    "манёвров), который не фиксируется в техническом паспорте пути. "
    "Источник данных для этого раздела — типовой регламент/анкета "
    "предприятия и станции, не техпаспорт."
)


def _leaf(available: bool, data: Any = None, source: str | None = None, note: str | None = None) -> dict:
    out = {"available": available, "data": data, "source": source}
    if note:
        out["note"] = note
    return out


def _boundary_to_dict(pb) -> dict:
    d = asdict(pb)
    return {k: v for k, v in d.items() if v is not None}


def _cargo_front_to_dict(cf) -> dict:
    d = asdict(cf)
    return {k: v for k, v in d.items() if v is not None}


def _superstructure_to_dict(ts) -> dict:
    d = asdict(ts)
    return {k: v for k, v in d.items() if v is not None}


def build_instruction_json(data: TechPassportData) -> dict:
    g = data.general

    section_1: dict[str, Any] = {}

    section_1["1.1"] = _leaf(
        available=bool(g.company_name),
        data={"company_name": g.company_name, "path_numbers": g.path_numbers} if g.company_name else None,
        source="титульный лист / общие сведения",
    )

    section_1["1.2"] = _leaf(
        available=bool(g.locomotive_series or g.station_name),
        data={
            "station_name": g.station_name,
            "locomotive_series": g.locomotive_series or None,
            "service_order_raw": g.service_order_text,
        }
        if (g.locomotive_series or g.station_name)
        else None,
        source="общие сведения: «Порядок подачи и уборки вагонов...»",
    )

    section_1["1.3"] = _leaf(
        available=bool(g.junction_text or g.boundary_text),
        data={"junction_raw": g.junction_text, "boundary_raw": g.boundary_text}
        if (g.junction_text or g.boundary_text)
        else None,
        source="общие сведения: «Место примыкания…» / «Границы…»",
    )

    section_1["1.4"] = _leaf(
        available=bool(g.boundary_text),
        data={"boundary_raw": g.boundary_text} if g.boundary_text else None,
        source="общие сведения: «Границы…» (знак ГПНП фиксируется той же формулировкой)",
        note=None if g.boundary_text else "В общих сведениях не найдено формулировки границы пути.",
    )

    section_1["1.5"] = _leaf(
        available=bool(g.safety_devices),
        data=[asdict(d) for d in g.safety_devices] if g.safety_devices else None,
        source="общие сведения: «Наличие предохранительных устройств»",
    )

    boundaries_data = [_boundary_to_dict(b) for b in data.path_boundaries]
    section_1["1.6"] = {
        "1.6.1": _leaf(
            available=False,
            note="Схема пути — графическое приложение (план/схема), не текстовое поле. "
            "Сервис извлекает числовые/текстовые характеристики; вложение самой схемы "
            "как файла-приложения — отдельная задача (см. README).",
        ),
        "1.6.2": _leaf(
            available=False,
            note="Максимальный уклон и минимальный радиус кривой в изученных техпаспортах "
            "присутствуют только как подписи на чертеже продольного профиля/плана пути "
            "(векторная графика), а не в текстовых таблицах. Надёжный разбор требует "
            "отдельного модуля работы с векторной геометрией чертежа (см. README, "
            "'Ограничения и точки расширения').",
        ),
        "1.6.3": _leaf(
            available=data.road_crossings_present is not None,
            data={"road_crossings_present": data.road_crossings_present}
            if data.road_crossings_present is not None
            else None,
            source="Таблица 2.5 «Пересечения с автомобильными дорогами»",
        ),
        "path_lengths": _leaf(
            available=bool(boundaries_data) or data.total_length_full_m is not None,
            data={
                "paths": boundaries_data or None,
                "total_length_full_m": data.total_length_full_m,
                "total_length_useful_m": data.total_length_useful_m,
            },
            source="Таблицы 1.2 «Ведомость путей», 1.3 «Данные по длине путей»",
        ),
    }

    section_1["1.7"] = _leaf(
        available=False,
        note="Допускаемые скорости движения в изученных инструкциях — фиксированные "
        "нормативные значения (15 км/ч, 3 км/ч), одинаковые для всех предприятий и "
        "заданные ПТЭ/ИДП, а не значения из техпаспорта конкретного пути.",
    )

    section_1["1.8"] = _leaf(
        available=False,
        note="Наличие устройств СЦБ и распорядительных постов не выведено ни в одной "
        "таблице изученных техпаспортов; в примерах инструкций эти пункты — типовая "
        "формулировка об отсутствии устройств. Если у предприятия устройства СЦБ есть, "
        "это потребует отдельного текстового поля в техпаспорте, которого сейчас нет.",
    )

    cargo_data = [_cargo_front_to_dict(f) for f in data.cargo_fronts]
    section_1["1.9"] = {
        "cargo_fronts": _leaf(
            available=bool(cargo_data),
            data=cargo_data or None,
            source="Таблица 4.1 «Вместимость грузовых фронтов» + описательный текст раздела 4",
        ),
        "1.9.1": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
        "1.9.2": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
    }

    section_1["1.10"] = _leaf(available=False, note=_NOT_IN_TECH_PASSPORT)
    section_1["1.11"] = _leaf(available=False, note=_NOT_IN_TECH_PASSPORT)

    section_1["lower_structure"] = {
        "2.1_embankments": _leaf(
            available=data.embankments_present is not None,
            data={"present": data.embankments_present} if data.embankments_present is not None else None,
            source="Таблица 2.1 «Наличие насыпей или выемок»",
        ),
        "2.2_drainage": _leaf(
            available=data.drainage_present is not None,
            data={"present": data.drainage_present} if data.drainage_present is not None else None,
            source="Таблица 2.2 «Наличие водоотводных сооружений»",
        ),
        "2.3_deformation": _leaf(
            available=data.deformation_present is not None,
            data={"present": data.deformation_present} if data.deformation_present is not None else None,
            source="Таблица 2.3 «Деформация земляного полотна»",
        ),
        "2.4_structures": _leaf(
            available=data.structures_present is not None,
            data={"present": data.structures_present} if data.structures_present is not None else None,
            source="Таблица 2.4 «Искусственные сооружения»",
        ),
    }

    superstructure_data = [_superstructure_to_dict(s) for s in data.track_superstructure]
    section_1["upper_structure"] = _leaf(
        available=bool(superstructure_data or data.switches_summary),
        data={
            "by_path": superstructure_data or None,
            "switches_summary": data.switches_summary,
        },
        source="Таблицы 3.1–3.12 «Верхнее строение пути»",
    )

    section_2: dict[str, Any] = {
        "2.1": _leaf(
            available=bool(g.station_name or g.locomotive_series),
            data={"station_name": g.station_name, "locomotive_series": g.locomotive_series or None}
            if (g.station_name or g.locomotive_series)
            else None,
            source="общие сведения (частично пересекается с 1.2)",
        ),
        "2.2": _leaf(
            available=bool(cargo_data),
            data={"cargo_fronts_capacity": [c.get("capacity") for c in cargo_data if c.get("capacity")]} or None,
            source="Таблица 4.1 (вместимость грузовых фронтов используется как ограничитель "
            "величины подаваемой группы вагонов)",
            note="Итоговая норма состава (число вагонов/осей/вес) в инструкции — "
            "результат расчёта, не прямое значение из техпаспорта; здесь отдаются "
            "только исходные вместимости фронтов.",
        ),
        "2.3": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
        "2.4": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
        "2.5": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
        "2.6": _leaf(available=False, note=_NOT_IN_TECH_PASSPORT),
        "2.7": _leaf(
            available=bool(g.safety_devices),
            data={"safety_devices": [asdict(d) for d in g.safety_devices]} if g.safety_devices else None,
            source="общие сведения: «Наличие предохранительных устройств» "
            "(процедура въезда описывает работу именно с этим устройством)",
        ),
    }

    return {
        "meta": {
            "source_file": data.source_file,
            "source_format": data.source_format,
            "company_name": g.company_name,
            "station_name": g.station_name,
            "path_numbers": g.path_numbers,
        },
        "section_1_general_characteristics": section_1,
        "section_2_supply_removal_procedure": section_2,
        "unmapped_raw_tables": data.raw_tables_by_number,
    }
