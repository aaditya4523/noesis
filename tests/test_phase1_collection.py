from pathlib import Path

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
