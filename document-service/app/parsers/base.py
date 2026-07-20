"""
Общие low-level утилиты, используемые всеми парсерами форматов (docx/doc/pdf).

Здесь нет логики, специфичной для конкретного формата файла — только
разбор текста, который в техпаспортах устроен единообразно независимо
от того, в каком формате пришёл документ (пикеты вида ПК1+23,45, числа
с запятой как разделителем дробной части, названия таблиц "Таблица 3.7" и т.п.)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional



# Разбор чисел / пикетов — в техпаспортах всегда десятичная запятая,
# а не точка.

_NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")
_PICKET_RE = re.compile(r"ПК\s*(\d+)\s*\+\s*(\d{1,2}[.,]\d{1,2})", re.IGNORECASE)


def to_float(raw: Optional[str]) -> Optional[float]:
    """'115,10' -> 115.10 ; '169,00' -> 169.0 ; None/'-'/'' -> None"""
    if raw is None:
        return None
    raw = raw.strip()
    if raw in ("", "-", "—", "–", "нет", "н/д"):
        return None
    m = _NUMBER_RE.search(raw.replace("\xa0", " "))
    if not m:
        return None
    return float(m.group(0).replace(",", "."))


def parse_picket(raw: str) -> Optional[float]:
    """
    'ПК0+43,56' -> 43.56
    Возвращает суммарное значение в метрах: pk*100 + остаток.
    """
    if not raw:
        return None
    m = _PICKET_RE.search(raw.replace("\xa0", " "))
    if not m:
        return None
    pk = int(m.group(1))
    rest = float(m.group(2).replace(",", "."))
    return pk * 100 + rest


def extract_picket_label(raw: str) -> Optional[str]:
    """Возвращает исходную строку пикета в каноническом виде 'ПК0+43,56' или None."""
    if not raw:
        return None
    m = _PICKET_RE.search(raw.replace("\xa0", " "))
    if not m:
        return None
    return f"ПК{m.group(1)}+{m.group(2).replace('.', ',')}"


def clean_text(raw: Optional[str]) -> str:
    if raw is None:
        return ""
    # схлопываем переносы/множественные пробелы, характерные для docx/pdf экспорта
    text = raw.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return text.strip()


def is_empty_cell(raw: Optional[str]) -> bool:
    if raw is None:
        return True
    v = raw.strip()
    return v in ("", "-", "—", "–")


TABLE_TITLE_RE = re.compile(
    r"Таблиц[аы]\s+(\d+\.\d+)\s*[-–—]?\s*(.*)", re.IGNORECASE
)

# Ключевые слова (в нижнем регистре) для сопоставления таблицы её смысловой
# теме независимо от номера, под которым она значится в конкретном
# техпаспорте. Список собран по формулировкам всех изученных на данный
# момент шаблонов (АО «ВНИИЖТ», ООО «Забтранспроект», шаблон «ТЧГП»).
# Порядок ключей важен только в той мере, что первое совпадение по
# конкретной таблице побеждает — конфликтов между темами ниже нет,
# т.к. формулировки не пересекаются.
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "adjacent_paths": ["примыкани"],  # Табл. 1.1
    "path_registry": ["ведомость железнодорожных путей", "ведомость путей"],  # 1.2
    "path_lengths": ["длине путей", "данные по длине", "длины путей"],  # 1.3
    "embankments": ["насып", "выемок"],  # 2.1
    "drainage": ["водоотвод"],  # 2.2
    "deformation": ["деформац"],  # 2.3
    "structures": ["искусственн"],  # 2.4
    "road_crossings": ["пересечен"],  # 2.5
    "ballast_type": ["род балласта"],  # 3.1
    "ballast_thickness": ["толщина балласт"],  # 3.2
    "ballast_pollution": ["загрязнение балласт"],  # 3.3
    "ballast_pollutability": ["загрязняемость балласт"],  # 3.4
    "anti_creepers": ["закреплени", "противоугон"],  # номер разный по шаблонам!
    "sleepers": ["эпюра шпал", "количество шпал"],
    "rails": ["тип рельсов"],
    "welded_joints": ["сварных стыков", "сварные стыки"],
    "switches_list": ["ведомость стрелочных переводов"],
    "switches_superstructure": ["строение пути на стрелоч", "верхнее строение на стрелоч"],
    "joint_fasteners": ["стыковые скреплен", "стыковых скреплен"],
    "intermediate_fasteners": ["промежуточные скреплен", "промежуточных скреплен"],
    "cargo_capacity": ["вместимость грузовых фронт"],
}


def match_table_title(paragraph_text: str) -> Optional[tuple[str, str]]:
    """
    По тексту абзаца, стоящего перед/над таблицей, определяет её номер
    и заголовок, например: 'Таблица 3.2 – Толщина балластного слоя'
    -> ('3.2', 'Толщина балластного слоя')
    """
    m = TABLE_TITLE_RE.search(paragraph_text)
    if not m:
        return None
    return m.group(1), clean_text(m.group(2))



# Промежуточное представление документа: последовательность блоков —
# абзацы и таблицы вперемешку, в порядке появления в исходном файле.
# Формато-специфичные парсеры (docx/pdf) обязаны привести файл именно
# к этой структуре — дальше вся логика извлечения работает одинаково.



@dataclass
class RawTable:
    caption: Optional[str]          # текст абзаца-подписи ("Таблица 3.2 – ...")
    rows: list[list[str]]           # ячейки построчно, как в документе
    page_or_index: int = 0          # номер страницы (pdf) или порядковый индекс (docx)


@dataclass
class RawParagraph:
    text: str
    page_or_index: int = 0


@dataclass
class RawDocument:
    """Единое представление документа для docx и pdf парсеров."""
    blocks: list[object] = field(default_factory=list)  # RawParagraph | RawTable

    @property
    def full_text(self) -> str:
        return "\n".join(b.text for b in self.blocks if isinstance(b, RawParagraph))

    def tables(self) -> list[RawTable]:
        return [b for b in self.blocks if isinstance(b, RawTable)]

    def tables_by_number(self) -> dict[str, RawTable]:
        """
        Сопоставляет номер таблицы ('3.2') -> RawTable по подписи.
        Если заголовок таблицы не распознан регэкспом,
        таблица просто не попадёт в словарь и должна обрабатываться
        позиционно (см. pdf_parser.py:heuristic fallback).

        ВАЖНО: номер таблицы НЕ является надёжным межшаблонным ключом —
        разные проектные организации нумеруют одни и те же по смыслу
        таблицы по-разному (например, «Закрепление от угона» — это
        Таблица 3.12 в шаблоне АО «ВНИИЖТ», но Таблица 3.5 в шаблоне
        с маркировкой «ТЧГП»). Этот метод оставлен для отладки и для
        специфичных для конкретного шаблона случаев; вся логика
        извлечения данных в extraction/normalize.py использует
        tables_by_topic() ниже, которая матчит таблицы по смыслу их
        заголовка, а не по номеру.
        """
        result: dict[str, RawTable] = {}
        for t in self.tables():
            if not t.caption:
                continue
            hit = match_table_title(t.caption)
            if hit:
                result[hit[0]] = t
        return result

    def tables_by_topic(self) -> dict[str, RawTable]:
        """
        Сопоставляет смысловую тему ('ballast_type', 'sleepers', ...) ->
        RawTable, по ключевым словам в заголовке таблицы — независимо
        от того, каким номером эта таблица помечена в конкретном
        техпаспорте. Это основной способ адресации таблиц в extraction/
        normalize.py, устойчивый к разной нумерации разных проектных
        организаций (см. docstring tables_by_number() выше).

        Если заголовок таблицы не распознан regex'ом match_table_title
        (например, PDF без чёткой подписи), пробуем сматчить тему по
        всему тексту подписи как есть — это покрывает шаблоны, где
        заголовок таблицы стоит отдельным абзацем без слова 'Таблица'
        на той же строке.
        """
        result: dict[str, RawTable] = {}
        for t in self.tables():
            if not t.caption:
                continue
            hit = match_table_title(t.caption)
            title = hit[1] if hit else t.caption
            title_lower = title.lower()
            for topic, keywords in TOPIC_KEYWORDS.items():
                if topic in result:
                    continue  # первое совпадение побеждает
                if any(kw in title_lower for kw in keywords):
                    result[topic] = t
        return result
