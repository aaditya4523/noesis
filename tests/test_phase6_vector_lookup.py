from datetime import UTC, datetime
import importlib
import json
from pathlib import Path
import sys

import noesis.vector_store
import pytest

from noesis.embeddings import embed_run_chunks, lookup_similar_chunks
from noesis.models import FetchResult, SourceCandidate
from noesis.orchestrator import collect_topic_sources_to_db
from noesis.storage import load_run_chunks_from_shared_sqlite
from noesis.vector_store import LanceVectorStore


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


class FakeEmbeddingProvider:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            if "Replication" in text:
                vectors.append([0.0, 1.0])
            else:
                vectors.append([1.0, 0.0])
        return vectors

    def embed_query(self, text: str) -> list[float]:
        if "replication" in text.lower():
            return [0.0, 1.0]
        return [1.0, 0.0]


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


def test_save_vectors_and_lookup_filters_by_run_id(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    run_a = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )
    run_b = collect_topic_sources_to_db(
        topic="distributed systems second run",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 3, tzinfo=UTC),
    )
    provider = FakeEmbeddingProvider()
    store = LanceVectorStore(tmp_path / "vectors")

    embed_run_chunks(
        db_path=db_path,
        vector_store=store,
        run_id=run_a.run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
    )
    embed_run_chunks(
        db_path=db_path,
        vector_store=store,
        run_id=run_b.run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
    )

    results = lookup_similar_chunks(
        db_path=db_path,
        vector_store=store,
        provider=provider,
        run_id=run_a.run_id,
        query_text="How does replication help?",
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        limit=5,
    )

    assert results
    assert all(result["run_id"] == run_a.run_id for result in results)
    assert results[0]["heading_path"] == ["Distributed Systems Article", "Replication"]


def test_vector_store_emits_backend_logs(tmp_path: Path):
    original_backend = noesis.vector_store.lancedb
    noesis.vector_store.lancedb = None
    messages: list[str] = []
    try:
        store = LanceVectorStore(tmp_path / "vectors", log=messages.append)

        store.upsert_embeddings(
            [
                {
                    "embedding_id": "embedding-1",
                    "chunk_id": "chunk-1",
                    "run_id": "run-a",
                    "source_id": "source-1",
                    "heading_path": ["Cache Notes"],
                    "title": "Cache Notes",
                    "vector": [1.0, 0.0],
                }
            ]
        )
        store.search([1.0, 0.0], run_id="run-a", limit=5)
    finally:
        noesis.vector_store.lancedb = original_backend

    assert messages == [
        "vector-store: using fallback json backend for upsert",
        "vector-store: using fallback json backend for search",
    ]


def test_vector_store_migrates_fallback_json_into_lancedb_when_available(
    tmp_path: Path,
    monkeypatch,
):
    fallback_root = tmp_path / "vectors"
    fallback_root.mkdir(parents=True, exist_ok=True)
    fallback_path = fallback_root / "chunk_embeddings.json"
    fallback_rows = [
        {
            "embedding_id": "embedding-1",
            "chunk_id": "chunk-1",
            "run_id": "run-a",
            "source_id": "source-1",
            "heading_path": ["Cache Notes"],
            "title": "Cache Notes",
            "vector": [1.0, 0.0],
        }
    ]
    fallback_path.write_text(json.dumps(fallback_rows), encoding="utf-8")

    class FakeTable:
        def __init__(self, rows: list[dict[str, object]]) -> None:
            self._rows = rows
            self._filtered_rows = rows

        def to_list(self) -> list[dict[str, object]]:
            return list(self._rows)

        def add(self, rows: list[dict[str, object]]) -> None:
            self._rows.extend(rows)

        def search(self, _query_vector: list[float]) -> "FakeTable":
            self._filtered_rows = list(self._rows)
            return self

        def where(self, expression: str) -> "FakeTable":
            run_id = expression.split("'")[1]
            self._filtered_rows = [row for row in self._rows if str(row["run_id"]) == run_id]
            return self

        def limit(self, limit: int) -> "FakeTable":
            self._filtered_rows = self._filtered_rows[:limit]
            return self

    class FakeDatabase:
        def __init__(self) -> None:
            self.tables: dict[str, FakeTable] = {}

        def open_table(self, name: str) -> FakeTable:
            if name not in self.tables:
                raise RuntimeError("missing table")
            return self.tables[name]

        def create_table(self, name: str, data: list[dict[str, object]]) -> FakeTable:
            table = FakeTable(list(data))
            self.tables[name] = table
            return table

    class FakeBackend:
        def __init__(self) -> None:
            self.database = FakeDatabase()

        def connect(self, _root: str) -> FakeDatabase:
            return self.database

    fake_backend = FakeBackend()
    monkeypatch.setattr(noesis.vector_store, "lancedb", fake_backend)

    messages: list[str] = []
    store = LanceVectorStore(fallback_root, log=messages.append)

    rows = store.search([1.0, 0.0], run_id="run-a", limit=5)

    assert rows == fallback_rows
    assert fake_backend.database.tables["chunk_embeddings"].to_list() == fallback_rows
    assert json.loads(fallback_path.read_text(encoding="utf-8")) == fallback_rows
    assert messages == [
        "vector-store: migrating fallback json rows into lancedb",
        "vector-store: imported 1 fallback rows into lancedb",
        "vector-store: using lancedb backend for search",
    ]


def test_vector_store_public_migration_returns_import_count(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    fallback_root = tmp_path / "vectors"
    fallback_root.mkdir(parents=True, exist_ok=True)
    fallback_path = fallback_root / "chunk_embeddings.json"
    fallback_rows = [
        {
            "embedding_id": "embedding-1",
            "chunk_id": "chunk-1",
            "run_id": "run-a",
            "source_id": "source-1",
            "heading_path": ["Cache Notes"],
            "title": "Cache Notes",
            "vector": [1.0, 0.0],
        }
    ]
    fallback_path.write_text(json.dumps(fallback_rows), encoding="utf-8")

    class FakeTable:
        def __init__(self, rows: list[dict[str, object]]) -> None:
            self._rows = rows

        def to_list(self) -> list[dict[str, object]]:
            return list(self._rows)

        def add(self, rows: list[dict[str, object]]) -> None:
            self._rows.extend(rows)

    class FakeDatabase:
        def __init__(self) -> None:
            self.tables: dict[str, FakeTable] = {}

        def open_table(self, name: str) -> FakeTable:
            if name not in self.tables:
                raise RuntimeError("missing table")
            return self.tables[name]

        def create_table(self, name: str, data: list[dict[str, object]]) -> FakeTable:
            table = FakeTable(list(data))
            self.tables[name] = table
            return table

    class FakeBackend:
        def __init__(self) -> None:
            self.database = FakeDatabase()

        def connect(self, _root: str) -> FakeDatabase:
            return self.database

    monkeypatch.setattr(noesis.vector_store, "lancedb", FakeBackend())
    store = LanceVectorStore(fallback_root)

    imported = store.migrate_fallback_vectors()

    assert imported == 1


def test_cli_migrate_vectors_runs_without_embedding_provider(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "lancedb").mkdir(parents=True, exist_ok=True)

    class FakeStore:
        def __init__(self, root: Path, log=None) -> None:
            assert root == Path("data") / "lancedb"
            self._log = log

        def migrate_fallback_vectors(self) -> int:
            if self._log is not None:
                self._log("vector-store: imported 19 fallback rows into lancedb")
            return 19

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "LanceVectorStore", FakeStore)

    argv_before = sys.argv
    sys.argv = ["noesis", "migrate-vectors"]
    try:
        cli_module.main()
    finally:
        sys.argv = argv_before

    assert capsys.readouterr().out.splitlines() == [
        "vector-store: imported 19 fallback rows into lancedb",
        "migrated 19 vectors",
        str(Path("data") / "lancedb"),
    ]


def test_cli_query_prints_readable_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    run, _db_path = _prepare_queryable_run(tmp_path)
    monkeypatch.chdir(tmp_path)

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "GeminiEmbeddingProvider", FakeEmbeddingProvider)

    argv_before = sys.argv
    sys.argv = ["noesis", "query", run.run_id, "How does replication help?"]
    try:
        cli_module.main()
    finally:
        sys.argv = argv_before

    assert capsys.readouterr().out.splitlines() == [
        "result[1]",
        "title: Distributed Systems Article",
        "headings: Distributed Systems Article > Replication",
        "source_url: https://example.com/article",
        "text: Replication improves availability and read throughput.",
        "",
        "result[2]",
        "title: Distributed Systems Article",
        "headings: Distributed Systems Article",
        "source_url: https://example.com/article",
        "text: Distributed systems are collections of independent computers.",
    ]


def test_cli_query_prints_json_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    run, db_path = _prepare_queryable_run(tmp_path)
    expected_top_row = load_run_chunks_from_shared_sqlite(db_path, run.run_id)[1]
    monkeypatch.chdir(tmp_path)

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "GeminiEmbeddingProvider", FakeEmbeddingProvider)

    argv_before = sys.argv
    sys.argv = ["noesis", "query", run.run_id, "How does replication help?", "--json", "--limit", "1"]
    try:
        cli_module.main()
    finally:
        sys.argv = argv_before

    payload = json.loads(capsys.readouterr().out)
    assert payload == [
        {
            "chunk_id": expected_top_row["chunk_id"],
            "run_id": run.run_id,
            "source_id": expected_top_row["source_id"],
            "source_url": "https://example.com/article",
            "title": "Distributed Systems Article",
            "heading_path": ["Distributed Systems Article", "Replication"],
            "source_type": "secondary",
            "paragraph_index": 0,
            "chunk_index": 0,
            "text": "Replication improves availability and read throughput.",
            "parent_paragraph_text": "Replication improves availability and read throughput.",
        }
    ]


def _prepare_queryable_run(tmp_path: Path):
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.chdir(tmp_path)
    db_path = Path("data") / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )
    store = LanceVectorStore(Path("data") / "lancedb")
    embed_run_chunks(
        db_path=db_path,
        vector_store=store,
        run_id=run.run_id,
        provider=FakeEmbeddingProvider(),
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
    )
    monkeypatch.undo()
    return run, tmp_path / db_path
