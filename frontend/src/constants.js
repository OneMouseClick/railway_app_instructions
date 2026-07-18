export const STATIONS = ['Чита I', 'Кадала', 'Благовещенск', 'Бада']

export const PROCESSING_STEPS = [
  'Файл загружен',
  'Распознаём текст и таблицы',
  'Извлекаем данные технического паспорта',
  'Формируем инструкцию для выбранной станции',
  'Собираем итоговый документ',
  'Инструкция готова',
]

export const STATUS_META = {
  CREATED: { label: 'Файл загружен', progress: 8, step: 0 },
  PARSING: { label: 'Распознаём документ', progress: 25, step: 1 },
  PARSED: { label: 'Данные извлечены', progress: 45, step: 2 },
  GENERATING: { label: 'Формируем инструкцию', progress: 62, step: 3 },
  GENERATED: { label: 'Инструкция сформирована', progress: 78, step: 4 },
  ASSEMBLING: { label: 'Собираем PDF', progress: 92, step: 4 },
  COMPLETED: { label: 'Готова', progress: 100, step: 5 },
  FAILED: { label: 'Ошибка', progress: 100, step: 5 },
}

export const TERMINAL_STATUSES = new Set(['COMPLETED', 'FAILED'])
