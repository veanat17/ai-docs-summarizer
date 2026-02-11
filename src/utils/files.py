from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set


DEFAULT_EXTS: Set[str] = {
    ".pdf", ".docx", ".txt", ".md",
    ".jpg", ".jpeg", ".png", ".webp"
}


@dataclass(frozen=True)
class FileItem:
    path: Path
    ext: str


def iter_files(
    root: Path,
    *,
    exts: Optional[Sequence[str]] = None,
    recursive: bool = True,
) -> List[FileItem]:
    """
    Собирает список файлов в папке root.
    - recursive=True: ходим по подпапкам
    - exts: список расширений (например [".pdf", ".docx"])
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"Папка не найдена: {root}")

    allowed = set(e.lower() for e in (exts or DEFAULT_EXTS))

    pattern = "**/*" if recursive else "*"
    items: List[FileItem] = []

    for p in root.glob(pattern):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in allowed:
            items.append(FileItem(path=p, ext=ext))

    # Стабильная сортировка: сначала по расширению, потом по имени
    items.sort(key=lambda x: (x.ext, x.path.name.lower()))
    return items
