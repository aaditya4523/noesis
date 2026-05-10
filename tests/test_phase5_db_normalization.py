import importlib
import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from noesis.models import FetchResult, SourceCandidate
from noesis.normalization import normalize_run_html_sources_sqlite
from noesis.orchestrator import collect_topic_sources_to_db


class SingleSourceDiscoverer:
    def discover(self, topic: str) -> list[SourceCandidate]:
        return [
            SourceCandidate(
                url="https://example.com/article?utm_source=feed",
                title="Distributed Systems Article",
                domain="example.com",
                snippet="systems",
                source_type="secondary",
            )
        ]


class CountingFetcher:
    def fetch(self, candidate: SourceCandidate) -> FetchResult:
        return FetchResult(
            candidate=candidate,
            final_url="https://example.com/article",
            status_code=200,
            content_type="text/html",
            raw_content=ARTICLE_HTML.encode("utf-8"),
            published_date=None,
        )


ARTICLE_HTML = """
<html>
  <head>
    <title>Distributed Systems Article</title>
  </head>
  <body>
    <main>
      <h1>Distributed Systems Article</h1>
      <p>Distributed systems are collections of independent computers.</p>
      <h2>Replication</h2>
      <p>Replication improves availability and read throughput.</p>
      <a href="https://example.com/child-article">Child article</a>
    </main>
  </body>
</html>
"""


def test_normalize_run_html_sources_sqlite_rebuilds_sections_for_run(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )

    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM chunks")
        connection.execute("DELETE FROM sections")

    source_ids = normalize_run_html_sources_sqlite(db_path, run.run_id)

    assert len(source_ids) == 1
    assert source_ids[0].startswith("source-")

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT section_index, heading_path, paragraphs
            FROM sections
            ORDER BY section_index
            """
        ).fetchall()

    assert [
        {
            "section_index": row[0],
            "heading_path": json.loads(row[1]),
            "paragraphs": json.loads(row[2]),
        }
        for row in rows
    ] == [
        {
            "section_index": 0,
            "heading_path": ["Distributed Systems Article"],
            "paragraphs": ["Distributed systems are collections of independent computers."],
        },
        {
            "section_index": 1,
            "heading_path": ["Distributed Systems Article", "Replication"],
            "paragraphs": ["Replication improves availability and read throughput."],
        },
    ]


def test_cli_normalize_command_supports_run_id_with_shared_database(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.chdir(tmp_path)
    db_path = tmp_path / "data" / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )

    with sqlite3.connect(db_path) as connection:
        connection.execute("DELETE FROM chunks")
        connection.execute("DELETE FROM sections")

    argv_before = sys.argv
    sys.argv = ["noesis", "normalize", run.run_id]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    captured = capsys.readouterr()
    output_lines = captured.out.splitlines()
    assert len(output_lines) == 2
    assert output_lines[0].startswith("source-")
    assert output_lines[1] == str(Path("data") / "noesis.db")


def _load_cli_main():
    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    return cli_module.main
