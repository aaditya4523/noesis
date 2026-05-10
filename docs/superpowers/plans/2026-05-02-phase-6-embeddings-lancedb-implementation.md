# Phase 6 Embeddings and LanceDB Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `embed <run_id>` with Gemini embeddings, SQLite embedding metadata, LanceDB vector storage, and run-scoped nearest-neighbor lookup.

**Architecture:** Keep SQLite as the source of truth for chunks and embedding metadata while LanceDB stores vectors for similarity search. Add a narrow embedding-provider interface with a Gemini-first implementation, then wire a separate embedding orchestration path and lookup API on top of the DB-first chunk pipeline.

**Tech Stack:** Python 3.14, SQLite, LanceDB, Gemini embeddings API, pytest

---

## File Structure

- Create: `src/noesis/embeddings.py`
  - embedding payload construction, provider interface, Gemini provider, orchestration helpers
- Create: `src/noesis/vector_store.py`
  - LanceDB connection, vector writes, run-scoped nearest-neighbor lookup
- Modify: `src/noesis/storage.py`
  - shared SQLite schema for embeddings and chunk links, run chunk reads for embedding, metadata persistence helpers
- Modify: `src/noesis/cli.py`
  - add `embed` command and any lookup/debug plumbing needed for this phase
- Modify: `src/noesis/models.py`
  - add any minimal dataclasses needed for embedding metadata or lookup results
- Modify: `pyproject.toml`
  - add LanceDB and Gemini client dependencies
- Create: `tests/test_phase6_embeddings.py`
  - embed command, missing-key behavior, payload-hash reuse, SQLite metadata writes
- Create: `tests/test_phase6_vector_lookup.py`
  - LanceDB vector writes and run-scoped nearest-neighbor lookup

### Task 1: Add Schema and Metadata Helpers

**Files:**
- Modify: `src/noesis/storage.py`
- Modify: `src/noesis/models.py`
- Test: `tests/test_phase6_embeddings.py`

- [ ] **Step 1: Write the failing test**

```python
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
    )
    second_id = save_embedding_record_sqlite(
        db_path,
        payload_hash="abc",
        embedding_model="gemini-embedding-001",
        embedding_dimensions=3072,
        provider="gemini",
        created_at="2026-05-02T00:00:01+00:00",
    )

    assert first_id == second_id
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_save_embedding_metadata_reuses_existing_payload_hash -q`
Expected: FAIL with missing SQLite helpers or schema columns

- [ ] **Step 3: Write minimal implementation**

```python
def save_embedding_record_sqlite(... ) -> str:
    ensure_shared_sqlite_schema(db_path)
    existing = find_embedding_record_sqlite(
        db_path,
        payload_hash=payload_hash,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
    )
    if existing:
        return str(existing["embedding_id"])
    embedding_id = f"embedding-{uuid4().hex[:12]}"
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_save_embedding_metadata_reuses_existing_payload_hash -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/noesis/storage.py src/noesis/models.py tests/test_phase6_embeddings.py
git commit -m "feat: add embedding metadata schema helpers"
```

### Task 2: Add Embedding Payload and Gemini Provider

**Files:**
- Create: `src/noesis/embeddings.py`
- Modify: `pyproject.toml`
- Test: `tests/test_phase6_embeddings.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_build_embedding_payload_includes_title_heading_and_content -q`
Expected: FAIL because the embedding module does not exist

- [ ] **Step 3: Write minimal implementation**

```python
def build_embedding_payload(chunk: EvidenceChunk) -> str:
    return (
        f"Title: {chunk.title}\n"
        f"Headings: {' > '.join(chunk.heading_path)}\n"
        f"Content: {chunk.text}"
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_build_embedding_payload_includes_title_heading_and_content -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/noesis/embeddings.py pyproject.toml tests/test_phase6_embeddings.py
git commit -m "feat: add gemini embedding payload and provider scaffolding"
```

### Task 3: Add LanceDB Vector Storage

**Files:**
- Create: `src/noesis/vector_store.py`
- Modify: `pyproject.toml`
- Test: `tests/test_phase6_vector_lookup.py`

- [ ] **Step 1: Write the failing test**

```python
def test_save_vectors_and_lookup_filters_by_run_id(tmp_path: Path):
    store = LanceVectorStore(tmp_path / "vectors")
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
            },
            {
                "embedding_id": "embedding-2",
                "chunk_id": "chunk-2",
                "run_id": "run-b",
                "source_id": "source-2",
                "heading_path": ["Queue Notes"],
                "title": "Queue Notes",
                "vector": [0.0, 1.0],
            },
        ]
    )

    results = store.search([1.0, 0.0], run_id="run-a", limit=5)

    assert [row["chunk_id"] for row in results] == ["chunk-1"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase6_vector_lookup.py::test_save_vectors_and_lookup_filters_by_run_id -q`
Expected: FAIL because the vector store module does not exist

- [ ] **Step 3: Write minimal implementation**

```python
class LanceVectorStore:
    def __init__(self, root: Path) -> None:
        self._db = lancedb.connect(str(root))
    ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase6_vector_lookup.py::test_save_vectors_and_lookup_filters_by_run_id -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/noesis/vector_store.py pyproject.toml tests/test_phase6_vector_lookup.py
git commit -m "feat: add lancedb vector storage"
```

### Task 4: Add `embed <run_id>` Command

**Files:**
- Modify: `src/noesis/cli.py`
- Modify: `src/noesis/embeddings.py`
- Modify: `src/noesis/storage.py`
- Modify: `tests/test_phase6_embeddings.py`

- [ ] **Step 1: Write the failing test**

```python
def test_cli_embed_command_fails_without_gemini_api_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(SystemExit):
        sys.argv = ["noesis", "embed", "run-123"]
        _load_cli_main()()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_cli_embed_command_fails_without_gemini_api_key -q`
Expected: FAIL because the embed command does not exist

- [ ] **Step 3: Write minimal implementation**

```python
embed_parser = subparsers.add_parser("embed", help="Generate embeddings for a run in shared SQLite.")
embed_parser.add_argument("run_id", help="Run ID stored in shared data/noesis.db.")
...
elif args.command == "embed":
    _embed_run(args.run_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase6_embeddings.py::test_cli_embed_command_fails_without_gemini_api_key -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/noesis/cli.py src/noesis/embeddings.py src/noesis/storage.py tests/test_phase6_embeddings.py
git commit -m "feat: add embed command"
```

### Task 5: Add Run-Scoped Lookup API

**Files:**
- Modify: `src/noesis/embeddings.py`
- Modify: `src/noesis/vector_store.py`
- Modify: `src/noesis/storage.py`
- Test: `tests/test_phase6_vector_lookup.py`

- [ ] **Step 1: Write the failing test**

```python
def test_lookup_run_embeddings_returns_chunk_metadata(tmp_path: Path):
    ...
    results = lookup_similar_chunks(
        query_text="How do I invalidate stale cache entries?",
        run_id="run-a",
        ...
    )

    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["title"] == "Cache Notes"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase6_vector_lookup.py::test_lookup_run_embeddings_returns_chunk_metadata -q`
Expected: FAIL because the lookup orchestration does not exist

- [ ] **Step 3: Write minimal implementation**

```python
def lookup_similar_chunks(... ) -> list[dict[str, object]]:
    query_vector = provider.embed_query(query_text)
    rows = vector_store.search(query_vector, run_id=run_id, limit=limit)
    return hydrate_lookup_rows_sqlite(db_path, rows)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase6_vector_lookup.py::test_lookup_run_embeddings_returns_chunk_metadata -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/noesis/embeddings.py src/noesis/vector_store.py src/noesis/storage.py tests/test_phase6_vector_lookup.py
git commit -m "feat: add run scoped vector lookup"
```

### Task 6: Run Phase Verification

**Files:**
- Test: `tests/test_phase6_embeddings.py`
- Test: `tests/test_phase6_vector_lookup.py`
- Test: `tests/test_phase5_db_chunking.py`
- Test: `tests/test_phase5_db_normalization.py`

- [ ] **Step 1: Run the new embedding suite**

Run: `python -m pytest tests/test_phase6_embeddings.py tests/test_phase6_vector_lookup.py -q`
Expected: PASS

- [ ] **Step 2: Run the DB-first regression suite**

Run: `python -m pytest tests/test_phase5_db_chunking.py tests/test_phase5_db_normalization.py tests/test_source_reuse_integration.py -q`
Expected: PASS

- [ ] **Step 3: Commit final verification-safe state**

```bash
git add src/noesis/embeddings.py src/noesis/vector_store.py src/noesis/storage.py src/noesis/cli.py pyproject.toml tests/test_phase6_embeddings.py tests/test_phase6_vector_lookup.py
git commit -m "feat: add gemini embeddings and lancedb lookup"
```
