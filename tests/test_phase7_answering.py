from datetime import UTC, datetime
import importlib
from pathlib import Path
import sys

import pytest

from noesis.errors import ProviderError
from noesis.embeddings import embed_run_chunks
from noesis.models import FetchResult, SourceCandidate
from noesis.orchestrator import collect_topic_sources_to_db
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


class FakeAnswerGenerator:
    def __init__(self, *, model: str = "gemini-2.0-flash", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key

    def generate_answer(self, *, question: str, evidence_rows: list[dict[str, object]]) -> str:
        assert question == "How does replication help?"
        assert len(evidence_rows) == 2
        assert evidence_rows[0]["heading_path"] == ["Distributed Systems Article", "Replication"]
        return "Replication improves availability and read throughput."


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


def test_cli_answer_prints_final_answer_and_sources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    run = _prepare_answerable_run(tmp_path)
    monkeypatch.chdir(tmp_path)

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "GeminiEmbeddingProvider", FakeEmbeddingProvider)
    monkeypatch.setattr(cli_module, "GeminiAnswerGenerator", FakeAnswerGenerator)

    argv_before = sys.argv
    sys.argv = ["noesis", "answer", run.run_id, "How does replication help?", "--limit", "2"]
    try:
        cli_module.main()
    finally:
        sys.argv = argv_before

    assert capsys.readouterr().out.splitlines() == [
        "Replication improves availability and read throughput.",
    ]


def test_cli_answer_prints_clean_provider_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    run = _prepare_answerable_run(tmp_path)
    monkeypatch.chdir(tmp_path)

    class FailingAnswerGenerator:
        def __init__(self, *, model: str = "gemini-3-flash-preview", api_key: str | None = None) -> None:
            self.model = model
            self.api_key = api_key

        def generate_answer(self, *, question: str, evidence_rows: list[dict[str, object]]) -> str:
            raise ProviderError("quota exhausted, please try again later")

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "GeminiEmbeddingProvider", FakeEmbeddingProvider)
    monkeypatch.setattr(cli_module, "GeminiAnswerGenerator", FailingAnswerGenerator)

    argv_before = sys.argv
    sys.argv = ["noesis", "answer", run.run_id, "How does replication help?", "--limit", "2"]
    try:
        with pytest.raises(SystemExit) as excinfo:
            cli_module.main()
    finally:
        sys.argv = argv_before

    assert excinfo.value.code == 1
    assert capsys.readouterr().err.splitlines() == ["error: quota exhausted, please try again later"]


def _prepare_answerable_run(tmp_path: Path):
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
    return run
