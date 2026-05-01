# SQLite Evidence Storage Design

Date: 2026-05-01
Status: Approved for implementation

## Goal

Add a structured local storage layer for completed evidence runs so Noesis can persist `runs`, `sources`, and `chunks` in `SQLite` while temporarily retaining `evidence/chunks.json` as a secondary debug/export artifact.

## Scope

This phase sits immediately after Phase 3 chunk generation.

Inputs:

- `manifest.json`
- `sources/*/metadata.json`
- generated `EvidenceChunk` records

Outputs:

- a run-scoped `SQLite` database containing structured `runs`, `sources`, and `chunks`
- the existing `evidence/chunks.json` artifact, still written during the migration period

## Product Boundary

This is a storage foundation phase, not a retrieval or generation phase.

This phase does:

- define a durable relational schema for handbook run evidence
- persist chunk text and metadata in structured records
- keep local-first persistence aligned with the MVP architecture

This phase does not do:

- embeddings
- LanceDB writes
- vector search
- hybrid retrieval
- reranking
- handbook planning
- handbook generation

## Storage Strategy

Approved storage direction remains:

- `SQLite` as the structured source of truth for application state and evidence records
- `LanceDB` later for embeddings and vector retrieval

For this phase, the database should be stored under the run directory so storage remains simple, local, and inspectable:

- `data/raw-runs/<run-id>/evidence/noesis.db`

This keeps the implementation run-scoped for now while preserving a schema that can later be promoted to a shared database without changing record semantics.

## Canonical Write Behavior

During Phase 4, chunk persistence is dual-write:

1. generate in-memory `EvidenceChunk` records
2. persist `evidence/chunks.json`
3. persist the same evidence into `SQLite`

`SQLite` becomes the new structured persistence layer.
`chunks.json` remains temporarily as a secondary artifact for inspection, regression comparison, and migration safety.

## Schema Design

### Runs

The `runs` table stores one row per collected run.

Required fields:

- `run_id` primary key
- `topic`
- `max_sources`

This phase only persists fields already available from `manifest.json`.

### Sources

The `sources` table stores one row per source within a run.

Required fields:

- `run_id`
- `source_id`
- `source_url`
- `title`
- `source_type`
- `final_url`
- `domain`
- `published_date`
- `content_type`

Uniqueness should be enforced by `(run_id, source_id)`.

### Chunks

The `chunks` table stores one row per emitted chunk.

Required fields:

- `run_id`
- `source_id`
- `source_url`
- `title`
- `heading_path`
- `source_type`
- `paragraph_index`
- `chunk_index`
- `text`
- `parent_paragraph_text`

`heading_path` should be stored as JSON text for now.

Uniqueness should be enforced by:

- `(run_id, source_id, paragraph_index, chunk_index)`

## Ordering and Read Semantics

Writes must be deterministic for the same run inputs.

Read helpers added in this phase should support:

- fetching sources for a run ordered by `source_id`
- fetching chunks for a run ordered by `source_id`, `paragraph_index`, `chunk_index`

This is sufficient for verification, regression tests, and the next embedding phase.

## Module Boundaries

### `src/noesis/storage.py`

Owns:

- SQLite schema creation
- run/source/chunk persistence
- run-scoped storage reads for tests and later pipeline stages
- existing JSON artifact persistence

### `src/noesis/chunking.py`

Owns:

- generation of `EvidenceChunk` records only

It should not take on database responsibilities.

### `src/noesis/cli.py`

Owns:

- invoking chunk generation
- invoking JSON persistence
- invoking SQLite persistence
- printing resulting artifact paths

## Migration Posture

This design intentionally avoids deleting the JSON artifact yet.

The planned follow-up step is to make SQLite the sole canonical persisted output and retire `evidence/chunks.json` once downstream embedding and retrieval stages consume the database directly.

## Testing Requirements

Phase 4 tests must prove:

- the database file is created in the expected run location
- the schema is created automatically when persisting evidence
- run metadata from `manifest.json` is stored correctly
- source metadata from `metadata.json` is stored correctly
- chunk rows match the generated chunk records exactly
- run-scoped reads return deterministic ordered records
- the CLI continues to write `chunks.json` while also writing SQLite

## Acceptance Criteria

Phase 4 is complete when:

- chunk generation for a normalized run writes both `evidence/chunks.json` and `evidence/noesis.db`
- SQLite contains accurate `runs`, `sources`, and `chunks` rows for the run
- tests cover schema creation, persistence, ordered reads, and CLI dual-write behavior
- no embeddings, vector indexing, or retrieval features are introduced in the phase
