import importlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from noesis.chunking import generate_run_chunks_sqlite
from noesis.models import FetchResult, SourceCandidate
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
    </main>
  </body>
</html>
"""


def test_generate_run_chunks_sqlite_reads_sections_from_shared_database(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )

    chunks = generate_run_chunks_sqlite(db_path, run.run_id)

    assert [chunk.text for chunk in chunks] == [
        "Distributed systems are collections of independent computers.",
        "Replication improves availability and read throughput.",
    ]
    assert chunks[0].run_id == run.run_id
    assert chunks[0].source_id.startswith("source-")
    assert chunks[0].source_url == "https://example.com/article"
    assert chunks[0].title == "Distributed Systems Article"
    assert chunks[0].heading_path == ["Distributed Systems Article"]
    assert chunks[1].heading_path == ["Distributed Systems Article", "Replication"]
    assert chunks[0].paragraph_index == 0
    assert chunks[1].paragraph_index == 1


def test_cli_chunk_command_supports_run_id_with_shared_database(
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

    argv_before = sys.argv
    sys.argv = ["noesis", "chunk", run.run_id]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "chunk[0] length=61",
        "chunk[1] length=54",
        str(Path("data") / "noesis.db"),
    ]

    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 2


def _load_cli_main():
    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    return cli_module.main
