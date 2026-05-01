# Phase 3 Evidence Chunking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first post-normalization evidence pipeline that reads normalized run data, creates source-faithful chunks, persists them locally, and exposes a CLI entry point.

**Architecture:** Add a dedicated chunking module that consumes `normalized.json` plus source metadata and emits structured chunk records. Persist chunk records alongside the run in JSON for this first slice, while keeping the model and storage boundaries clean so SQLite/LanceDB can be added next without reworking the chunking rules.

**Tech Stack:** Python 3.14, dataclasses, JSON persistence, pytest

---

## File Structure

- `src/noesis/models.py`
  - add chunk dataclasses and serialization helpers
- `src/noesis/chunking.py`
  - new Phase 3 module for run-level chunk generation
- `src/noesis/storage.py`
  - add chunk persistence helpers
- `src/noesis/cli.py`
  - add `chunk` subcommand
- `tests/test_phase3_chunking.py`
  - new tests for chunk boundaries, oversized paragraph fallback, persistence, and CLI-facing behavior

### Task 1: Define chunk records

**Files:**
- Modify: `src/noesis/models.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Write the failing test**

Add a test that expects persisted chunk JSON to expose fields:
`run_id`, `source_id`, `source_url`, `title`, `heading_path`, `source_type`, `paragraph_index`, `chunk_index`, `text`, and `parent_paragraph_text`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: FAIL because chunking module/models do not exist yet

- [ ] **Step 3: Write minimal implementation**

Add chunk dataclasses with `to_dict()` support in `src/noesis/models.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: the new test moves forward or fails later on missing chunk generation

### Task 2: Generate chunks from normalized runs

**Files:**
- Create: `src/noesis/chunking.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Write the failing test**

Add a test for a normalized source with headings and paragraphs:
- paragraphs remain whole when short
- heading path is attached
- chunk order is deterministic

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: FAIL on missing generation function

- [ ] **Step 3: Write minimal implementation**

Implement:
- load `normalized.json`
- load matching `metadata.json`
- split cleaned text by paragraph newlines
- assign heading path conservatively from the ordered heading list
- emit one chunk per paragraph initially

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: PASS for the paragraph chunking case

### Task 3: Add oversized paragraph fallback splitting

**Files:**
- Modify: `src/noesis/chunking.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Write the failing test**

Add a test where one paragraph exceeds a small configured token budget and must split into multiple child chunks while preserving:
- shared `paragraph_index`
- unique `chunk_index`
- full `parent_paragraph_text`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: FAIL because oversized paragraphs are not split yet

- [ ] **Step 3: Write minimal implementation**

Implement whitespace-token fallback splitting for oversized paragraphs in `src/noesis/chunking.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: PASS for fallback splitting

### Task 4: Persist chunk outputs locally

**Files:**
- Modify: `src/noesis/storage.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Write the failing test**

Add a test that runs chunk generation for a saved run and expects:
- `evidence/chunks.json` to be written under the run path
- the returned path to match that location
- persisted JSON to contain all chunk records in order

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: FAIL on missing persistence helper

- [ ] **Step 3: Write minimal implementation**

Add storage helpers that serialize chunk records to `run_path / "evidence" / "chunks.json"`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: PASS for persistence

### Task 5: Add CLI support

**Files:**
- Modify: `src/noesis/cli.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Write the failing test**

Add a test that invokes the CLI through `main()` with:
`["chunk", "<run_path>"]`
and expects the chunk file path to be printed.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: FAIL because `chunk` subcommand is not wired

- [ ] **Step 3: Write minimal implementation**

Add a `chunk` subcommand that generates and persists chunk records for the run path.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: PASS for CLI behavior

### Task 6: Full verification

**Files:**
- Modify: `docs/progress-checklist.md` only if implementation changes checklist wording
- Test: `tests/test_phase1_collection.py`
- Test: `tests/test_phase2_normalization.py`
- Test: `tests/test_phase3_chunking.py`

- [ ] **Step 1: Run focused Phase 3 tests**

Run: `python -m pytest tests/test_phase3_chunking.py -q`
Expected: PASS

- [ ] **Step 2: Run full suite**

Run: `python -m pytest -q`
Expected: PASS

- [ ] **Step 3: Review docs impact**

Confirm the implementation still matches the approved Phase 3 checklist and spec.

