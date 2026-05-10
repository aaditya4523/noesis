import importlib
import json
import sys
from pathlib import Path

import pytest

from noesis.chunking import generate_run_chunks
from noesis.storage import (
    load_run_chunks_from_sqlite,
    load_run_record_from_sqlite,
    load_run_sections_from_sqlite,
    load_run_sources_from_sqlite,
    save_run_chunks_sqlite,
)


def test_save_run_chunks_sqlite_creates_database_file(tmp_path: Path):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="sqlite-run",
        topic="SQLite Storage",
        max_sources=1,
        source_id="source-001",
        final_url="https://example.com/sqlite",
        title="SQLite Notes",
        headings=["SQLite Notes"],
        text="SQLite stores structured records in a single local file.",
        source_type="official",
    )

    db_path = save_run_chunks_sqlite(generate_run_chunks(run_path), run_path)

    assert db_path == run_path / "evidence" / "noesis.db"
    assert db_path.exists()


def test_save_run_chunks_sqlite_persists_run_and_source_records(tmp_path: Path):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="sqlite-run",
        topic="SQLite Storage",
        max_sources=1,
        source_id="source-001",
        final_url="https://example.com/sqlite",
        title="SQLite Notes",
        headings=["SQLite Notes"],
        text="SQLite stores structured records in a single local file.",
        source_type="official",
    )

    save_run_chunks_sqlite(generate_run_chunks(run_path), run_path)

    assert load_run_record_from_sqlite(run_path) == {
        "run_id": "sqlite-run",
        "topic": "SQLite Storage",
    }
    assert load_run_sources_from_sqlite(run_path) == [
        {
            "source_id": "source-001",
            "run_id": "sqlite-run",
            "url": "https://example.com/sqlite",
            "final_url": "https://example.com/sqlite",
            "title": "SQLite Notes",
            "domain": "example.com",
            "source_type": "official",
            "content_type": "text/html",
        }
    ]


def test_save_run_chunks_sqlite_persists_sections_and_chunk_rows_in_deterministic_order(tmp_path: Path):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="sqlite-order-run",
        topic="Caching",
        max_sources=1,
        source_id="source-001",
        final_url="https://example.com/cache",
        title="Cache Notes",
        headings=["Cache Notes"],
        text=(
            "Caches reduce repeated work.\n"
            "Cache invalidation keeps data fresh across readers."
        ),
        source_type="secondary",
    )

    save_run_chunks_sqlite(generate_run_chunks(run_path), run_path)

    assert load_run_sections_from_sqlite(run_path) == [
        {
            "section_id": "source-001-section-000",
            "source_id": "source-001",
            "section_index": 0,
            "heading_path": ["Cache Notes"],
            "paragraphs": ["Caches reduce repeated work."],
        },
        {
            "section_id": "source-001-section-001",
            "source_id": "source-001",
            "section_index": 1,
            "heading_path": ["Cache Notes"],
            "paragraphs": ["Cache invalidation keeps data fresh across readers."],
        },
    ]
    assert load_run_chunks_from_sqlite(run_path) == [
        {
            "chunk_id": "source-001-section-000-paragraph-000-chunk-000",
            "section_id": "source-001-section-000",
            "paragraph_index": 0,
            "chunk_index": 0,
            "text": "Caches reduce repeated work.",
        },
        {
            "chunk_id": "source-001-section-001-paragraph-000-chunk-000",
            "section_id": "source-001-section-001",
            "paragraph_index": 0,
            "chunk_index": 0,
            "text": "Cache invalidation keeps data fresh across readers.",
        },
    ]


def test_cli_chunk_command_writes_json_and_sqlite(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="cli-sqlite-run",
        topic="Queues",
        max_sources=1,
        source_id="source-001",
        final_url="https://example.com/queues",
        title="Queue Notes",
        headings=["Queue Notes"],
        text="Queues smooth traffic spikes between producers and consumers.",
        source_type="secondary",
    )

    argv_before = sys.argv
    sys.argv = ["noesis", "chunk", "debug-run", "--debug-run-path", str(run_path)]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "chunk[0] length=61",
        str(run_path / "evidence" / "chunks.json"),
        str(run_path / "evidence" / "noesis.db"),
    ]


def _create_normalized_run(
    parent: Path,
    *,
    run_id: str,
    topic: str,
    max_sources: int,
    source_id: str,
    final_url: str,
    title: str,
    headings: list[str],
    text: str,
    source_type: str,
) -> Path:
    run_path = parent / run_id
    source_dir = run_path / "sources" / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    (run_path / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "topic": topic,
                "max_sources": max_sources,
                "source_count": 1,
                "sources": [],
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "metadata.json").write_text(
        json.dumps(
            {
                "source_id": source_id,
                "url": final_url,
                "final_url": final_url,
                "source_type": source_type,
                "title": title,
                "domain": "example.com",
                "published_date": None,
                "content_type": "text/html",
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "normalized.json").write_text(
        json.dumps(
            {
                "source_id": source_id,
                "final_url": final_url,
                "title": title,
                "headings": headings,
                "sections": [
                    _section_fixture(headings, index, paragraph)
                    for index, paragraph in enumerate(text.split("\n"))
                    if paragraph
                ],
                "links": [],
            }
        ),
        encoding="utf-8",
    )
    return run_path


def _load_cli_main():
    cli_module = importlib.import_module("noesis.cli")
    return cli_module.main


def _section_fixture(headings: list[str], index: int, paragraph: str) -> dict[str, object]:
    if not headings:
        return {"heading_path": [], "paragraphs": [paragraph]}
    if index == 0 or index >= len(headings):
        return {"heading_path": headings[:1], "paragraphs": [paragraph]}
    return {"heading_path": [headings[0], headings[index]], "paragraphs": [paragraph]}
