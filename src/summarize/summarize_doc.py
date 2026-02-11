from __future__ import annotations

from typing import List

from config import AppConfig
from src.llm.openrouter_client import OpenRouterClient
from src.llm.prompts import SYSTEM_SUMMARIZER_RU, make_doc_summary_user_prompt
from src.summarize.chunking import chunk_text


def _finish_reason_is_length(resp_raw: dict) -> bool:
    try:
        choice = (resp_raw.get("choices") or [{}])[0]
        return choice.get("finish_reason") == "length"
    except Exception:
        return False


def _looks_truncated(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    # если конец выглядит как обрыв (нет точки/закрытия/или заканчивается на "...")
    bad_endings = (",", ":", "-", "(", "реальный", "упущенная", "и")
    if t.endswith(bad_endings):
        return True
    # если последний символ не "конец мысли"
    if t[-1] not in ".!?)]\"»":
        return True
    return False


def summarize_document_text(cfg: AppConfig, llm: OpenRouterClient, text: str) -> str:
    chunks = chunk_text(text, cfg.chunk_size_chars, cfg.chunk_overlap_chars)
    if not chunks:
        return "Документ пустой или текст не извлечён."

    # Если документ маленький — суммарим сразу
    if len(chunks) == 1:
        resp = llm.chat(
            system=SYSTEM_SUMMARIZER_RU,
            user=make_doc_summary_user_prompt(chunks[0]),
            max_tokens=2200,
        )

        result = resp.text
        last_raw = resp.raw  # <-- важно: храним raw последнего ответа

        # Автопродолжение: максимум 2 попытки
        for _ in range(2):
            if not (_finish_reason_is_length(last_raw) or _looks_truncated(result)):
                break

            cont = llm.chat(
                system="Ты продолжаешь текст. Не повторяй уже написанное. Сохрани стиль и формат.",
                user=(
                    "Текст оборвался. Продолжи с места обрыва и допиши до логического завершения.\n\n"
                    "ВАЖНО: Не повторяй уже написанное. Не добавляй новых фактов. "
                    "Если данных нет — пиши 'не найдено'.\n\n"
                    "ТЕКСТ, КОТОРЫЙ УЖЕ ЕСТЬ:\n"
                    f"{result}\n\n"
                    "ПРОДОЛЖЕНИЕ (только недостающая часть):"
                ),
                max_tokens=1200,
            )

            # Добавляем продолжение
            result = (result.rstrip() + "\n" + cont.text.lstrip()).strip()
            last_raw = cont.raw  # <-- важно: обновляем raw

        return result



    # Если кусков много — суммарим по кускам, потом объединяем
    partial_summaries: List[str] = []
    for idx, ch in enumerate(chunks, start=1):
        resp = llm.chat(
            system=SYSTEM_SUMMARIZER_RU,
            user=make_doc_summary_user_prompt(ch),
            max_tokens=2200,
        )
        partial_summaries.append(f"### Часть {idx}\n{resp.text}")

    combined = "\n\n".join(partial_summaries)

    # Финальная “сборка” из частичных саммари
    resp_final = llm.chat(
        system=SYSTEM_SUMMARIZER_RU,
        user=(
            "Собери финальную единую сводку по документу по шаблону. "
            "Источник — только частичные сводки ниже. "
            "Если чего-то нет — пиши 'не найдено'.\n\n"
            + combined
        ),
        max_tokens=2200,
    )
    return resp_final.text
