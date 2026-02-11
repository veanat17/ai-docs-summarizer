from __future__ import annotations

from pathlib import Path

from src.loaders.base import LoadedDoc
from src.loaders.docx import load_docx
from src.loaders.pdf import load_pdf
from src.loaders.text import load_text_file
from src.loaders.image_ocr import load_image_ocr


def load_document(path: str | Path) -> LoadedDoc:
    p = Path(path)
    ext = p.suffix.lower()

    if ext == ".pdf":
        return load_pdf(p)
    if ext == ".docx":
        return load_docx(p)
    if ext in {".txt", ".md"}:
        return load_text_file(p)
    if ext in {".jpg", ".jpeg", ".png", ".webp"}:
        return load_image_ocr(p)

    return LoadedDoc(path=p, text="", loader="unknown")
