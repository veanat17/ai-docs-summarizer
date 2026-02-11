from __future__ import annotations

from pathlib import Path

from docx import Document

from src.loaders.base import LoadedDoc


def load_docx(path: str | Path) -> LoadedDoc:
    p = Path(path)
    doc = Document(str(p))

    parts: list[str] = []
    for para in doc.paragraphs:
        if para.text:
            parts.append(para.text)

    text = "\n".join(parts).strip()
    return LoadedDoc(path=p, text=text, loader="docx")
