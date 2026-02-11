from __future__ import annotations

from pathlib import Path
from typing import Optional

from pypdf import PdfReader

from src.loaders.base import LoadedDoc


def load_pdf(path: str | Path) -> LoadedDoc:
    p = Path(path)
    reader = PdfReader(str(p))

    parts: list[str] = []
    for page in reader.pages:
        text: Optional[str] = page.extract_text()
        if text:
            parts.append(text)

    joined = "\n\n".join(parts).strip()
    return LoadedDoc(path=p, text=joined, loader="pdf")
