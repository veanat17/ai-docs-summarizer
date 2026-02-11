from __future__ import annotations

import json
from pathlib import Path

from config import load_config
from src.llm.openrouter_client import OpenRouterClient
from src.loaders import load_document
from src.summarize.summarize_doc import summarize_document_text
from src.summarize.summarize_folder import summarize_folder
from src.utils.files import iter_files
from src.utils.logging import setup_logging


def main() -> None:
    cfg = load_config()
    setup_logging(cfg.debug)

    print("DOCS:", cfg.docs_dir)
    print("MODEL:", cfg.openrouter_model)

    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    llm = OpenRouterClient(cfg)

    items = iter_files(cfg.docs_dir, recursive=True)
    if cfg.max_files is not None:
        items = items[: cfg.max_files]

    print(f"FILES FOUND: {len(items)}")

    summaries_by_file: dict[str, str] = {}
    meta: list[dict] = []

    for i, item in enumerate(items, start=1):
        loaded = load_document(item.path)
        text = loaded.text or ""

        print(f"\n[{i}/{len(items)}] {loaded.path.name} | loader={loaded.loader} | text_len={len(text)}")

        if not text.strip():
            summaries_by_file[loaded.path.name] = "Текст не извлечён или файл пустой."
            meta.append(
                {
                    "file": loaded.path.name,
                    "loader": loaded.loader,
                    "text_len": len(text),
                    "status": "empty",
                }
            )
            continue

        summary = summarize_document_text(cfg, llm, text)
        summaries_by_file[loaded.path.name] = summary

        meta.append(
            {
                "file": loaded.path.name,
                "loader": loaded.loader,
                "text_len": len(text),
                "status": "ok",
            }
        )

    # Общее саммари по папке
    folder_summary = summarize_folder(cfg, llm, summaries_by_file)

    # Сохранение результатов
    by_file_path = cfg.output_dir / "by_file.json"
    folder_path = cfg.output_dir / "folder_summary.md"
    meta_path = cfg.output_dir / "meta.json"

    by_file_path.write_text(
        json.dumps(summaries_by_file, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    folder_path.write_text(folder_summary, encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nDONE ✅")
    print("Saved:", by_file_path)
    print("Saved:", folder_path)
    print("Saved:", meta_path)


if __name__ == "__main__":
    main()
