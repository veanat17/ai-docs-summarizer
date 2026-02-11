from __future__ import annotations

from typing import Dict, List

from config import AppConfig
from src.llm.openrouter_client import OpenRouterClient


FOLDER_SYSTEM_RU = """\
Ты — помощник юриста. Составь общий итог по папке документов.
Правила:
1) Не выдумывай факты. Если нет данных — пиши "не найдено".
2) Пиши кратко, структурированно, по-русски.
3) Основывайся ТОЛЬКО на саммари отдельных файлов, которые тебе дали.
"""


def summarize_folder(cfg: AppConfig, llm: OpenRouterClient, summaries_by_file: Dict[str, str]) -> str:
    if not summaries_by_file:
        return "В папке нет обработанных документов."

    # Собираем единый контекст из саммари файлов (не исходных текстов!)
    blocks: List[str] = []
    for filename, summ in summaries_by_file.items():
        blocks.append(f"## Файл: {filename}\n{summ}")

    combined = "\n\n".join(blocks)

    user_prompt = f"""\
Составь ОБЩЕЕ саммари по всей папке на основе сводок файлов ниже.

Формат Markdown:

# Итог по папке

## Общие темы
- ...

## Самое важное (кратко)
- ...

## Даты
- ... (или "не найдено")

## Суммы
- ... (или "не найдено")

## Риски / спорные места
- ...

## Что уточнить у клиента (общие вопросы)
- ...

Сводки по файлам (это единственный источник правды):
---
{combined}
---
"""

    resp = llm.chat(
        system=FOLDER_SYSTEM_RU,
        user=user_prompt,
        max_tokens=2200,
    )
    return resp.text
