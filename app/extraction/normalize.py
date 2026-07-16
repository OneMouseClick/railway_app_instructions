"""
Нормализация: превращает формато-независимый RawDocument (см.
parsers/base.py) в TechPassportData (models.py).

На данный момент подтверждено 3 разных шаблона бланка техпаспорта:

  A) АО «ВНИИЖТ»              — общий текст с лейблами вида
                                 'Место примыкания ...:', таблицы
                                 подписаны 'Таблица 3.2 – Толщина...'
                                 одной строкой, десятичные через запятую.
  Б) ООО «Забтранспроект»      — структурно идентичен (A) по всем
                                 значимым для парсинга признакам.
  В) шаблон с маркировкой
     техпаспорта «ТЧГП»        — те же лейблы общих сведений, НО:
                                 заголовок и номер таблицы разнесены на
                                 два абзаца ('Толщина...' \\n 'Таблица 3.2'),
                                 номера таблиц НЕ совпадают по смыслу с
                                 шаблоном (A) начиная с раздела 3,
                                 десятичные через точку, другие
                                 формулировки якорных фраз в отдельных
                                 местах (см. ниже).

Из-за разной нумерации таблиц между шаблонами (Б) и (В) КЛЮЧЕВОЕ
архитектурное решение: таблицы адресуются НЕ по номеру
(RawDocument.tables_by_number()), а по смысловой теме заголовка
(RawDocument.tables_by_topic(), см. parsers/base.py::TOPIC_KEYWORDS).
Номер таблицы для логики извлечения не используется нигде в этом
модуле — только тема.

Общий принцип экстракторов: техпаспорта оформлены по одному из
известных шаблонов, и внутри шаблона формулировки практически не
меняются от объекта к объекту — меняются только значения. Поэтому
экстракция построена на "якорных" фразах (label-anchored regex), а
не на позиции таблицы/абзаца. Если для нового, ещё не виденного
шаблона якорная фраза сформулирована иначе — экстрактор просто не
найдёт значение и оставит поле None, вместо того чтобы подставить
неверные данные (см. README, раздел «Ограничения»).
"""
from __future__ import annotations

import re

from ..models import (
    CargoFront,
    GeneralInfo,
    PathBoundary,
    SafetyDevice,
    TechPassportData,
    TrackSuperstructure,
)
from ..parsers.base import RawDocument, RawTable, clean_text, to_float

LOCOMOTIVE_RE = re.compile(r"ТЭМ[\s-]?\d+[МA-Я]{0,3}", re.IGNORECASE)
SPECIALIZATION_KEYWORDS = [
    "Погрузочно-выгрузочный",
    "Погрузочно выгрузочный",
    "Погрузовыгрузочный",
    "Обгонный",
    "Погрузочный",
    "Выгрузочный",
    "МСУ",
]


# ---------------------------------------------------------------------------
# Общие сведения (титульный текстовый блок техпаспорта)
# ---------------------------------------------------------------------------

# Список из (ключ_результата, regex_лейбла). Один и тот же ключ может
# встречаться несколько раз с разными формулировками — актуально для
# шаблона (В), где помимо 'Наличие предохранительного тупика...'
# отдельным абзацем встречается ещё и 'Предохранительными устройствами,
# предотвращающими самопроизвольный выход вагонов ... являются:'.
# Оба варианта пишут в одно и то же поле safety_raw (конкатенацией).
_GENERAL_LABELS = [
    ("junction_text", r"Место примыкания[^:]*:"),
    ("boundary_text", r"Границ[аы][^:]*:"),
    ("safety_raw", r"Наличие предохранительн\w+[^:]*:"),
    ("safety_raw", r"Предохранительными устройствами[^:]*:"),
    ("contract_text", r"Дата заключения договора[^:]*:"),
    ("service_order_text", r"Порядок подачи и уборки вагонов[^:]*:"),
]


def _extract_general_block(full_text: str) -> dict[str, str]:
    """
    Вырезает текст между лейблами вида 'Место примыкания ... :' и
    следующим лейблом (или заголовком следующего раздела).
    Если один ключ встречается по нескольким формулировкам лейбла —
    результаты конкатенируются через пробел (см. _GENERAL_LABELS).
    """
    positions: list[tuple[str, int, int]] = []
    for key, pattern in _GENERAL_LABELS:
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            positions.append((key, m.start(), m.end()))

    if not positions:
        return {}

    positions.sort(key=lambda p: p[1])
    # граница конца текущего блока — начало следующего лейбла или,
    # для последнего, ближайший заголовок раздела/таблицы
    stop_re = re.compile(
        r"(ХАРАКТЕРИСТИКА ПУТИ|Таблица\s+\d+\.\d+|^\s*\d\.\s*Общие сведения|"
        r"Примыкание других железнодорожных путей)",
        re.MULTILINE,
    )

    result: dict[str, list[str]] = {}
    for i, (key, _start, end) in enumerate(positions):
        next_start = positions[i + 1][1] if i + 1 < len(positions) else None
        segment = full_text[end:next_start] if next_start else full_text[end:]
        stop_m = stop_re.search(segment)
        if stop_m:
            segment = segment[: stop_m.start()]
        segment = clean_text(segment)
        if segment:
            result.setdefault(key, []).append(segment)

    return {k: " ".join(v) for k, v in result.items()}


_DESIGN_ORG_BLOCKLIST = {"ЗАБТРАНСПРОЕКТ", "ВНИИЖТ", "НАУЧНО-ИССЛЕДОВАТЕЛЬСКИЙ ИНСТИТУТ ЖЕЛЕЗНОДОРОЖНОГО ТРАНСПОРТА"}


def extract_general_info(raw: RawDocument) -> GeneralInfo:
    info = GeneralInfo()
    text = raw.full_text

    blocks = _extract_general_block(text)
    info.junction_text = blocks.get("junction_text") or None
    info.boundary_text = blocks.get("boundary_text") or None
    info.contract_text = blocks.get("contract_text") or None
    info.service_order_text = blocks.get("service_order_text") or None

    safety_raw = blocks.get("safety_raw")
    if safety_raw:
        info.safety_devices = _parse_safety_devices(safety_raw)

    if info.service_order_text:
        info.locomotive_series = sorted(
            set(
                m.group(0).upper().replace(" ", "").replace("-", "")
                for m in LOCOMOTIVE_RE.finditer(info.service_order_text)
            )
        )

    # Название владельца пути ищем ПОСЛЕ заголовка 'ТЕХНИЧЕСКИЙ ПАСПОРТ',
    # а не в первых байтах документа: на бланках АО «ВНИИЖТ» и
    # ООО «Забтранспроект» перед этим заголовком стоит название самой
    # проектной организации (тоже в кавычках, тоже с ООО/АО), которое
    # иначе ложно матчится вместо реального владельца пути (баг,
    # проявившийся на техпаспорте ИП Цивинского — см. тесты).
    title_pos = text.lower().find("технический паспорт")
    search_zone = text[title_pos : title_pos + 700] if title_pos != -1 else text[:600]

    # 'ИП Цивинский Н.Н.' пишется без кавычек — если зона содержит 'ИП',
    # это надёжнее компании в кавычках (у ИП просто нет кавычек по ГОСТ)
    ip_m = re.search(r"ИП\s+([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)?)", search_zone)

    company_m = re.search(r"(ООО|ОАО|АО|ПАО|ЗАО)\s*[«\"]([^»\"]+)[»\"]", search_zone)
    if company_m and company_m.group(2).strip().upper() not in _DESIGN_ORG_BLOCKLIST:
        info.company_name = f"{company_m.group(1)} «{company_m.group(2)}»"
    elif ip_m:
        info.company_name = f"ИП {clean_text(ip_m.group(1))}"
    elif company_m:
        # совпадение было только с институтом-разработчиком — ищем дальше
        # в тексте (за пределами первой найденной, заблокированной, компании)
        rest = search_zone[company_m.end():]
        fallback_m = re.search(r"(ООО|ОАО|АО|ПАО|ЗАО)\s*[«\"]([^»\"]+)[»\"]", rest)
        if fallback_m:
            info.company_name = f"{fallback_m.group(1)} «{fallback_m.group(2)}»"

    head = search_zone  # используется ниже для номера станции/пути

    # 'ст. Чита-I', 'Ст. Бада', 'станции Кадала', 'станция Благовещенск' —
    # захватываем только первое слово названия (плюс римскую цифру через
    # дефис, как в 'Чита-I'), т.к. дальше в линеаризованном PDF-тексте
    # переносов строк уже нет и жадный класс символов уедет в соседний абзац
    station_m = re.search(r"[Сс]т\.?\s+([А-ЯЁ][а-яё]*(?:-[IVXA-ZА-Я0-9]+)?)", head)
    if not station_m:
        station_m = re.search(
            r"станци[ияю]\s+([А-ЯЁ][а-яё]*(?:-[IVXA-ZА-Я0-9]+)?)", text[:1500]
        )
    if station_m:
        info.station_name = clean_text(station_m.group(1))

    # 'Путь №2', 'Путь №ГМС-3', 'Пути №71, 71а, МСУ 262-270' — берём из
    # заголовочной строки титульного листа, а НЕ из произвольного
    # упоминания 'путь № N' по всему тексту: в тексте «Место примыкания»
    # часто фигурируют номера ЧУЖИХ, соседних путей ('к пути №305а
    # Читинской дистанции пути', 'к продолжению пути №1АБ станции
    # Благовещенск'), которые не должны попадать в список путей самого
    # владельца. Поэтому зону поиска обрезаем строго титульным блоком —
    # до начала 'ОБЩИЕ СВЕДЕНИЯ'/'Место примыкания', не заходя в текст,
    # где такие чужие упоминания встречаются.
    title_block_end = re.search(r"ОБЩИЕ СВЕДЕНИЯ|Место примыкания", search_zone, re.IGNORECASE)
    title_zone = search_zone[: title_block_end.start()] if title_block_end else search_zone

    path_line_m = re.search(
        r"[Пп]ут[ьи]\s*№\s*"
        r"([0-9][0-9а-яА-Я]{0,4}"                          # '22', 'ГМС-3' начинается с цифры? нет — см. альтернативу ниже
        r"(?:\s*,\s*[0-9][0-9а-яА-Я]{0,4})*"                # ', 71а, ...'
        r"(?:\s*,\s*МСУ\s+[\d\-]+)?"                        # необязательный ', МСУ 262-270'
        r"|[А-ЯЁ]+-\d+)",                                    # 'ГМС-3' (буквенно-числовой номер)
        title_zone,
    )
    _PATH_TOKEN_JUNK_WORDS = (
        "железнодорожн", "станци", "путей", "необщего", "пользования",
        "парка", "дистанции", "забайкальской",
    )
    path_numbers: list[str] = []
    if path_line_m:
        for token in path_line_m.group(1).split(","):
            token = clean_text(token).rstrip(".")
            if not token or len(token) > 15:
                continue
            if any(w in token.lower() for w in _PATH_TOKEN_JUNK_WORDS):
                continue
            path_numbers.append(token)
    info.path_numbers = path_numbers

    return info


def _parse_safety_devices(safety_text: str) -> list[SafetyDevice]:
    devices: list[SafetyDevice] = []
    # 'Ручной сбрасывающий башмак СБР№583а (сброс вправо) ПК1+04,86'
    # 'колесосбрасывающий башмак №5СБ (ручной, сброс вправо) ПК1+16,36'
    # 'ручной сбрасывающий башмак №15 (пк01+28.03)'
    for m in re.finditer(
        r"(?P<type>(?:[А-Яа-яё]+\s+)?(?:сбрасывающ\w+|колесосбрасывающ\w+)\s+башмак\w*)"
        r"[^А-Яа-я0-9№]*(?P<id>(?:СБР?№?\s?\d+[а-яА-Я]{0,3}|БС№?\s?\d+[а-яА-Я]{0,3}|№\s?\d+[а-яА-Я]{0,3}))?",
        safety_text,
        re.IGNORECASE,
    ):
        # picket/direction ищем локально, в окне после найденного устройства,
        # а не по всему тексту — иначе при нескольких устройствах на
        # предприятие (см. ЗЛП: два башмака на разных путях) вся информация
        # схлопнется к первому найденному пикету
        window = safety_text[m.end() : m.end() + 120]
        picket_m = re.search(r"[Пп][Кк]\s*\d+\s*\+\s*\d{1,2}[.,]\d{1,2}", window) or re.search(
            r"[Пп][Кк]\s*\d+\s*\+\s*\d{1,2}[.,]\d{1,2}", safety_text
        )
        direction_m = re.search(r"сброс\w*\s+(вправо|влево)", window, re.IGNORECASE) or re.search(
            r"сброс\w*\s+(вправо|влево)", safety_text, re.IGNORECASE
        )
        devices.append(
            SafetyDevice(
                device_type=clean_text(m.group("type")),
                device_id=clean_text(m.group("id")) if m.group("id") else None,
                picket=picket_m.group(0).replace(" ", "").upper() if picket_m else None,
                throw_direction=direction_m.group(1).lower() if direction_m else None,
            )
        )
    return devices


# ---------------------------------------------------------------------------
# Ведомость путей / данные по длине (темы 'path_registry' / 'path_lengths')
# ---------------------------------------------------------------------------


def _row_text(row: list[str]) -> str:
    return " ".join(c for c in row if c)


def _guess_path_number(row_text: str, known_path_numbers: list[str]) -> str | None:
    """
    В "чистых" docx-таблицах номер пути — первый токен строки, и для
    большинства шаблонов этого достаточно. В PDF, полученном из
    чертёжного бланка, порядок слов внутри ячейки может ломаться
    боковыми подписями штампа ('Взам. инв. №', 'Подп. и дата'), поэтому
    добавлены более гибкие эвристики:
    1) если известен единственный номер пути из титульного листа —
       используем его (самый надёжный источник для однопутных техпаспортов);
    2) первый токен строки, если это похоже на номер пути;
    3) изолированный 1-2-значный токен перед 'ПС' / 'Знак ГПНП' / 'ГПНП';
    4) токен сразу после специализации.
    """
    first_token_m = re.match(r"\s*(\d{1,3}[а-яА-Я]?)\s", row_text)
    if first_token_m and (not known_path_numbers or first_token_m.group(1) in known_path_numbers):
        return first_token_m.group(1)

    m = re.search(r"(?<![\d.])(\d{1,3}[а-яА-Я]?)(?![\d.])\s+(?:ПС\s*СП|Знак\s*ГПНП|ГПНП)", row_text)
    if m:
        return m.group(1)

    m = re.search(
        r"(?:Погрузочно[- ]?выгрузочный|Выгрузочный|Погрузочный|Обгонный)\S*\s+\S+\s+(\d{1,3}[а-яА-Я]?)\b",
        row_text,
    )
    if m:
        return m.group(1)

    # если построчно ничего не нашли — единственный номер пути с
    # титульного листа остаётся разумным допущением ТОЛЬКО для
    # действительно однопутевых техпаспортов, и ТОЛЬКО если строка
    # вообще похожа на данные (есть пикет), а не на шапку таблицы —
    # иначе шапка таблицы (без единого пикета) тоже "находит" путь
    # и порождает пустой дублирующий результат
    if len(known_path_numbers) == 1 and re.search(r"пк\s*\d+\s*\+", row_text, re.IGNORECASE):
        return known_path_numbers[0]

    return None


def _count_data_rows(table) -> int:
    """Считает строки таблицы, которые не являются шапкой/итогом."""
    if not table:
        return 0
    count = 0
    for row in table.rows:
        text = _row_text(row)
        if re.match(r"\s*(№\s*пути|Итого)\b", text, re.IGNORECASE):
            continue
        if "ПК" in text or re.search(r"\d", text):
            count += 1
    return count


def _split_blob_by_known_paths(blob: str, known_path_numbers: list[str]) -> list[tuple[str, str]]:
    """
    PDF-таблица для многопутевого предприятия приходит одной
    "псевдострокой" (см. pdf_parser.py) — все пути внутри неё склеены
    в одну строку текста, и построчная логика ниже (рассчитанная на
    честную сетку docx) не может разделить их. Если известны номера
    путей с титульного листа (2 и более), ищем их как отдельные токены
    в тексте блоба и режем блоб на сегменты по позициям этих токенов —
    дальше каждый сегмент обрабатывается как обычная "строка" таблицы,
    но с уже известным (не угадываемым) номером пути.

    Составные номера вида 'МСУ 262-270' в PDF-линеаризации иногда
    разрываются посторонним текстом (боковые подписи чертёжного
    штампа) и не находятся как целая фраза — для них дополнительно
    ищем короткий якорь (первое слово, 'МСУ'), сопоставляя найденное
    обратно с полным каноническим номером пути.
    """
    if len(known_path_numbers) < 1:
        return []

    anchor_to_canonical: dict[str, str] = {}
    for t in known_path_numbers:
        anchor_to_canonical[t] = t
        first_word = t.split()[0]
        if first_word != t and len(first_word) >= 3:
            anchor_to_canonical.setdefault(first_word, t)

    # длинные варианты — раньше коротких, чтобы полный токен побеждал
    # частичный при совпадении на той же позиции
    anchors = sorted(anchor_to_canonical, key=len, reverse=True)
    pattern = re.compile(r"(?<!\S)(" + "|".join(re.escape(a) for a in anchors) + r")(?!\S)")
    matches = list(pattern.finditer(blob))
    if not matches:
        return []

    segments = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(blob)
        segments.append((blob[m.start() : end], anchor_to_canonical[m.group(1)]))
    return segments


def _iter_path_rows(
    table: RawTable | None, known_path_numbers: list[str]
) -> list[tuple[str, str | None]]:
    """
    Единая точка итерации по "строкам" таблицы независимо от источника:
    - honest docx-сетка -> возвращает её строки как есть, номер пути
      неизвестен заранее (None), его определит _guess_path_number;
    - однострочный PDF-блоб при 2+ известных путях -> результат
      _split_blob_by_known_paths, номер пути уже известен из анкера;
    - однострочный PDF-блоб при <2 известных путях (типичный
      однопутевый техпаспорт) -> одна "строка" как есть.
    """
    if table is None:
        return []
    if len(table.rows) == 1:
        blob = _row_text(table.rows[0])
        segments = _split_blob_by_known_paths(blob, known_path_numbers)
        if segments:
            return segments
        if len(known_path_numbers) == 1:
            # единственный известный путь — блоб целиком относится к нему;
            # ждать совпадения 'цифра в начале строки' бессмысленно, т.к.
            # PDF-блоб начинается с шапки таблицы, а не с номера пути
            return [(blob, known_path_numbers[0])]
        return [(blob, None)]
    return [(_row_text(row), None) for row in table.rows]


def extract_path_boundaries_and_lengths(
    raw: RawDocument, known_path_numbers: list[str] | None = None
) -> tuple[list[PathBoundary], float | None, float | None]:
    topics = raw.tables_by_topic()
    boundaries: list[PathBoundary] = []
    known_path_numbers = known_path_numbers or []

    t_registry = topics.get("path_registry")
    t_lengths = topics.get("path_lengths")

    if not known_path_numbers:
        # титульный лист не дал номеров путей (например, в колонке
        # '№ пути' самой таблицы вписано название компании вместо
        # цифры — реальный случай техпаспорта ООО «Труд»). Если у
        # таблицы ровно одна содержательная строка данных — это
        # однопутевое предприятие, и можно безопасно считать его
        # единственный путь путём "1", не теряя данные целиком.
        n_rows = max(_count_data_rows(t_lengths), _count_data_rows(t_registry))
        if n_rows == 1:
            known_path_numbers = ["1"]

    length_by_path: dict[str, tuple[float | None, float | None]] = {}
    total_full: float | None = None
    total_useful: float | None = None

    if t_lengths:
        blob = " ".join(_row_text(r) for r in t_lengths.rows)
        # 'ИТОГО 419,34 287,34' (шаблон А/Б) или 'Итого: 1308.38 1015.72' (шаблон В)
        total_m = re.search(r"ИТОГО:?\s+([\d,.]+)\s+([\d,.]+)", blob, re.IGNORECASE)
        if total_m:
            total_full = to_float(total_m.group(1))
            total_useful = to_float(total_m.group(2))
        for row_text, hint in _iter_path_rows(t_lengths, known_path_numbers):
            if re.match(r"\s*Итого\b", row_text, re.IGNORECASE):
                continue
            path_number = hint or _guess_path_number(row_text, known_path_numbers)
            # обрезаем хвост 'ИТОГО ...' внутри сегмента (актуально для
            # последнего пути при разбиении PDF-блоба по known_path_numbers,
            # см. _split_blob_by_known_paths) — иначе итоговая сумма по
            # всему предприятию ошибочно принимается за длину этого пути
            row_text_for_lengths = re.split(r"\bИТОГО\b", row_text, maxsplit=1, flags=re.IGNORECASE)[0]
            # значения длины пути (полная/полезная) — это числа ПОСЛЕ
            # всех упоминаний пикетов; если искать decimal-числа по всей
            # строке как есть, в них попадают остатки пикетов вида
            # 'ПК01+95.69' (тут '95.69' — не длина, а координата)
            without_pickets = re.sub(r"пк\d+\+\d{1,2}[.,]\d{1,2}", " ", row_text_for_lengths, flags=re.IGNORECASE)
            lengths = re.findall(r"(\d+[.,]\d+)", without_pickets)
            if path_number and len(lengths) >= 2:
                length_by_path[path_number] = (
                    to_float(lengths[0]),
                    to_float(lengths[1]),
                )

    source_table = t_registry or t_lengths
    if source_table:
        for row_text, hint in _iter_path_rows(source_table, known_path_numbers):
            if re.match(r"\s*Итого\b", row_text, re.IGNORECASE):
                continue
            path_number = hint or _guess_path_number(row_text, known_path_numbers)
            if not path_number:
                continue

            spec: str | None = None
            if re.search(r"Погрузочно-?\s*", row_text, re.IGNORECASE) and re.search(
                r"\bвыгрузочн\w+\b", row_text, re.IGNORECASE
            ):
                # 'Погрузочно-' и 'выгрузочный' в PDF-бланке иногда разорваны
                # посторонним текстом боковых подписей штампа — если оба
                # фрагмента слова есть в пределах одной строки таблицы,
                # достаточно уверенно считаем специализацию погрузочно-выгрузочной.
                # Эта проверка идёт ПЕРЕД поиском отдельных ключевых слов,
                # иначе 'выгрузочный' сам по себе матчился бы как самостоятельное
                # (и неверное) значение 'Выгрузочный'.
                spec = "Погрузочно-выгрузочный"
            else:
                spec = next(
                    (kw for kw in SPECIALIZATION_KEYWORDS if kw.lower() in row_text.lower()),
                    None,
                )
            # доп. специализация может идти через запятую после основной
            # ('Погрузочно-выгрузочный, обгонный') — сохраняем как есть,
            # если явно обе присутствуют
            if spec and "обгонный" in row_text.lower() and "обгонный" not in spec.lower():
                spec = f"{spec}, обгонный"

            # 'ПС СП№260 ПК0+62,65' (А/Б) или 'ГПНП стык р.р. СП №168 ПК00+00.00' (В)
            from_m = re.search(
                r"((?:ГПНП|Знак\s*ГПНП|ПС\s*СП?\d*|стык\s*р\.?р\.?\s*СП\S*|Светофор|свет\.)"
                r".{0,60}?ПК\d+\+\d{1,2}[.,]\d{1,2})",
                row_text,
                re.IGNORECASE,
            )
            to_search_from = from_m.end() if from_m else 0
            to_m = re.search(
                r"((?:Упор|ГПНП|Остряк\s*СП?\d*|Светофор|свет\.)"
                r".{0,60}?ПК\d+\+\d{1,2}[.,]\d{1,2})",
                row_text[to_search_from:],
                re.IGNORECASE,
            )

            def _clean_label(match) -> str | None:
                if not match:
                    return None
                value = match.group(1)
                # если внутри совпадения затесалась дата или подпись —
                # значит боковые подписи бланка PDF сломали порядок текста
                # внутри ячейки; лучше не отдавать частично неверные данные
                if re.search(r"\d{2}[.,]\d{4}|[А-ЯЁ]\.[А-ЯЁ]\.", value):
                    return None
                return clean_text(value)

            full_len, useful_len = length_by_path.get(path_number, (None, None))

            boundaries.append(
                PathBoundary(
                    path_number=path_number,
                    from_label=_clean_label(from_m),
                    to_label=_clean_label(to_m),
                    specialization=spec,
                    length_full_m=full_len,
                    length_useful_m=useful_len,
                )
            )

    deduped: list[PathBoundary] = []
    seen: set[tuple] = set()
    for b in boundaries:
        key = (b.path_number, b.from_label, b.to_label, b.specialization, b.length_full_m, b.length_useful_m)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(b)

    if total_full is None and total_useful is None and len(deduped) == 1:
        # если явной строки 'ИТОГО' в таблице нет (типично для
        # однопутевых предприятий, где итог избыточен), итоговая длина
        # по определению равна длине единственного пути
        total_full = deduped[0].length_full_m
        total_useful = deduped[0].length_useful_m

    return deduped, total_full, total_useful


# ---------------------------------------------------------------------------
# Раздел «нижнее строение пути» — таблицы "простого" вида: одно значение
# на путь (темы embankments/drainage/deformation/structures/road_crossings)
# ---------------------------------------------------------------------------


def _table_has_negative_answer(table: RawTable | None) -> bool | None:
    """
    Для таблиц вида 'Наличие насыпей/выемок', 'Наличие водоотводных
    сооружений' и т.п. типовой ответ — одно слово 'нет' в графе
    значения. Возвращает True, если хотя бы для одного пути есть
    непустое значение, отличное от 'нет'/'отсутствует', False если
    для всех путей explicit 'нет', None если таблица не найдена.

    Известное упрощение: при нескольких путях в одном техпаспорте
    (см. ООО «БИЛУГА», путь №3 — 'Насыпь лево'/'Насыпь право') это
    поле агрегирует ответ по всему предприятию, а не по каждому пути
    отдельно — детализация по путям видна в data.raw_tables_by_number
    (сырой текст таблицы) для ручной проверки.
    """
    if table is None:
        return None
    blob = " ".join(_row_text(r) for r in table.rows).lower()
    if not blob.strip():
        return None
    if re.search(r"\b(нет|отсутствуют?)\b", blob) and not re.search(
        r"\b(насыпь|выемк\w+|переезд|проезд|пересечен\w+)\b", blob
    ):
        return False
    return True


# ---------------------------------------------------------------------------
# Раздел «верхнее строение пути»
# ---------------------------------------------------------------------------

_SIMPLE_VALUE_TOPICS = [
    "ballast_type",
    "ballast_thickness",
    "ballast_pollution",
    "ballast_pollutability",
    "welded_joints",
    "joint_fasteners",
    "intermediate_fasteners",
    "anti_creepers",
]


_KNOWN_ENGINEER_SURNAMES = {"афанасенко", "егиазарян", "коннова", "городний", "баклаженко"}
_UPPER_STRUCTURE_NOISE_WORDS = {
    "гпнп", "знак", "пс", "упор", "остряк", "светофор", "свет.", "№", "путей",
    "граница", "стык", "р.р.", "дата", "внесения", "изменений", "ф.и.о.",
    "должность", "внесшего", "изменения", "подпись", "итого",
}


_UPPER_STRUCTURE_NOISE_RE = re.compile(
    r"ПК\d+\+\d{1,2}[.,]\d{1,2}|"                      # пикеты
    r"Х\.к\.\s*СП\d*|"                                  # 'Х.к.СП51' (хвост крестовины)
    r"ИП\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s?[А-ЯЁ]\.?|"       # 'ИП Цивинский Н.Н'
    r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.\s?[А-ЯЁ]\.?|"            # 'Афанасенко С.Н.' (ФИО)
    r"(?:ООО|ОАО|АО|ПАО|ЗАО)\s*[«\"][^»\"]+[»\"]|"     # название компании вместо номера пути
    r"Знак\s*ГПНП|ГПНП|ПС(?:\s*СП№?\d*)?|Остряк(?:\s*СП№?\d*)?|"
    r"Упор|Светофор(?:\s*М?\d*)?|свет\.(?:\s*М?\d*)?|"
    r"стык\s*р\.?р\.?\s*СП\S*|Конец\s*пути|"
    r"№\s*п\s*у\s*т\s*и|Граница\s*путей|"
    r"Дата\s*внесения\s*изменений|Ф\.И\.О\.|должность|внесшего|изменени[ея]|Подпись|"
    r"Изм\.|Кол\.уч\.|Кол\.\s|Лист\s*№?\s*док\.?|Подп\.\s*и\s*дата|Подп\.|"
    r"Инв\.\s*№?\s*подл\.?|Взам\.\s*Инв\.?\s*№?|Инв\.\s*№|"
    r"\d{3,4}\s*[-–—]\s*ТП\b|\bЛист\b",
    re.IGNORECASE,
)


def _extract_trailing_value(segment: str, path_number: str | None) -> str | None:
    """
    Извлекает значение ячейки из сегмента текста таблицы. Значение
    может стоять не строго в конце сегмента (перед датой), а между
    "шумовыми" фрагментами — например, в шаблоне 'ТЧГП' координаты
    пикета и ФИО инженера иногда оказываются ПОСЛЕ искомого значения,
    а не только перед ним, из-за беспорядочного порядка текста в PDF.
    Поэтому вместо позиционного "берём хвост" вычитаем все известные
    шумовые фразы (пикеты, ФИО, ГПНП/ПС/Остряк/Упор/Светофор и т.п.)
    регэкспами, а что осталось — и есть искомое значение.
    """
    cleaned = _UPPER_STRUCTURE_NOISE_RE.sub(" ", segment)
    cleaned = re.sub(
        r"\b(" + "|".join(_KNOWN_ENGINEER_SURNAMES) + r")\b", " ", cleaned, flags=re.IGNORECASE
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,;")
    if path_number:
        # убираем изолированный номер пути, если он остался в начале/конце
        cleaned = re.sub(rf"(?<!\S){re.escape(path_number)}(?!\S)", " ", cleaned)
        if " " in path_number or "-" in path_number:
            # составные номера ('МСУ 262-270') в PDF-линеаризации иногда
            # разрываются на части посторонним текстом — чистим и отдельные
            # фрагменты ('МСУ', '262-', '270'), а не только номер целиком
            for part in re.split(r"[\s-]+", path_number):
                if len(part) >= 2:
                    cleaned = re.sub(rf"(?<!\S){re.escape(part)}-?(?!\S)", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,;")
    return cleaned or None


def extract_track_superstructure(
    raw: RawDocument, known_path_numbers: list[str] | None = None
) -> list[TrackSuperstructure]:
    topics = raw.tables_by_topic()
    known_path_numbers = known_path_numbers or []
    by_path: dict[str, TrackSuperstructure] = {}

    def get(path_number: str) -> TrackSuperstructure:
        if path_number not in by_path:
            by_path[path_number] = TrackSuperstructure(path_number=path_number)
        return by_path[path_number]

    for topic in _SIMPLE_VALUE_TOPICS:
        table = topics.get(topic)
        if not table:
            continue
        # для PDF (см. _iter_path_rows) вся таблица нередко приходит
        # ОДНОЙ псевдострокой со всеми путями сразу — построчный поиск
        # 'цифра в начале строки' в этом случае не находит вообще ничего,
        # т.к. строка начинается с шапки таблицы, а не с номера пути
        for row_text, hint in _iter_path_rows(table, known_path_numbers):
            if re.match(r"\s*Итого\b", row_text, re.IGNORECASE):
                continue
            path_number = hint
            if not path_number:
                num_m = re.match(r"\s*(\d{1,3}[а-яА-Я]?)\s", row_text)
                if not num_m:
                    # строка не начинается с цифры (типичный кейс: в
                    # колонке "№ пути" вписано название компании вместо
                    # номера, как в границах путей) — если известен ровно
                    # один путь и это явно не строка заголовка таблицы
                    # (нет "№ пути"/"Граница путей"), считаем её данными
                    # этого единственного пути
                    if (
                        len(known_path_numbers) == 1
                        and not re.match(r"\s*№\s*пути\b", row_text, re.IGNORECASE)
                        and re.search(r"\d{2}\.\d{2}(?:\.\d{2,4})?", row_text)
                    ):
                        path_number = known_path_numbers[0]
                    else:
                        continue
                else:
                    path_number = num_m.group(1)
            # значение — сегмент строки перед датой (поддерживаем и
            # 'ММ.ГГГГ', и полный 'ДД.ММ.ГГГГг.' формат шаблона В).
            # Если даты в сегменте нет (например, она осталась ДО якоря
            # при разбиении PDF-блоба по номеру пути и не попала в этот
            # сегмент) — не пропускаем сегмент целиком, а используем его
            # полностью для последующей вычистки шума.
            date_m = re.search(r"(?<![+,\d])\d{1,2}\.\d{2}(?:\.\d{2,4})?г?\.?", row_text)
            before_date = row_text[: date_m.start()] if date_m else row_text
            # последняя "содержательная" группа слов перед датой обычно
            # и есть искомое значение (см. модуль docstring) — извлекаем
            # через обратный проход по токенам, отбрасывая известный шум
            value = _extract_trailing_value(before_date.strip(), path_number)
            if value and getattr(get(path_number), topic) is None:
                setattr(get(path_number), topic, value)

    for topic, field_name in (("sleepers", "sleepers_summary"), ("rails", "rails_summary")):
        table = topics.get(topic)
        if not table:
            continue
        blob = " ".join(_row_text(r) for r in table.rows)
        # итоговая сводная строка обычно начинается с "Итого"
        summary_m = re.search(r"Итого[^А-ЯЁа-яё]{0,5}[А-ЯЁа-яё :–\-]{1,40}[\d,.\s%№а-яёА-ЯЁ/]{1,22}", blob, re.IGNORECASE)
        if summary_m:
            summary_text = summary_m.group(0)
            # обрезаем по первому признаку мусора подвала страницы —
            # последовательность из отдельных 1-2-буквенных "слов" типа
            # 'П .л д о П' (артефакт перевёрнутого бокового текста бланка,
            # затесавшийся в конец совпадения из-за отсутствия следующей
            # таблицы на странице, см. pdf_parser.py::_PARAGRAPH_BREAK_RE)
            garbage_m = re.search(r"(?:\s[.\wА-Яа-яЁё]{1,2}){3,}", summary_text)
            if garbage_m:
                summary_text = summary_text[: garbage_m.start()]
            summary_text = clean_text(summary_text)
            for entry in by_path.values():
                if getattr(entry, field_name) is None:
                    setattr(entry, field_name, summary_text)
        elif by_path:
            # нет сводной строки 'Итого' (например, шаблон В, где сводки
            # по рельсам/шпалам нет вовсе, только по путям) — берём
            # значение по каждому пути отдельно
            for row_text, hint in _iter_path_rows(table, known_path_numbers):
                path_number = hint
                if not path_number:
                    num_m = re.match(r"\s*(\d{1,3}[а-яА-Я]?)\s", row_text)
                    if not num_m:
                        continue
                    path_number = num_m.group(1)
                if path_number not in by_path:
                    continue
                date_m = re.search(r"(?<![+,\d])\d{1,2}\.\d{2}(?:\.\d{2,4})?г?\.?", row_text)
                segment = row_text[: date_m.start()] if date_m else row_text
                value = _extract_trailing_value(segment.strip(), path_number)
                if value and getattr(by_path[path_number], field_name) is None:
                    setattr(by_path[path_number], field_name, value)

    return list(by_path.values())


def extract_switches_summary(raw: RawDocument) -> str | None:
    topics = raw.tables_by_topic()
    table = topics.get("switches_list")
    if not table:
        return None
    blob = " ".join(_row_text(r) for r in table.rows)
    # типовой случай — ведомость заполнена прочерками ('-'), т.е. на пути
    # предприятия нет собственных стрелочных переводов; отдавать пустой
    # шаблон таблицы (шапку без данных) как "значение" бессмысленно
    data_row_m = re.search(r"(?:^|\s)-(?:\s+-){3,}", blob)
    if data_row_m and not re.search(r"[А-Яа-я0-9]{2,}\s*Р\d{2}", blob):
        return None
    return clean_text(blob) or None


# ---------------------------------------------------------------------------
# Грузовые фронты (тема 'cargo_capacity' + описательный текст рядом)
# ---------------------------------------------------------------------------

# Формат (A)/(Б): 'ГФ1 – рампа ... Среднесуточный вагонооборот – 1 вагон...'
_CARGO_FRONT_BLOCK_RE_DASH = re.compile(
    r"(?P<id>ГФ\s?\d+|Грузовой\s+фронт\s*№?\s*\d+)\s*[–—-]\s*(?P<name>[^.]{0,60}?)\s*(?:\n|(?=Среднесуточный))"
    r"(?P<body>.*?)(?=(?:ГФ\s?\d+|Грузовой\s+фронт\s*№?\s*\d+)\s*[–—-]|Технический паспорт составлен|$)",
    re.IGNORECASE | re.DOTALL,
)

# Формат (В): '5.4.1 Технико-технологическая характеристика рампы (грузовой
# фронт №1): 1) Среднесуточный вагонооборот: ... 2) Перечень ... : ...'
# Скобки вокруг '(грузовой фронт №N)' часто есть, но не всегда — некоторые
# техпаспорта пишут прямо 'характеристика грузового фронта №1:' без них.
_CARGO_FRONT_BLOCK_RE_NUMBERED = re.compile(
    r"характеристика\s+[^:\n]{0,60}?грузов\w+\s+фронт\w*\s*№\s*(?P<id>\d+)\)?\s*:?"
    r"(?P<body>.*?)(?=(?:\d+\.\d+\.?\d*\s*[^:\n]{0,40}?)?характеристика\s+[^:\n]{0,60}?грузов\w+\s+фронт\w*\s*№|"
    r"Технический паспорт составлен|Данный технический паспорт|$)",
    re.IGNORECASE | re.DOTALL,
)


_CARGO_FIELD_STOP = r"(?=\.\s|\.\n|\.$|\s*\d\)|Средства механизации|Перечень перерабатываемых|Среднесуточный вагонооборот|$)"
_TURNOVER_RE = re.compile(
    r"Среднесуточный вагонооборот[^–\-:]*[–\-:]\s*([\s\S]+?)" + _CARGO_FIELD_STOP, re.IGNORECASE
)
_CARGO_LIST_RE = re.compile(
    r"Перечень перерабатываемых грузов[^–\-:]*[–\-:]\s*([\s\S]+?)" + _CARGO_FIELD_STOP, re.IGNORECASE
)
_DANGEROUS_RE = re.compile(
    r"Перечень перерабатываемых опасных грузов[^–\-:]*[–\-:]\s*([\s\S]+?)" + _CARGO_FIELD_STOP, re.IGNORECASE
)
_MECH_RE = re.compile(
    r"Средства механизации[^–\-:]*[–\-:]\s*([\s\S]+?)" + _CARGO_FIELD_STOP, re.IGNORECASE
)


# Формат (Г): '5.4.1 Технико-технологическая характеристика открытой
# площадки:' — без явного 'грузовой фронт №N' вообще; номер фронта
# берётся из номера подраздела (5.4.1 -> фронт №1).
_CARGO_FRONT_BLOCK_RE_SUBSECTION = re.compile(
    r"\d+\.\d+\.(?P<id>\d+)\s+Технико-технологическая\s+характеристика\s+"
    r"(?P<name>[^:\n]{0,60}):"
    r"(?P<body>.*?)(?=\d+\.\d+\.\d+\s+Технико-технологическая\s+характеристика|"
    r"Технический паспорт составлен|Данный технический паспорт|$)",
    re.IGNORECASE | re.DOTALL,
)


def extract_cargo_fronts(raw: RawDocument) -> list[CargoFront]:
    text = raw.full_text
    fronts: list[CargoFront] = []

    dash_matches = list(_CARGO_FRONT_BLOCK_RE_DASH.finditer(text))
    numbered_matches = list(_CARGO_FRONT_BLOCK_RE_NUMBERED.finditer(text))
    subsection_matches = list(_CARGO_FRONT_BLOCK_RE_SUBSECTION.finditer(text))
    # используем тот формат, который реально нашёл хотя бы один блок —
    # они взаимоисключающие для конкретного шаблона документа
    matches = dash_matches or numbered_matches or subsection_matches

    for m in matches:
        body = m.group("body")
        turnover_m = _TURNOVER_RE.search(body)
        cargo_m = _CARGO_LIST_RE.search(body)
        dangerous_m = _DANGEROUS_RE.search(body)
        mech_m = _MECH_RE.search(body)

        raw_id = m.group("id")
        front_id = raw_id if raw_id.upper().startswith("ГФ") else f"ГФ{raw_id}"
        front_id = clean_text(front_id).replace(" ", "")

        fronts.append(
            CargoFront(
                id=front_id,
                name=clean_text(m.groupdict().get("name") or "") or None,
                daily_turnover=clean_text(turnover_m.group(1)) if turnover_m else None,
                cargo_list=clean_text(cargo_m.group(1)) if cargo_m else None,
                dangerous_cargo=clean_text(dangerous_m.group(1)) if dangerous_m else None,
                mechanization=clean_text(mech_m.group(1)) if mech_m else None,
            )
        )

    # геометрия (путь/пикеты/длина/вместимость) — из таблицы темы
    # 'cargo_capacity', если найдена. Блоб таблицы режем на сегменты по
    # вхождениям 'ГФ<n>', чтобы данные одного грузового фронта не
    # утекали в соседний при последовательном поиске по всему тексту
    # таблицы разом.
    topics = raw.tables_by_topic()
    t_cap = topics.get("cargo_capacity")
    if t_cap:
        blob = " ".join(_row_text(r) for r in t_cap.rows)
        segments = re.split(r"(?=ГФ\s?\d+\b)", blob)
        for segment in segments:
            id_m = re.match(r"\s*ГФ\s?(\d+)", segment)
            if not id_m:
                continue
            front_id = f"ГФ{id_m.group(1)}"
            # берём только "геометрическую" часть сегмента, до следующего
            # смыслового блока (описание грузов и т.п. парсится отдельно
            # выше, из свободного текста)
            geo_part = segment[:200]

            target = next((f for f in fronts if f.id == front_id), None)
            if target is None:
                target = CargoFront(id=front_id)
                fronts.append(target)

            pickets = re.findall(r"ПК\d+\+\d{1,2}[.,]\d{1,2}|\d{2}\+\d{2}[.,]\d{2}", geo_part)
            if len(pickets) >= 2:
                target.from_picket, target.to_picket = pickets[0], pickets[1]

            path_m = re.search(r"\s(\d{1,3}[а-яА-Я]?)\s+(?:ПК\d|\d{2}\+)", geo_part)
            if path_m:
                target.path_number = path_m.group(1)

            len_m = re.search(
                r"(?:ПК\d+\+\d{1,2}[.,]\d{1,2}|\d{2}\+\d{2}[.,]\d{2})\s+([\d]+[.,]\d+)\b", geo_part
            )
            if len_m:
                target.length_m = to_float(len_m.group(1))

            cap_m = re.search(
                r"\d+\s*(?:кр\.|пв\.|пл\.|вагон\w*)(?:\s*,?\s*\d*\s*(?:кр\.|пв\.|пл\.))?", geo_part
            )
            if cap_m:
                target.capacity = clean_text(cap_m.group(0))

    return fronts


# ---------------------------------------------------------------------------
# Точка входа модуля
# ---------------------------------------------------------------------------


def normalize(raw: RawDocument, source_file: str, source_format: str) -> TechPassportData:
    data = TechPassportData(source_file=source_file, source_format=source_format)

    data.general = extract_general_info(raw)

    boundaries, total_full, total_useful = extract_path_boundaries_and_lengths(
        raw, known_path_numbers=data.general.path_numbers
    )
    data.path_boundaries = boundaries
    data.total_length_full_m = total_full
    data.total_length_useful_m = total_useful

    # номера путей, реально разрешённые при разборе границ (включая
    # синтетический fallback '1' для однопутевых предприятий без цифры
    # в колонке "№ пути" — см. _count_data_rows), надёжнее сырого
    # meta.path_numbers и переиспользуются для верхнего строения пути,
    # чтобы обе секции были согласованы по номерам путей
    effective_path_numbers = [b.path_number for b in boundaries if b.path_number] or data.general.path_numbers

    topics = raw.tables_by_topic()
    data.embankments_present = _table_has_negative_answer(topics.get("embankments"))
    data.drainage_present = _table_has_negative_answer(topics.get("drainage"))
    data.deformation_present = _table_has_negative_answer(topics.get("deformation"))
    data.structures_present = _table_has_negative_answer(topics.get("structures"))
    data.road_crossings_present = _table_has_negative_answer(topics.get("road_crossings"))

    data.track_superstructure = extract_track_superstructure(raw, known_path_numbers=effective_path_numbers)
    data.switches_summary = extract_switches_summary(raw)

    data.cargo_fronts = extract_cargo_fronts(raw)

    data.raw_tables_by_number = {
        f"{num} ({t.caption})" if t.caption else num: " ".join(_row_text(r) for r in t.rows)
        for num, t in raw.tables_by_number().items()
    }

    return data
