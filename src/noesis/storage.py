from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlparse
from datetime import UTC, datetime
from uuid import uuid4

from noesis.models import AcquisitionRun, CollectedSource, EvidenceChunk, NormalizedHtmlDocument


def save_run_corpus(run: AcquisitionRun, output_root: Path) -> Path:
    run_path = output_root / run.run_id
    sources_path = run_path / "sources"
    sources_path.mkdir(parents=True, exist_ok=True)

    for source in run.sources:
        _save_source(source, sources_path / source.source_id)

    manifest_path = run_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(run.to_manifest(), indent=2),
        encoding="utf-8",
    )
    return run_path


def _save_source(source: CollectedSource, source_path: Path) -> None:
    source_path.mkdir(parents=True, exist_ok=True)
    extension = _extension_for_content_type(source.content_type)
    (source_path / f"raw{extension}").write_bytes(source.raw_content)
    (source_path / "metadata.json").write_text(
        json.dumps(source.to_metadata(), indent=2),
        encoding="utf-8",
    )


def _extension_for_content_type(content_type: str | None) -> str:
    if not content_type:
        return ".bin"

    normalized = content_type.lower()
    if "html" in normalized:
        return ".html"
    if "pdf" in normalized:
        return ".pdf"
    if "json" in normalized:
        return ".json"
    if "xml" in normalized:
        return ".xml"
    if "plain" in normalized or "text/" in normalized:
        return ".txt"
    return ".bin"


def save_run_chunks(chunks: list[EvidenceChunk], run_path: Path) -> Path:
    evidence_path = run_path / "evidence"
    evidence_path.mkdir(parents=True, exist_ok=True)
    chunk_path = evidence_path / "chunks.json"
    chunk_path.write_text(
        json.dumps([chunk.to_dict() for chunk in chunks], indent=2),
        encoding="utf-8",
    )
    return chunk_path


def save_run_chunks_sqlite(chunks: list[EvidenceChunk], run_path: Path) -> Path:
    db_path = run_path / "evidence" / "noesis.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((run_path / "manifest.json").read_text(encoding="utf-8"))
    source_rows = _load_source_rows(run_path)
    section_rows, paragraph_lookup = _load_section_rows(run_path)
    created_at = _utc_now()

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        _ensure_sqlite_schema(connection)
        connection.execute(
            """
            INSERT INTO runs (run_id, topic, created_at)
            VALUES (?, ?, ?)
            """,
            (
                str(manifest.get("run_id") or ""),
                str(manifest.get("topic") or ""),
                created_at,
            ),
        )
        connection.executemany(
            """
            INSERT INTO sources (
                source_id,
                run_id,
                url,
                title,
                final_url,
                domain,
                source_type,
                content_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            source_rows,
        )
        connection.executemany(
            """
            INSERT INTO sections (
                section_id,
                source_id,
                heading_path,
                paragraphs,
                section_index
            ) VALUES (?, ?, ?, ?, ?)
            """,
            section_rows,
        )
        connection.executemany(
            """
            INSERT INTO chunks (
                chunk_id,
                section_id,
                paragraph_index,
                chunk_index,
                text
            ) VALUES (?, ?, ?, ?, ?)
            """,
            _build_chunk_rows(chunks, paragraph_lookup),
        )

    return db_path


def load_run_record_from_sqlite(run_path: Path) -> dict[str, object] | None:
    db_path = run_path / "evidence" / "noesis.db"
    if not db_path.exists():
        return None

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT run_id, topic FROM runs LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def load_run_sources_from_sqlite(run_path: Path) -> list[dict[str, object]]:
    db_path = run_path / "evidence" / "noesis.db"
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                source_id,
                run_id,
                url,
                final_url,
                title,
                domain,
                source_type,
                content_type
            FROM sources
            ORDER BY source_id
            """
        ).fetchall()
        return [dict(row) for row in rows]


def load_run_sections_from_sqlite(run_path: Path) -> list[dict[str, object]]:
    db_path = run_path / "evidence" / "noesis.db"
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                section_id,
                source_id,
                section_index,
                heading_path,
                paragraphs
            FROM sections
            ORDER BY source_id, section_index
            """
        ).fetchall()
        return [
            {
                **dict(row),
                "heading_path": json.loads(str(row["heading_path"])),
                "paragraphs": json.loads(str(row["paragraphs"])),
            }
            for row in rows
        ]


def load_run_chunks_from_sqlite(run_path: Path) -> list[dict[str, object]]:
    db_path = run_path / "evidence" / "noesis.db"
    if not db_path.exists():
        return []

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                chunk_id,
                section_id,
                paragraph_index,
                chunk_index,
                text
            FROM chunks
            ORDER BY section_id, paragraph_index, chunk_index
            """
        ).fetchall()
        return [dict(row) for row in rows]


def _ensure_sqlite_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP TABLE IF EXISTS chunks;
        DROP TABLE IF EXISTS sections;
        DROP TABLE IF EXISTS sources;
        DROP TABLE IF EXISTS runs;

        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE sources (
            source_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            final_url TEXT NOT NULL,
            domain TEXT NOT NULL,
            source_type TEXT NOT NULL,
            content_type TEXT,
            PRIMARY KEY (source_id),
            FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
        );

        CREATE TABLE sections (
            section_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            heading_path TEXT NOT NULL,
            paragraphs TEXT NOT NULL,
            section_index INTEGER NOT NULL,
            FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE,
            UNIQUE (source_id, section_index)
        );

        CREATE TABLE chunks (
            chunk_id TEXT PRIMARY KEY,
            section_id TEXT NOT NULL,
            paragraph_index INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
            UNIQUE (section_id, paragraph_index, chunk_index)
        );
        """
    )


def _load_source_rows(run_path: Path) -> list[tuple[object, ...]]:
    manifest = json.loads((run_path / "manifest.json").read_text(encoding="utf-8"))
    run_id = str(manifest.get("run_id") or "")
    source_root = run_path / "sources"
    if not source_root.exists():
        return []

    rows: list[tuple[object, ...]] = []
    for source_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        metadata_path = source_dir / "metadata.json"
        if not metadata_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_url = str(metadata.get("url") or metadata.get("final_url") or "")
        final_url = str(metadata.get("final_url") or metadata.get("url") or "")
        domain = str(metadata.get("domain") or urlparse(final_url).netloc)
        rows.append(
            (
                str(metadata.get("source_id") or source_dir.name),
                run_id,
                source_url,
                str(metadata.get("title") or ""),
                final_url,
                domain,
                str(metadata.get("source_type") or "secondary"),
                metadata.get("content_type"),
            )
        )
    return rows


def _load_section_rows(run_path: Path) -> tuple[list[tuple[object, ...]], dict[tuple[str, int], tuple[str, int]]]:
    source_root = run_path / "sources"
    if not source_root.exists():
        return [], {}

    rows: list[tuple[object, ...]] = []
    paragraph_lookup: dict[tuple[str, int], tuple[str, int]] = {}
    for source_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        normalized_path = source_dir / "normalized.json"
        if not normalized_path.exists():
            continue
        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        source_id = str(normalized.get("source_id") or source_dir.name)
        global_paragraph_index = 0
        for section_index, section in enumerate(normalized.get("sections", [])):
            if not isinstance(section, dict):
                continue
            section_id = f"{source_id}-section-{section_index:03d}"
            heading_path = [str(value) for value in section.get("heading_path", [])]
            paragraphs = [
                str(paragraph).strip()
                for paragraph in section.get("paragraphs", [])
                if str(paragraph).strip()
            ]
            rows.append(
                (
                    section_id,
                    source_id,
                    json.dumps(heading_path),
                    json.dumps(paragraphs),
                    section_index,
                )
            )
            for paragraph_index, _paragraph in enumerate(paragraphs):
                paragraph_lookup[(source_id, global_paragraph_index)] = (section_id, paragraph_index)
                global_paragraph_index += 1
    return rows, paragraph_lookup


def _build_chunk_rows(
    chunks: list[EvidenceChunk],
    paragraph_lookup: dict[tuple[str, int], tuple[str, int]],
) -> list[tuple[object, ...]]:
    rows: list[tuple[object, ...]] = []
    for chunk in chunks:
        lookup_key = (chunk.source_id, chunk.paragraph_index)
        if lookup_key not in paragraph_lookup:
            raise ValueError(f"Missing section mapping for {lookup_key}")
        section_id, paragraph_index = paragraph_lookup[lookup_key]
        rows.append(
            (
                f"{section_id}-paragraph-{paragraph_index:03d}-chunk-{chunk.chunk_index:03d}",
                section_id,
                paragraph_index,
                chunk.chunk_index,
                chunk.text,
            )
        )
    return rows


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def ensure_shared_sqlite_schema(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                canonical_url TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL,
                final_url TEXT NOT NULL,
                title TEXT NOT NULL,
                domain TEXT NOT NULL,
                source_type TEXT NOT NULL,
                content_type TEXT,
                last_fetched_at TEXT NOT NULL,
                refresh_ttl_days INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS run_sources (
                run_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                source_order INTEGER NOT NULL,
                PRIMARY KEY (run_id, source_id),
                FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE,
                FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sections (
                section_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                section_index INTEGER NOT NULL,
                heading_path TEXT NOT NULL,
                paragraphs TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE,
                UNIQUE (source_id, section_index)
            );

            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                section_id TEXT NOT NULL,
                paragraph_index INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (section_id) REFERENCES sections(section_id) ON DELETE CASCADE,
                UNIQUE (section_id, paragraph_index, chunk_index)
            );
            """
        )
    return db_path


def save_run_record_sqlite(db_path: Path, *, run_id: str, topic: str, created_at: str) -> None:
    ensure_shared_sqlite_schema(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO runs (run_id, topic, created_at)
            VALUES (?, ?, ?)
            """,
            (run_id, topic, created_at),
        )


def find_reusable_source_sqlite(
    db_path: Path,
    *,
    canonical_url: str,
    now: str,
) -> dict[str, object] | None:
    if not db_path.exists():
        return None

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT
                source_id,
                canonical_url,
                url,
                final_url,
                title,
                domain,
                source_type,
                content_type,
                last_fetched_at,
                refresh_ttl_days
            FROM sources
            WHERE canonical_url = ?
            """,
            (canonical_url,),
        ).fetchone()
        if not row:
            return None
        return dict(row)


def save_source_graph_sqlite(
    db_path: Path,
    *,
    run_id: str,
    source_order: int,
    source_id: str,
    canonical_url: str,
    url: str,
    final_url: str,
    title: str,
    domain: str,
    source_type: str,
    content_type: str | None,
    fetched_at: str,
    refresh_ttl_days: int,
    normalized: NormalizedHtmlDocument,
    chunks: list[EvidenceChunk],
) -> str:
    ensure_shared_sqlite_schema(db_path)
    source_row = find_reusable_source_sqlite(db_path, canonical_url=canonical_url, now=fetched_at)
    source_id = str(source_row["source_id"]) if source_row else source_id
    section_rows = _build_section_rows_from_document(source_id, normalized)
    chunk_rows = _build_chunk_rows_from_section_lookup(chunks, section_rows)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT INTO sources (
                source_id,
                canonical_url,
                url,
                final_url,
                title,
                domain,
                source_type,
                content_type,
                last_fetched_at,
                refresh_ttl_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                canonical_url=excluded.canonical_url,
                url=excluded.url,
                final_url=excluded.final_url,
                title=excluded.title,
                domain=excluded.domain,
                source_type=excluded.source_type,
                content_type=excluded.content_type,
                last_fetched_at=excluded.last_fetched_at,
                refresh_ttl_days=excluded.refresh_ttl_days
            """,
            (
                source_id,
                canonical_url,
                url,
                final_url,
                title,
                domain,
                source_type,
                content_type,
                fetched_at,
                refresh_ttl_days,
            ),
        )
        connection.execute("DELETE FROM chunks WHERE section_id IN (SELECT section_id FROM sections WHERE source_id = ?)", (source_id,))
        connection.execute("DELETE FROM sections WHERE source_id = ?", (source_id,))
        connection.executemany(
            """
            INSERT INTO sections (section_id, source_id, section_index, heading_path, paragraphs)
            VALUES (?, ?, ?, ?, ?)
            """,
            section_rows,
        )
        connection.executemany(
            """
            INSERT INTO chunks (chunk_id, section_id, paragraph_index, chunk_index, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            chunk_rows,
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO run_sources (run_id, source_id, source_order)
            VALUES (?, ?, ?)
            """,
            (run_id, source_id, source_order),
        )
    return source_id


def link_run_to_existing_source_sqlite(db_path: Path, *, run_id: str, source_id: str, source_order: int) -> None:
    ensure_shared_sqlite_schema(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            """
            INSERT OR REPLACE INTO run_sources (run_id, source_id, source_order)
            VALUES (?, ?, ?)
            """,
            (run_id, source_id, source_order),
        )


def _build_section_rows_from_document(
    source_id: str,
    normalized: NormalizedHtmlDocument,
) -> list[tuple[str, str, int, str, str]]:
    rows: list[tuple[str, str, int, str, str]] = []
    for section_index, section in enumerate(normalized.sections):
        section_id = f"{source_id}-section-{section_index:03d}"
        rows.append(
            (
                section_id,
                source_id,
                section_index,
                json.dumps(section.heading_path),
                json.dumps(section.paragraphs),
            )
        )
    return rows


def _build_chunk_rows_from_section_lookup(
    chunks: list[EvidenceChunk],
    section_rows: list[tuple[str, str, int, str, str]],
) -> list[tuple[str, str, int, int, str]]:
    paragraph_lookup: dict[tuple[str, int], tuple[str, int]] = {}
    for section_id, source_id, _section_index, _heading_path, paragraphs in section_rows:
        for paragraph_index, _paragraph in enumerate(json.loads(paragraphs)):
            paragraph_lookup[(source_id, len([key for key in paragraph_lookup if key[0] == source_id]))] = (
                section_id,
                paragraph_index,
            )

    rows: list[tuple[str, str, int, int, str]] = []
    for chunk in chunks:
        section_id, paragraph_index = paragraph_lookup[(chunk.source_id, chunk.paragraph_index)]
        rows.append(
            (
                f"{section_id}-paragraph-{paragraph_index:03d}-chunk-{chunk.chunk_index:03d}",
                section_id,
                paragraph_index,
                chunk.chunk_index,
                chunk.text,
            )
        )
    return rows
