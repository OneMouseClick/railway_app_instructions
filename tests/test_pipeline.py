"""
Smoke- и регресс-тесты пайплайна на реальных техпаспортах трёх шаблонов
бланка (АО «ВНИИЖТ», ООО «Забтранспроект», шаблон «ТЧГП»), включая
одно- и многопутевые предприятия (до 4 путей в одном техпаспорте).

Запуск: pytest -q  (из корня tp_parser_service, с образцами в
переменной TP_SAMPLES_DIR — по умолчанию /mnt/user-data/uploads)
"""
import os
import pytest
from pathlib import Path

from app.pipeline import parse_tech_passport

current_dir = Path(__file__).parent
SAMPLES_DIR = current_dir / "tech_passports"

# (файл, ожидаемое количество путей, ожидаемое количество путей с данными
# верхнего строения — они должны совпадать, это регресс-тест на баг
# "верхнее строение пустое для PDF, хотя пути найдены")
SAMPLES = [
    ("ТП ООО МеталлСнаб путь №2 2025.pdf", 1),
    ("ТП Цивинский 25.09.2023.pdf", 2),
    ("ТП АО Читаглавснаб 13.05.2025.pdf", 1),
    ("ТП ООО ВСТК.pdf", 1),
    ("Техпаспорт ООО ЗЛП 2024.pdf", 3),
    ("Техпаспорт_ООО_Русский_экспорт_Кадала.pdf", 3),
    ("Судостроительный_завод_СЗОР_Благовещенск_30_05_24.doc", 2),
    ("Тех. паспорт ООО Билуга (1).doc", 4),
    ("Техпаспорт Труд_Благовещенск 2024.doc", 1),
    ("Техпаспорт Читаоблгаз 2024г.doc", 4),
    ("ТП ООО ЗабайкалТехноИнвест 28.05.24.pdf", 1),
    ("ТП ООО РОССЫПЬ 2024 (1).pdf", 1),
]


@pytest.mark.parametrize("filename,min_paths", SAMPLES)
def test_parses_without_error(filename, min_paths):
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"нет файла-образца {path}")
    result = parse_tech_passport(path)
    assert "meta" in result
    assert "section_1_general_characteristics" in result
    assert "section_2_supply_removal_procedure" in result


@pytest.mark.parametrize("filename,min_paths", SAMPLES)
def test_company_name_extracted(filename, min_paths):
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"нет файла-образца {path}")
    result = parse_tech_passport(path)
    assert result["meta"]["company_name"], "название владельца пути должно извлекаться всегда"


@pytest.mark.parametrize("filename,min_paths", SAMPLES)
def test_multipath_not_collapsed(filename, min_paths):
    """Регресс-тест: для многопутевых предприятий все пути не должны схлопываться в один."""
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"нет файла-образца {path}")
    result = parse_tech_passport(path)
    paths_data = result["section_1_general_characteristics"]["1.6"]["path_lengths"]["data"]["paths"]
    n_found = len(paths_data or [])
    assert n_found >= min_paths, f"{filename}: ожидалось не менее {min_paths} путей, найдено {n_found}"
    if paths_data:
        numbers = [p.get("path_number") for p in paths_data]
        assert len(set(numbers)) == len(numbers), f"{filename}: дублирующиеся номера путей в {numbers}"


@pytest.mark.parametrize("filename,min_paths", SAMPLES)
def test_upper_structure_matches_path_count(filename, min_paths):
    """
    Регресс-тест на баг: для PDF-техпаспортов (таблица приходит одной
    псевдострокой) верхнее строение пути раньше не находилось вовсе,
    хотя пути (1.6) успешно извлекались.
    """
    path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        pytest.skip(f"нет файла-образца {path}")
    result = parse_tech_passport(path)
    s1 = result["section_1_general_characteristics"]
    n_paths = len(s1["1.6"]["path_lengths"]["data"]["paths"] or [])
    n_upper = len(s1["upper_structure"]["data"]["by_path"] or [])
    assert n_upper == n_paths, (
        f"{filename}: число путей с данными верхнего строения ({n_upper}) "
        f"не совпадает с числом путей ({n_paths})"
    )


def test_metallsnab_cargo_fronts():
    path = os.path.join(SAMPLES_DIR, "ТП_ООО_МеталлСнаб_путь__2_2025.pdf")
    if not os.path.exists(path):
        pytest.skip("нет файла-образца")
    result = parse_tech_passport(path)
    fronts = result["section_1_general_characteristics"]["1.9"]["cargo_fronts"]["data"]
    assert fronts is not None
    assert len(fronts) == 2
    assert {f["id"] for f in fronts} == {"ГФ1", "ГФ2"}


def test_tsivinsky_is_individual_entrepreneur():
    """Регресс-тест: владелец пути (ИП) не должен определяться как проектная организация."""
    path = os.path.join(SAMPLES_DIR, "ТП_Цивинский_25_09_2023.pdf")
    if not os.path.exists(path):
        pytest.skip("нет файла-образца")
    result = parse_tech_passport(path)
    assert result["meta"]["company_name"].startswith("ИП")


def test_rossyp_path_number_is_own_not_adjacent():
    """
    Регресс-тест: номер пути должен браться из титульной строки 'Путь №22',
    а не из упоминания ЧУЖОГО, соединительного пути ('...пути №5 ст. Бада')
    в тексте 'Место примыкания'.
    """
    path = os.path.join(SAMPLES_DIR, "ТП_ООО_РОССЫПЬ_2024__1_.pdf")
    if not os.path.exists(path):
        pytest.skip("нет файла-образца")
    result = parse_tech_passport(path)
    paths_data = result["section_1_general_characteristics"]["1.6"]["path_lengths"]["data"]["paths"]
    numbers = {p.get("path_number") for p in (paths_data or [])}
    assert "22" in numbers, f"ожидался путь №22, найдено: {numbers}"
    assert "5" not in numbers, "путь №5 — соседний путь, принадлежащий другому предприятию"
