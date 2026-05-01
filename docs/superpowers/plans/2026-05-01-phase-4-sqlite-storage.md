# Phase 4 SQLite Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add run-scoped SQLite persistence for runs, sources, and chunks while temporarily retaining `evidence/chunks.json` as a secondary artifact.

**Architecture:** Keep chunk generation unchanged and introduce SQLite persistence in `storage.py` as a parallel write path. The CLI will continue to generate chunks once, then persist them to both JSON and SQLite so downstream embedding and retrieval work can move to structured storage without breaking current inspection workflows.

**Tech Stack:** Python 3.14, sqlite3, dataclasses, JSON, pytest

---

## File Structure

- `src/noesis/storage.py`
  - add schema creation, SQLite persistence, and read helpers
- `src/noesis/cli.py`
  - extend `chunk` command to dual-write JSON and SQLite
- `tests/test_phase4_sqlite_storage.py`
  - add new storage-first tests for schema creation, persistence, ordered reads, and CLI behavior
- `docs/progress-checklist.md`
  - mark Phase 4 items when implementation is verified

### Task 1: Add failing storage tests

**Files:**
- Create: `tests/test_phase4_sqlite_storage.py`

- [ ] **Step 1: Write the failing test**

Add a test that creates a normalized run, generates chunks, persists them to SQLite, and expects:

```python
assert db_path == run_path / "evidence" / "noesis.db"
assert db_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: FAIL because SQLite persistence helpers do not exist yet

- [ ] **Step 3: Write minimal implementation**

Create a `save_run_chunks_sqlite()` helper in `src/noesis/storage.py` that creates the DB file path and initializes schema.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: the DB creation test passes or the suite fails later on missing row assertions

### Task 2: Persist run and source metadata

**Files:**
- Modify: `src/noesis/storage.py`
- Test: `tests/test_phase4_sqlite_storage.py`

- [ ] **Step 1: Write the failing test**

Add tests that read back persisted `runs` and `sources` rows and expect:

```python
assert runs == [{"run_id": "sqlite-run", "topic": "SQLite Storage", "max_sources": 1}]
assert sources == [{
    "run_id": "sqlite-run",
    "source_id": "source-001",
    "source_url": "https://example.com/sqlite",
    "title": "SQLite Notes",
    "source_type": "official",
}]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: FAIL because row persistence or read helpers are incomplete

- [ ] **Step 3: Write minimal implementation**

Read `manifest.json` and each source `metadata.json`, then insert or replace rows in `runs` and `sources`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: run/source persistence tests pass or the suite fails later on chunk assertions

### Task 3: Persist chunk rows and ordered reads

**Files:**
- Modify: `src/noesis/storage.py`
- Test: `tests/test_phase4_sqlite_storage.py`

- [ ] **Step 1: Write the failing test**

Add a test that persists multiple chunks and expects ordered read-back:

```python
assert [row["text"] for row in chunks] == [
    "Caches reduce repeated work.",
    "Cache invalidation keeps data fresh across readers.",
]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: FAIL because chunk rows are not inserted or not returned deterministically

- [ ] **Step 3: Write minimal implementation**

Insert `EvidenceChunk` rows into `chunks`, storing `heading_path` as JSON text and exposing deterministic run-scoped read helpers.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: ordered chunk persistence tests pass

### Task 4: Extend CLI dual-write behavior

**Files:**
- Modify: `src/noesis/cli.py`
- Test: `tests/test_phase4_sqlite_storage.py`

- [ ] **Step 1: Write the failing test**

Add a CLI test that invokes:

```python
sys.argv = ["noesis", "chunk", str(run_path)]
```

and expects output lines that include both:

```python
str(run_path / "evidence" / "chunks.json")
str(run_path / "evidence" / "noesis.db")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: FAIL because the CLI only writes JSON today

- [ ] **Step 3: Write minimal implementation**

Call the new SQLite persistence helper from the `chunk` command and print the DB path after the JSON path.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: PASS for dual-write CLI behavior

### Task 5: Final verification and checklist update

**Files:**
- Modify: `docs/progress-checklist.md`
- Test: `tests/test_phase3_chunking.py`
- Test: `tests/test_phase4_sqlite_storage.py`
- Test: `tests/test_phase2_normalization.py`
- Test: `tests/test_phase1_collection.py`

- [ ] **Step 1: Run focused Phase 4 tests**

Run: `python -m pytest tests/test_phase4_sqlite_storage.py -q`
Expected: PASS

- [ ] **Step 2: Run full suite**

Run: `python -m pytest -q`
Expected: PASS

- [ ] **Step 3: Mark Phase 4 checklist items**

Update `docs/progress-checklist.md` only after verification confirms the implementation matches the approved scope.
