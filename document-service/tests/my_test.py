from app.pipeline import parse_tech_passport
import json
from pathlib import Path

current_dir = Path(__file__).parent
input_dir = current_dir / "tech_passports"

files = [
         "Техпаспорт ООО ЗЛП 2024.pdf",
         "Техпаспорт_ООО_Русский_экспорт_Кадала.pdf",
        "ТП АО Читаглавснаб 13.05.2025.pdf",
         "ТП ООО ВСТК.pdf",
         "ТП ООО ЗабайкалТехноИнвест 28.05.24.pdf",
         "ТП ООО МеталлСнаб путь №2 2025.pdf",
         "ТП ООО РОССЫПЬ 2024 (1).pdf",
         "ТП Цивинский 25.09.2023.pdf",
         "Судостроительный_завод_СЗОР_Благовещенск_30_05_24.doc",
         "Тех. паспорт ООО Билуга (1).doc",
         "Техпаспорт Труд_Благовещенск 2024.doc",
         "Техпаспорт Читаоблгаз 2024г.doc"
         ]

for i in files:
    input_file = input_dir / i
    # Создаем путь к выходному файлу (меняем расширение на .json)
    output_file = str(Path(input_file).with_suffix('.json'))

    result = parse_tech_passport(input_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Результат сохранен в файл: {output_file}")