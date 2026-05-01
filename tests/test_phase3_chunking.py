import json
import importlib
import sys
from pathlib import Path
from types import ModuleType

import pytest

from noesis.chunking import generate_run_chunks
from noesis.storage import save_run_chunks


def test_generate_run_chunks_builds_paragraph_chunks_with_metadata(tmp_path: Path):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="distributed-systems-run",
        source_id="source-001",
        final_url="https://example.com/distributed-systems-primer",
        title="Distributed Systems Primer",
        headings=["Distributed Systems Primer", "Replication", "Sharding"],
        text=(
            "Distributed systems are collections of independent computers.\n"
            "Replication improves availability and read throughput for critical data.\n"
            "Sharding partitions data to distribute write and storage load across nodes."
        ),
        source_type="official",
    )

    chunks = generate_run_chunks(run_path)

    assert [chunk.text for chunk in chunks] == [
        "Distributed systems are collections of independent computers.",
        "Replication improves availability and read throughput for critical data.",
        "Sharding partitions data to distribute write and storage load across nodes.",
    ]
    assert chunks[0].run_id == "distributed-systems-run"
    assert chunks[0].source_id == "source-001"
    assert chunks[0].source_url == "https://example.com/distributed-systems-primer"
    assert chunks[0].title == "Distributed Systems Primer"
    assert chunks[0].heading_path == ["Distributed Systems Primer"]
    assert chunks[1].heading_path == ["Distributed Systems Primer", "Replication"]
    assert chunks[2].heading_path == ["Distributed Systems Primer", "Sharding"]
    assert chunks[0].source_type == "official"
    assert chunks[0].paragraph_index == 0
    assert chunks[0].chunk_index == 0
    assert chunks[0].parent_paragraph_text == chunks[0].text


def test_generate_run_chunks_splits_oversized_paragraphs_with_langchain(tmp_path: Path):
    paragraph = "one two three four five six seven eight nine ten"
    run_path = _create_normalized_run(
        tmp_path,
        run_id="character-fallback-run",
        source_id="source-001",
        final_url="https://example.com/caching",
        title="Caching Basics",
        headings=["Caching Basics"],
        text=paragraph,
        source_type="secondary",
    )

    chunks = generate_run_chunks(run_path, max_paragraph_chars=15)

    assert len(chunks) > 1
    assert all(chunk.paragraph_index == 0 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.parent_paragraph_text == paragraph for chunk in chunks)
    assert all(len(chunk.text) <= 15 for chunk in chunks)


def test_generate_run_chunks_uses_character_fallback_for_dense_text(tmp_path: Path):
    dense_text = "antidisestablishmentarianism-" * 20
    run_path = _create_normalized_run(
        tmp_path,
        run_id="dense-character-run",
        source_id="source-001",
        final_url="https://example.com/dense-text",
        title="Dense Text",
        headings=["Dense Text"],
        text=dense_text,
        source_type="secondary",
    )

    chunks = generate_run_chunks(run_path, max_paragraph_chars=40)

    assert len(chunks) > 1
    assert "".join(chunk.text for chunk in chunks) == dense_text
    assert all(len(chunk.text) <= 40 for chunk in chunks)


def test_save_run_chunks_persists_chunk_records(tmp_path: Path):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="persisted-run",
        source_id="source-001",
        final_url="https://example.com/consistency",
        title="Consistency Notes",
        headings=["Consistency Notes"],
        text="Consistency determines how replicas observe writes.",
        source_type="official",
    )

    chunk_path = save_run_chunks(generate_run_chunks(run_path), run_path)

    assert chunk_path == run_path / "evidence" / "chunks.json"
    data = json.loads(chunk_path.read_text(encoding="utf-8"))
    assert data == [
        {
            "run_id": "persisted-run",
            "source_id": "source-001",
            "source_url": "https://example.com/consistency",
            "title": "Consistency Notes",
            "heading_path": ["Consistency Notes"],
            "source_type": "official",
            "paragraph_index": 0,
            "chunk_index": 0,
            "text": "Consistency determines how replicas observe writes.",
            "parent_paragraph_text": "Consistency determines how replicas observe writes.",
        }
    ]


def test_cli_chunk_command_prints_chunk_file_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="cli-run",
        source_id="source-001",
        final_url="https://example.com/queues",
        title="Queue Notes",
        headings=["Queue Notes"],
        text="Queues smooth traffic spikes between producers and consumers.",
        source_type="secondary",
    )

    argv_before = sys.argv
    sys.argv = ["noesis", "chunk", str(run_path)]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "chunk[0] length=61",
        str(run_path / "evidence" / "chunks.json"),
        str(run_path / "evidence" / "noesis.db"),
    ]


def test_cli_chunk_command_prints_chunk_lengths(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    run_path = _create_normalized_run(
        tmp_path,
        run_id="cli-length-run",
        source_id="source-001",
        final_url="https://example.com/cache",
        title="Cache Notes",
        headings=["Cache Notes"],
        text=(
            "Caches reduce repeated work.\n"
            "Cache invalidation keeps data fresh across readers."
        ),
        source_type="secondary",
    )

    argv_before = sys.argv
    sys.argv = ["noesis", "chunk", str(run_path)]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        "chunk[0] length=28",
        "chunk[1] length=51",
        str(run_path / "evidence" / "chunks.json"),
        str(run_path / "evidence" / "noesis.db"),
    ]


def test_collect_and_normalize_do_not_import_chunking_module(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    imported = {"chunking_loaded": False}
    original_import = __import__

    def tracking_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "noesis.chunking":
            imported["chunking_loaded"] = True
            return ModuleType("noesis.chunking")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", tracking_import)
    sys.modules.pop("noesis.cli", None)

    argv_before = sys.argv
    sys.argv = ["noesis", "normalize", str(tmp_path / "missing-run")]
    try:
        _load_cli_main()()
    finally:
        sys.argv = argv_before

    assert imported["chunking_loaded"] is False


def _create_normalized_run(
    parent: Path,
    *,
    run_id: str,
    source_id: str,
    final_url: str,
    title: str,
    headings: list[str],
    text: str,
    source_type: str,
) -> Path:
    run_path = parent / run_id
    source_dir = run_path / "sources" / source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    (run_path / "manifest.json").write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    (source_dir / "metadata.json").write_text(
        json.dumps(
            {
                "source_id": source_id,
                "url": final_url,
                "final_url": final_url,
                "source_type": source_type,
                "title": title,
                "content_type": "text/html",
            }
        ),
        encoding="utf-8",
    )
    (source_dir / "normalized.json").write_text(
        json.dumps(
            {
                "source_id": source_id,
                "final_url": final_url,
                "title": title,
                "headings": headings,
                "text": text,
                "sections": [
                    _section_fixture(headings, index, paragraph)
                    for index, paragraph in enumerate(text.split("\n"))
                    if paragraph
                ],
                "links": [],
            }
        ),
        encoding="utf-8",
    )
    return run_path


def _load_cli_main():
    cli_module = importlib.import_module("noesis.cli")
    return cli_module.main


def _section_fixture(headings: list[str], index: int, paragraph: str) -> dict[str, object]:
    if not headings:
        return {"heading_path": [], "paragraphs": [paragraph]}
    if index == 0 or index >= len(headings):
        return {"heading_path": headings[:1], "paragraphs": [paragraph]}
    return {"heading_path": [headings[0], headings[index]], "paragraphs": [paragraph]}
