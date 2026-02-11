from __future__ import annotations

import os
from pathlib import Path

from PIL import Image
import pytesseract

from src.loaders.base import LoadedDoc


def _configure_tesseract_if_needed() -> None:
    """
    На Windows tesseract.exe может не быть в PATH.
    Можно задать путь через переменную окружения TESSERACT_CMD.
    Например:
      TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
    """
    cmd = os.getenv("TESSERACT_CMD", "").strip()
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


def load_image_ocr(path: str | Path, lang: str = "rus+eng") -> LoadedDoc:
    p = Path(path)
    _configure_tesseract_if_needed()

    try:
        img = Image.open(str(p))
        text = pytesseract.image_to_string(img, lang=lang)
        text = (text or "").strip()
        return LoadedDoc(path=p, text=text, loader="image_ocr")
    except Exception as e:
        # Не падаем, а возвращаем пусто и причину (в тексте)
        return LoadedDoc(
            path=p,
            text=f"OCR не удалось выполнить: {e}",
            loader="image_ocr_error",
        )
