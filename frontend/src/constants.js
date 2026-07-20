export const STATIONS = ['Чита I', 'Кадала', 'Благовещенск', 'Бада']

export const PROCESSING_STEPS = [
  'Файл загружен',
  'Распознаём текст и таблицы',
  'Извлекаем данные технического паспорта',
  'Подбираем данные по выбранной станции',
  'Формируем разделы документа',
  'Собираем итоговую инструкцию',
]

export const STATUS_META = {
  CREATED: { label: 'Файл загружен', progress: 8, step: 0 },
  PARSING: { label: 'Распознаём документ', progress: 25, step: 1 },
  PARSED: { label: 'Данные извлечены', progress: 45, step: 2 },
  GENERATING: { label: 'Формируем инструкцию', progress: 63, step: 3 },
  GENERATED: { label: 'Разделы сформированы', progress: 80, step: 4 },
  ASSEMBLING: { label: 'Собираем документ', progress: 93, step: 5 },
  COMPLETED: { label: 'Готова', progress: 100, step: 5 },
  FAILED: { label: 'Ошибка', progress: 100, step: 5 },
}

export const ACTIVE_STATUSES = new Set([
  'CREATED',
  'PARSING',
  'PARSED',
  'GENERATING',
  'GENERATED',
  'ASSEMBLING',
])

export const TERMINAL_STATUSES = new Set(['COMPLETED', 'FAILED'])
