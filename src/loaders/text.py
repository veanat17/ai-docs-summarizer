from __future__ import annotations

from pathlib import Path

from src.loaders.base import LoadedDoc


def load_text_file(path: str | Path, encoding: str = "utf-8") -> LoadedDoc:
    p = Path(path)
    # На Windows иногда попадаются файлы в cp1251. Сделаем fallback.
    try:
        text = p.read_text(encoding=encoding, errors="strict")
    except UnicodeDecodeError:
        text = p.read_text(encoding="cp1251", errors="replace")

    return LoadedDoc(path=p, text=text.strip(), loader="text")
