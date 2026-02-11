from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from config import AppConfig


class OpenRouterError(RuntimeError):
    """Ошибки вызова OpenRouter (сеть, авторизация, лимиты, формат ответа)."""


@dataclass
class LLMResponse:
    text: str
    raw: Dict[str, Any]


class OpenRouterClient:
    """
    Мини-клиент для OpenRouter Chat Completions.

    Цели:
    - модульность (поменять провайдера/модель без переписывания проекта)
    - стабильность (retry, понятные ошибки)
    - поддержка случаев, когда content пустой из-за лимита токенов,
      а модель успела "подумать" (reasoning), но не успела вывести ответ.
    """

    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.base_url = cfg.openrouter_base_url.rstrip("/")
        self.session = requests.Session()

        # Эти заголовки рекомендованы OpenRouter (идентификация приложения)
        self.headers = {
            "Authorization": f"Bearer {cfg.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "folder-summarizer",
        }

    def chat(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 800,
        extra: Optional[Dict[str, Any]] = None,
        retries: int = 2,
        retry_sleep_sec: float = 1.2,
        # внутренний флаг, чтобы авто-ретрай "по длине" не ушёл в бесконечность
        _length_retry_done: bool = False,
    ) -> LLMResponse:
        """
        Делает запрос к LLM и возвращает текст + сырой JSON.
        """

        url = f"{self.base_url}/chat/completions"

        payload: Dict[str, Any] = {
            "model": self.cfg.openrouter_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if extra:
            payload.update(extra)

        last_err: Optional[Exception] = None

        for attempt in range(retries + 1):
            try:
                resp = self.session.post(
                    url,
                    headers=self.headers,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    timeout=self.cfg.request_timeout_sec,
                )

                # Частые случаи ошибок — сразу нормальными сообщениями
                if resp.status_code in (401, 403):
                    raise OpenRouterError(
                        "Ошибка авторизации (401/403). Проверь OPENROUTER_API_KEY."
                    )
                if resp.status_code == 429:
                    raise OpenRouterError(
                        "Лимит запросов (429). Попробуй позже или уменьшай частоту/объём."
                    )
                if resp.status_code >= 500:
                    raise OpenRouterError(
                        f"Ошибка сервера OpenRouter ({resp.status_code})."
                    )

                data = resp.json()

                # OpenRouter иногда возвращает { "error": {...} } даже при 200/4xx
                if isinstance(data, dict) and "error" in data:
                    err = data["error"] or {}
                    msg = err.get("message", "Unknown error")
                    code = err.get("code", resp.status_code)
                    raise OpenRouterError(f"OpenRouter error {code}: {msg}")

                # Основной путь: chat.completion -> choices[0].message.content
                choice = (data.get("choices") or [{}])[0]
                msg = (choice.get("message") or {})

                text = (msg.get("content") or "").strip()
                finish_reason = choice.get("finish_reason")

                # 1) Если модель упёрлась в лимит и не успела вывести content — повторяем с большим max_tokens
                if (not text) and (finish_reason == "length") and (max_tokens is not None):
                    if not _length_retry_done:
                        bigger = max(256, int(max_tokens * 3))
                        # короткая задержка, чтобы не долбить одинаково
                        time.sleep(0.2)
                        return self.chat(
                            system=system,
                            user=user,
                            temperature=temperature,
                            max_tokens=bigger,
                            extra=extra,
                            retries=retries,
                            retry_sleep_sec=retry_sleep_sec,
                            _length_retry_done=True,
                        )

                # 2) Если content пустой — покажем понятную ошибку
                if not text:
                    reasoning = (msg.get("reasoning") or "")
                    hint = ""
                    if reasoning:
                        hint = " (есть reasoning, но content пустой — увеличь max_tokens или измени промпт)"
                    raise OpenRouterError(
                        f"Пустой content от модели. finish_reason={finish_reason}.{hint} "
                        f"Raw: {str(data)[:700]}"
                    )

                return LLMResponse(text=text, raw=data)

            except (requests.RequestException, ValueError, OpenRouterError) as e:
                last_err = e
                if attempt < retries:
                    time.sleep(retry_sleep_sec * (attempt + 1))
                    continue
                break

        raise OpenRouterError(f"Не удалось получить ответ от OpenRouter: {last_err}")
