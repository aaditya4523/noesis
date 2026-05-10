from pathlib import Path
import importlib
import sys

import noesis.orchestrator
import pytest

from noesis.errors import DiscoveryError
from noesis.models import FetchResult, SourceCandidate
from noesis.orchestrator import collect_topic_sources
from noesis.ranking import prioritize_candidates
from noesis.storage import save_run_corpus


class StubDiscoverer:
    def discover(self, topic: str) -> list[SourceCandidate]:
        assert topic == "game theory"
        return [
            SourceCandidate(
                url="https://example.com/secondary-1",
                title="Secondary 1",
                domain="example.com",
                snippet="secondary",
                source_type="secondary",
            ),
            SourceCandidate(
                url="https://docs.python.org/3/",
                title="Official Docs",
                domain="docs.python.org",
                snippet="official",
                source_type="official",
            ),
            SourceCandidate(
                url="https://example.org/secondary-2",
                title="Secondary 2",
                domain="example.org",
                snippet="secondary",
                source_type="secondary",
            ),
        ]


class StubFetcher:
    def fetch(self, candidate: SourceCandidate) -> FetchResult:
        return FetchResult(
            candidate=candidate,
            final_url=candidate.url,
            status_code=200,
            content_type="text/html",
            raw_content=f"<html><title>{candidate.title}</title></html>".encode("utf-8"),
            published_date=None,
        )


class PartiallyFailingFetcher:
    def fetch(self, candidate: SourceCandidate) -> FetchResult:
        if candidate.title == "Official Docs":
            raise RuntimeError("403 forbidden")

        return FetchResult(
            candidate=candidate,
            final_url=candidate.url,
            status_code=200,
            content_type="text/html",
            raw_content=f"<html><title>{candidate.title}</title></html>".encode("utf-8"),
            published_date=None,
        )


def test_prioritize_candidates_prefers_official_sources():
    candidates = [
        SourceCandidate(
            url="https://example.com/guide",
            title="Guide",
            domain="example.com",
            snippet="secondary",
            source_type="secondary",
        ),
        SourceCandidate(
            url="https://docs.python.org/3/",
            title="Python Docs",
            domain="docs.python.org",
            snippet="official",
            source_type="official",
        ),
    ]

    prioritized = prioritize_candidates(candidates)

    assert [candidate.title for candidate in prioritized] == ["Python Docs", "Guide"]


def test_collect_topic_sources_applies_fetch_cap_and_priority(tmp_path: Path):
    run = collect_topic_sources(
        topic="game theory",
        discoverer=StubDiscoverer(),
        fetcher=StubFetcher(),
        output_root=tmp_path,
        max_sources=2,
    )

    assert run.topic == "game theory"
    assert len(run.sources) == 2
    assert [source.title for source in run.sources] == ["Official Docs", "Secondary 1"]


def test_collect_topic_sources_skips_fetch_failures_and_continues(tmp_path: Path):
    run = collect_topic_sources(
        topic="game theory",
        discoverer=StubDiscoverer(),
        fetcher=PartiallyFailingFetcher(),
        output_root=tmp_path,
        max_sources=3,
    )

    assert len(run.sources) == 2
    assert [source.title for source in run.sources] == ["Secondary 1", "Secondary 2"]


def test_collect_topic_sources_creates_unique_run_ids(tmp_path: Path):
    first_run = collect_topic_sources(
        topic="game theory",
        discoverer=StubDiscoverer(),
        fetcher=StubFetcher(),
        output_root=tmp_path,
        max_sources=1,
    )
    second_run = collect_topic_sources(
        topic="game theory",
        discoverer=StubDiscoverer(),
        fetcher=StubFetcher(),
        output_root=tmp_path,
        max_sources=1,
    )

    assert first_run.run_id != second_run.run_id
    assert first_run.run_id.startswith("game-theory-")
    assert second_run.run_id.startswith("game-theory-")


def test_save_run_corpus_writes_manifest_and_raw_files(tmp_path: Path):
    run = collect_topic_sources(
        topic="game theory",
        discoverer=StubDiscoverer(),
        fetcher=StubFetcher(),
        output_root=tmp_path,
        max_sources=2,
    )

    saved_path = save_run_corpus(run, tmp_path)

    assert (saved_path / "manifest.json").exists()
    assert (saved_path / "sources" / "source-001" / "raw.html").exists()
    assert (saved_path / "sources" / "source-001" / "metadata.json").exists()


def test_save_run_corpus_preserves_binary_source_extension(tmp_path: Path):
    candidate = SourceCandidate(
        url="https://example.edu/notes.pdf",
        title="Lecture Notes",
        domain="example.edu",
        snippet="official pdf",
        source_type="official",
    )
    run = collect_topic_sources(
        topic="game theory",
        discoverer=type("SingleCandidateDiscoverer", (), {"discover": lambda self, topic: [candidate]})(),
        fetcher=type(
            "PdfFetcher",
            (),
            {
                "fetch": lambda self, candidate: FetchResult(
                    candidate=candidate,
                    final_url=candidate.url,
                    status_code=200,
                    content_type="application/pdf",
                    raw_content=b"%PDF-1.7\nfake-pdf",
                    published_date=None,
                )
            },
        )(),
        output_root=tmp_path,
        max_sources=1,
    )

    saved_path = save_run_corpus(run, tmp_path)

    assert (saved_path / "sources" / "source-001" / "raw.pdf").exists()


def test_collect_cli_accepts_max_sources(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    captured: dict[str, object] = {}

    class FakeDiscoverer:
        def __init__(self, max_results: int) -> None:
            captured["max_results"] = max_results

    def fake_collect_topic_sources_to_db(*, topic, discoverer, fetcher, db_path, max_sources, on_fetch_error=None):
        captured["topic"] = topic
        captured["discoverer"] = discoverer
        captured["fetcher"] = fetcher
        captured["db_path"] = db_path
        captured["max_sources"] = max_sources
        return type("Run", (), {"run_id": "run-123"})()

    monkeypatch.setattr(noesis.orchestrator, "collect_topic_sources_to_db", fake_collect_topic_sources_to_db)

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")
    monkeypatch.setattr(cli_module, "DDGSDiscoverer", FakeDiscoverer)

    argv_before = sys.argv
    sys.argv = ["noesis", "collect", "game theory", "--max-sources", "3"]
    try:
        cli_module.main()
    finally:
        sys.argv = argv_before

    assert captured["topic"] == "game theory"
    assert captured["max_results"] == 3
    assert captured["max_sources"] == 3
    assert captured["db_path"] == Path("data") / "noesis.db"
    assert capsys.readouterr().out.splitlines() == ["run-123", str(Path("data") / "noesis.db")]


def test_collect_cli_prints_clean_discovery_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    def fake_collect_topic_sources_to_db(*, topic, discoverer, fetcher, db_path, max_sources, on_fetch_error=None):
        raise DiscoveryError("DDGS discovery failed: network unavailable")

    monkeypatch.setattr(noesis.orchestrator, "collect_topic_sources_to_db", fake_collect_topic_sources_to_db)

    sys.modules.pop("noesis.cli", None)
    cli_module = importlib.import_module("noesis.cli")

    argv_before = sys.argv
    sys.argv = ["noesis", "collect", "game theory"]
    try:
        with pytest.raises(SystemExit) as excinfo:
            cli_module.main()
    finally:
        sys.argv = argv_before

    assert excinfo.value.code == 1
    assert capsys.readouterr().err.splitlines() == ["error: DDGS discovery failed: network unavailable"]
