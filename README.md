# AI Folder Docs Summarizer (OpenRouter, Free Models)

Небольшой проект для тестового задания: программа проходит по папке с документами, извлекает текст из файлов разных типов и формирует:
1) саммари по каждому файлу  
2) итоговое общее саммари по всей папке

Поддерживаемые типы:
- **PDF** (текстовый слой)  
- **DOCX**
- **TXT / MD**
- **Изображения**: JPG/JPEG/PNG/WEBP через OCR (Tesseract)

LLM: **OpenRouter** (используются бесплатные модели `:free`).

---

## Что получается на выходе

После запуска создаётся папка `output/`:

- `output/by_file.json` — саммари по каждому файлу  
- `output/folder_summary.md` — итоговое саммари по всей папке  
- `output/meta.json` — техническая информация (какой loader использовался, длина текста и т.п.)

Формат саммари “юридически удобный”:
- Темы
- Ключевые пункты
- Даты
- Суммы
- Риски / спорные места
- Что нужно уточнить у клиента

Антигаллюцинации:
- если данных нет → **"не найдено"**
- если OCR-данные искажены → **"неразборчиво"**
- запрет формулировок “вероятно/скорее всего/предположительно”

---

## Структура проекта

├── main.py
├── config.py
├── requirements.txt
├── src
│ ├── llm
│ │ ├── openrouter_client.py # клиент OpenRouter + retry/стабильность
│ │ └── prompts.py # промпты (структура + антигаллюцинации)
│ ├── loaders
│ │ ├── base.py # базовые типы
│ │ ├── pdf.py # извлечение текста из PDF
│ │ ├── docx.py # извлечение текста из DOCX
│ │ ├── text.py # TXT/MD
│ │ ├── image_ocr.py # OCR изображений (Tesseract)
│ │ └── init.py # роутинг по расширениям
│ ├── summarize
│ │ ├── chunking.py # нарезка текста на чанки
│ │ ├── summarize_doc.py # саммари одного документа + автопродолжение
│ │ └── summarize_folder.py # общее саммари по папке
│ └── utils
│ ├── files.py # обход папки, фильтрация расширений
│ └── logging.py # логирование
└── tools
├── ping_openrouter.py # проверка ключа
├── list_free_models.py # список free моделей
└── find_working_model.py # поиск реально рабочей free модели

2) Переменные окружения (.env)

Создайте файл .env в корне проекта:

OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=stepfun/step-3.5-flash:free
DOCS_DIR=H:\Neural Networks\docs
OUTPUT_DIR=output


Опционально (если tesseract не в PATH):
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

Опционально (ограничить количество файлов для быстрого теста):
MAX_FILES=5


OCR для изображений (Tesseract)

Для OCR нужен установленный Tesseract OCR.

Проверка (если добавлен в PATH):

tesseract --version
Если в PATH не добавлен — достаточно указать TESSERACT_CMD в .env.
например:
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe 

Запуск - python main.py


После завершения смотрите результаты:

output/folder_summary.md

output/by_file.json