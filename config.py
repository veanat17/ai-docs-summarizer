from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Загружаем переменные окружения из .env 
load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    # Пути
    project_root: Path
    docs_dir: Path
    output_dir: Path

    # OpenRouter
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str

    # Параметры саммари / чанкинга
    chunk_size_chars: int
    chunk_overlap_chars: int
    max_files: int | None

    # Прочее
    request_timeout_sec: int
    debug: bool


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config() -> AppConfig:
    project_root = Path(__file__).resolve().parent

    docs_dir = Path(os.getenv("DOCS_DIR", "docs"))
    if not docs_dir.is_absolute():
        docs_dir = (project_root / docs_dir).resolve()

    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Не найден OPENROUTER_API_KEY. "
            "Добавь его в .env или в переменные окружения Windows."
        )

    model = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free").strip()
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()

    chunk_size_chars = int(os.getenv("CHUNK_SIZE_CHARS", "12000"))
    chunk_overlap_chars = int(os.getenv("CHUNK_OVERLAP_CHARS", "800"))

    max_files_raw = os.getenv("MAX_FILES", "").strip()
    max_files = int(max_files_raw) if max_files_raw else None

    timeout_sec = int(os.getenv("REQUEST_TIMEOUT_SEC", "60"))
    debug = _env_bool("DEBUG", False)

    return AppConfig(
        project_root=project_root,
        docs_dir=docs_dir,
        output_dir=output_dir,
        openrouter_api_key=api_key,
        openrouter_model=model,
        openrouter_base_url=base_url,
        chunk_size_chars=chunk_size_chars,
        chunk_overlap_chars=chunk_overlap_chars,
        max_files=max_files,
        request_timeout_sec=timeout_sec,
        debug=debug,
    )
