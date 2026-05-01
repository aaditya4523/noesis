from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class SourceCandidate:
    url: str
    title: str
    domain: str
    snippet: str | None
    source_type: str


@dataclass(slots=True)
class FetchResult:
    candidate: SourceCandidate
    final_url: str
    status_code: int
    content_type: str | None
    raw_content: bytes
    published_date: str | None


@dataclass(slots=True)
class CollectedSource:
    source_id: str
    title: str
    url: str
    final_url: str
    domain: str
    source_type: str
    snippet: str | None
    status_code: int
    content_type: str | None
    raw_content: bytes
    published_date: str | None

    def to_metadata(self) -> dict[str, object]:
        metadata = asdict(self)
        metadata.pop("raw_content", None)
        return metadata


@dataclass(slots=True)
class AcquisitionRun:
    run_id: str
    topic: str
    max_sources: int
    sources: list[CollectedSource]

    def to_manifest(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "topic": self.topic,
            "max_sources": self.max_sources,
            "source_count": len(self.sources),
            "sources": [source.to_metadata() for source in self.sources],
        }


@dataclass(slots=True)
class NormalizedLink:
    url: str
    text: str


@dataclass(slots=True)
class NormalizedSection:
    heading_path: list[str]
    paragraphs: list[str]


@dataclass(slots=True)
class NormalizedHtmlDocument:
    source_id: str
    final_url: str
    title: str
    headings: list[str]
    sections: list[NormalizedSection]
    links: list[NormalizedLink]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["sections"] = [asdict(section) for section in self.sections]
        payload["links"] = [asdict(link) for link in self.links]
        return payload


@dataclass(slots=True)
class EvidenceChunk:
    run_id: str
    source_id: str
    source_url: str
    title: str
    heading_path: list[str]
    source_type: str
    paragraph_index: int
    chunk_index: int
    text: str
    parent_paragraph_text: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
