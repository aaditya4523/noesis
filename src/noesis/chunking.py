from __future__ import annotations

import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from noesis.models import EvidenceChunk


def generate_run_chunks(run_path: Path, max_paragraph_chars: int = 480) -> list[EvidenceChunk]:
    manifest = json.loads((run_path / "manifest.json").read_text(encoding="utf-8"))
    run_id = str(manifest["run_id"])
    source_root = run_path / "sources"
    chunks: list[EvidenceChunk] = []

    if not source_root.exists():
        return chunks

    for source_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        normalized_path = source_dir / "normalized.json"
        metadata_path = source_dir / "metadata.json"
        if not normalized_path.exists() or not metadata_path.exists():
            continue

        normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        chunks.extend(
            generate_document_chunks(
                run_id=run_id,
                normalized=normalized,
                source_type=str(metadata.get("source_type") or "secondary"),
                fallback_source_id=source_dir.name,
                max_paragraph_chars=max_paragraph_chars,
            )
        )

    return chunks


def generate_document_chunks(
    *,
    run_id: str,
    normalized: dict[str, object],
    source_type: str,
    fallback_source_id: str = "source",
    max_paragraph_chars: int = 480,
) -> list[EvidenceChunk]:
    source_id = str(normalized.get("source_id") or fallback_source_id)
    source_url = str(normalized.get("final_url") or normalized.get("url") or "")
    title = str(normalized.get("title") or "")
    chunks: list[EvidenceChunk] = []
    paragraph_index = 0
    for heading_path, paragraph_text in _iter_section_paragraphs(normalized):
        paragraph_chunks = _split_oversized_paragraph(paragraph_text, max_paragraph_chars)
        for chunk_index, chunk_text in enumerate(paragraph_chunks):
            chunks.append(
                EvidenceChunk(
                    run_id=run_id,
                    source_id=source_id,
                    source_url=source_url,
                    title=title,
                    heading_path=heading_path,
                    source_type=source_type,
                    paragraph_index=paragraph_index,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    parent_paragraph_text=paragraph_text,
                )
            )
        paragraph_index += 1
    return chunks


def _extract_paragraphs(text: str) -> list[str]:
    return [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]


def _iter_section_paragraphs(normalized: dict[str, object]) -> list[tuple[list[str], str]]:
    sections = normalized.get("sections")
    if isinstance(sections, list) and sections:
        section_paragraphs: list[tuple[list[str], str]] = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            heading_path = [str(value) for value in section.get("heading_path", [])]
            paragraphs = section.get("paragraphs", [])
            if not isinstance(paragraphs, list):
                continue
            for paragraph in paragraphs:
                paragraph_text = str(paragraph).strip()
                if paragraph_text:
                    section_paragraphs.append((heading_path, paragraph_text))
        if section_paragraphs:
            return section_paragraphs

    headings = normalized.get("headings")
    fallback_heading_path = [str(headings[0])] if isinstance(headings, list) and headings else []
    if not fallback_heading_path:
        title = str(normalized.get("title") or "")
        fallback_heading_path = [title] if title else []
    return [
        (fallback_heading_path, paragraph)
        for paragraph in _extract_paragraphs(str(normalized.get("text", "")))
    ]


def _split_oversized_paragraph(paragraph_text: str, max_paragraph_chars: int) -> list[str]:
    if len(paragraph_text) <= max_paragraph_chars:
        return [paragraph_text]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_paragraph_chars,
        chunk_overlap=0,
        separators=["\n\n", "\n", ". ", " ", ""],
        keep_separator=False,
        strip_whitespace=True,
        length_function=len,
    )
    return splitter.split_text(paragraph_text)
