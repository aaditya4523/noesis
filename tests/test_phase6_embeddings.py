import importlib
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from noesis.errors import ProviderError
from noesis.embeddings import (
    MissingGeminiApiKeyError,
    build_embedding_payload,
    embed_run_chunks,
)
from noesis.models import EvidenceChunk, FetchResult, SourceCandidate
from noesis.orchestrator import collect_topic_sources_to_db
from noesis.storage import (
    ensure_shared_sqlite_schema,
    load_chunk_embedding_links_sqlite,
    load_embedding_records_sqlite,
    load_run_chunks_from_shared_sqlite,
    save_embedding_record_sqlite,
)
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
    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[float(index + 1), float(len(text))] for index, text in enumerate(texts)]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, float(len(text))]


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


def test_save_embedding_metadata_reuses_existing_payload_hash(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    ensure_shared_sqlite_schema(db_path)

    first_id = save_embedding_record_sqlite(
        db_path,
        payload_hash="abc",
        embedding_model="gemini-embedding-001",
        embedding_dimensions=3072,
        provider="gemini",
        created_at="2026-05-02T00:00:00+00:00",
        status="completed",
    )
    second_id = save_embedding_record_sqlite(
        db_path,
        payload_hash="abc",
        embedding_model="gemini-embedding-001",
        embedding_dimensions=3072,
        provider="gemini",
        created_at="2026-05-02T00:00:01+00:00",
        status="completed",
    )

    assert first_id == second_id
    assert len(load_embedding_records_sqlite(db_path)) == 1


def test_build_embedding_payload_includes_title_heading_and_content():
    chunk = EvidenceChunk(
        run_id="run-1",
        source_id="source-1",
        source_url="https://example.com",
        title="Cache Notes",
        heading_path=["Cache Notes", "Invalidation"],
        source_type="secondary",
        paragraph_index=0,
        chunk_index=0,
        text="Invalidate stale entries.",
        parent_paragraph_text="Invalidate stale entries.",
    )

    payload = build_embedding_payload(chunk)

    assert payload == (
        "Title: Cache Notes\n"
        "Headings: Cache Notes > Invalidation\n"
        "Content: Invalidate stale entries."
    )


def test_embed_run_chunks_reuses_existing_embedding_for_same_payload(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )
    vector_store = LanceVectorStore(tmp_path / "vectors")
    provider = FakeEmbeddingProvider()

    first_embedding_ids = embed_run_chunks(
        db_path=db_path,
        vector_store=vector_store,
        run_id=run.run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
    )
    second_embedding_ids = embed_run_chunks(
        db_path=db_path,
        vector_store=vector_store,
        run_id=run.run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
    )

    assert provider.calls and len(provider.calls) == 1
    assert first_embedding_ids == second_embedding_ids
    assert len(load_embedding_records_sqlite(db_path)) == 2
    assert len(load_chunk_embedding_links_sqlite(db_path, run.run_id)) == 2


def test_embed_run_chunks_emits_progress_logs(tmp_path: Path):
    db_path = tmp_path / "noesis.db"
    run = collect_topic_sources_to_db(
        topic="distributed systems",
        discoverer=SingleSourceDiscoverer(),
        fetcher=CountingFetcher(),
        db_path=db_path,
        max_sources=1,
        now=datetime(2026, 5, 2, tzinfo=UTC),
    )
    vector_store = LanceVectorStore(tmp_path / "vectors")
    provider = FakeEmbeddingProvider()
    messages: list[str] = []

    embed_run_chunks(
        db_path=db_path,
        vector_store=vector_store,
        run_id=run.run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=2,
        provider_name="gemini",
        log=messages.append,
    )

    assert messages == [
        f"embed: loading chunks for run {run.run_id}",
        "embed: loaded 2 chunks",
        "embed: checking for reusable embeddings",
        "embed: reusing 0 embeddings, generating 2 new embeddings",
        "embed: requesting embeddings from provider",
        "embed: writing 2 vectors to vector store",
        "embed: completed",
    ]


def test_cli_embed_command_fails_without_gemini_api_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "")

    argv_before = sys.argv
    sys.argv = ["noesis", "embed", "run-123"]
    try:
        with pytest.raises(SystemExit) as excinfo:
            _load_cli_main()()
    finally:
        sys.argv = argv_before

    assert excinfo.value.code == 1
    assert capsys.readouterr().err.splitlines() == ["error: GEMINI_API_KEY is required for the embed command"]


def test_cli_query_prints_clean_missing_embeddings_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.chdir(tmp_path)
    ensure_shared_sqlite_schema(Path("data") / "noesis.db")

    argv_before = sys.argv
    sys.argv = ["noesis", "query", "run-123", "What is caching?"]
    try:
        with pytest.raises(SystemExit) as excinfo:
            _load_cli_main()()
    finally:
        sys.argv = argv_before

    assert excinfo.value.code == 1
    assert capsys.readouterr().err.splitlines() == ["error: no embeddings found for run run-123"]


def _load_cli_main():
    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    return cli_module.main
