from __future__ import annotations

import json
from pathlib import Path

from noesis.models import AcquisitionRun, CollectedSource


def save_run_corpus(run: AcquisitionRun, output_root: Path) -> Path:
    run_path = output_root / run.run_id
    sources_path = run_path / "sources"
    sources_path.mkdir(parents=True, exist_ok=True)

    for source in run.sources:
        _save_source(source, sources_path / source.source_id)

    manifest_path = run_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(run.to_manifest(), indent=2),
        encoding="utf-8",
    )
    return run_path


def _save_source(source: CollectedSource, source_path: Path) -> None:
    source_path.mkdir(parents=True, exist_ok=True)
    extension = _extension_for_content_type(source.content_type)
    (source_path / f"raw{extension}").write_bytes(source.raw_content)
    (source_path / "metadata.json").write_text(
        json.dumps(source.to_metadata(), indent=2),
        encoding="utf-8",
    )


def _extension_for_content_type(content_type: str | None) -> str:
    if not content_type:
        return ".bin"

    normalized = content_type.lower()
    if "html" in normalized:
        return ".html"
    if "pdf" in normalized:
        return ".pdf"
    if "json" in normalized:
        return ".json"
    if "xml" in normalized:
        return ".xml"
    if "plain" in normalized or "text/" in normalized:
        return ".txt"
    return ".bin"
