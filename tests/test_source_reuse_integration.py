import sqlite3
from datetime import UTC, datetime
from pathlib import Path

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
    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, candidate: SourceCandidate) -> FetchResult:
        self.calls += 1
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


def test_collect_topic_sources_to_db_reuses_recent_source(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    fetcher = CountingFetcher()

    first_run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=fetcher,
        db_path=db_path,
        max_sources=1,
        ttl_days=365,
        now=datetime(2026, 5, 1, tzinfo=UTC),
    )
    second_run = collect_topic_sources_to_db(
        topic="distributed systems interview prep",
        discoverer=SingleSourceDiscoverer(),
        fetcher=fetcher,
        db_path=db_path,
        max_sources=1,
        ttl_days=365,
        now=datetime(2026, 8, 1, tzinfo=UTC),
    )

    assert fetcher.calls == 1
    assert first_run.run_id != second_run.run_id

    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM run_sources").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM sections").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 2
        assert connection.execute("SELECT canonical_url FROM sources").fetchone()[0] == "https://example.com/article"


def test_collect_topic_sources_to_db_refreshes_stale_source(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    fetcher = CountingFetcher()

    collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=fetcher,
        db_path=db_path,
        max_sources=1,
        ttl_days=365,
        now=datetime(2024, 1, 1, tzinfo=UTC),
    )
    collect_topic_sources_to_db(
        topic="distributed systems interview prep",
        discoverer=SingleSourceDiscoverer(),
        fetcher=fetcher,
        db_path=db_path,
        max_sources=1,
        ttl_days=365,
        now=datetime(2026, 5, 1, tzinfo=UTC),
    )

    assert fetcher.calls == 2

    with sqlite3.connect(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM run_sources").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM sections").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0] == 2
