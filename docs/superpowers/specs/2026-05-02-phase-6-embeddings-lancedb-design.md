# Phase 6 Embeddings and LanceDB Retrieval Design

## Goal

Add a separate embedding stage that reads DB-backed chunks, generates Gemini embeddings for a run, stores vectors in LanceDB, stores embedding metadata and links in SQLite, and supports run-scoped nearest-neighbor lookup.

## Scope

This design covers:

- a new `embed <run_id>` command
- Gemini-based embedding generation
- LanceDB as the vector lookup store
- SQLite metadata for embeddings and chunk-to-embedding links
- run-scoped nearest-neighbor lookup over embedded chunks
- embedding reuse keyed by content-derived payload hash plus model configuration

This design does not cover:

- cross-run retrieval
- reranking
- hybrid lexical + semantic retrieval
- handbook generation
- background jobs or async orchestration

## Architecture

The pipeline remains split into explicit stages:

1. `collect <topic>`
2. `normalize <run_id>`
3. `chunk <run_id>`
4. `embed <run_id>`

`SQLite` remains the source of truth for run metadata, sources, sections, chunks, and embedding metadata. `LanceDB` stores vectors for nearest-neighbor retrieval.

Embeddings are generated only after chunk persistence. This keeps chunking deterministic and local, and isolates API cost, retries, and provider-specific failure handling inside the embedding stage.

## Provider Strategy

The embedding code should depend on a narrow `EmbeddingProvider` interface.

First implementation:

- `GeminiEmbeddingProvider`

Deferred:

- OpenAI embedding provider
- multi-provider selection beyond the single initial Gemini path

The provider abstraction exists to keep embedding generation separate from retrieval storage and to avoid hard-coding Gemini concerns across the pipeline. The initial product behavior still only supports Gemini.

## Command Behavior

### `embed <run_id>`

Behavior:

- requires a valid `run_id`
- reads run-scoped chunks from SQLite
- builds embedding payloads from chunk metadata
- reuses existing embeddings when the reuse key matches
- generates missing embeddings through Gemini
- writes vectors into LanceDB
- writes metadata and links into SQLite

Failure policy:

- if `GEMINI_API_KEY` is missing, fail immediately with a clear error
- do not create pending embedding rows
- do not silently skip missing credentials

This command is intended to be explicitly user-invoked rather than automatically chained into `chunk`.

## Embedding Payload

Each embedding should be generated from a derived text payload shaped as:

```text
Title: <title>
Headings: <heading path joined>
Content: <chunk text>
```

Rationale:

- `chunk.text` alone can be too context-thin
- `heading_path` provides concept framing
- `title` provides additional stable semantic context

Non-goals:

- embedding raw HTML
- embedding full documents
- embedding arbitrary metadata blobs
- building prompt-like instructions into the payload

The stored chunk text remains unchanged. The embedding payload is a derived representation used only for vector generation and reuse identity.

## Embedding Identity and Reuse

Reuse key:

- `payload_hash`
- `embedding_model`
- `embedding_dimensions`

`chunk_id` is not the primary embedding identity. It is used for lineage and linking only.

Rationale:

- the same semantic payload can appear in multiple runs
- the same chunk can require multiple embedding versions over time
- model changes must not overwrite the meaning of an old embedding record

Multiple embedding versions for the same payload are allowed side by side when the model or dimensions differ.

## SQLite Schema Additions

### `embeddings`

Proposed fields:

- `embedding_id`
- `payload_hash`
- `embedding_model`
- `embedding_dimensions`
- `provider`
- `created_at`
- `status`

Recommended constraints:

- primary key on `embedding_id`
- uniqueness on `(payload_hash, embedding_model, embedding_dimensions)`

`status` should start simple. For the first slice, successful writes are the main case. Since the command fails hard on missing credentials and should not create pending rows, the initial status space can remain minimal.

### `chunk_embeddings`

Proposed fields:

- `chunk_id`
- `embedding_id`
- `run_id`

Recommended constraints:

- foreign key to `chunks.chunk_id`
- foreign key to `embeddings.embedding_id`
- uniqueness on `(chunk_id, embedding_id)`

Purpose:

- link a run’s chunk row to the embedding version currently available
- allow the same chunk to be linked to multiple embedding versions over time

## LanceDB Table Design

Use one LanceDB table for chunk vectors.

Initial fields:

- `embedding_id`
- `chunk_id`
- `run_id`
- `source_id`
- `heading_path`
- `title`
- `vector`

Rationale:

- `embedding_id` is the stable join handle back to SQLite
- `run_id` allows run-scoped filtering during lookup
- `chunk_id`, `source_id`, `heading_path`, and `title` support debugging and result reconstruction

The vector row should correspond to a specific embedding version, not just a chunk.

## Retrieval Scope

The first retrieval slice is run-scoped only.

Behavior:

- query embedding is generated with the same embedding model used for lookup
- LanceDB nearest-neighbor search is filtered by `run_id`
- results are mapped back through `chunk_id` / `embedding_id` into SQLite-backed chunk metadata

Not included yet:

- cross-run retrieval
- topic-aware search over multiple runs
- reranking
- hybrid retrieval

Run-scoped lookup keeps the retrieval contract simple and aligned with the current `run_id`-oriented pipeline.

## Data Flow

### Embedding Ingestion

1. Read chunks for `run_id` from SQLite.
2. Build embedding payload from `title`, `heading_path`, and `chunk.text`.
3. Compute `payload_hash`.
4. Check SQLite for existing embedding metadata matching `(payload_hash, model, dimensions)`.
5. If found, link `chunk_id` to `embedding_id`.
6. If missing, call Gemini embeddings API.
7. Write vector row into LanceDB.
8. Write embedding metadata into SQLite.
9. Write `chunk_embeddings` link row into SQLite.

### Query-Time Lookup

1. Receive query text and `run_id`.
2. Embed the query with the same model configuration.
3. Search LanceDB with nearest-neighbor lookup filtered by `run_id`.
4. Map the top results back through `embedding_id` / `chunk_id`.
5. Return chunk metadata from SQLite.

## Error Handling

Required first-slice behaviors:

- missing `GEMINI_API_KEY` fails fast
- invalid `run_id` fails clearly
- LanceDB write failures should fail the command
- SQLite write failures should fail the command

This design intentionally avoids partial “prepared” or “pending” embedding state in v1.

## Testing Strategy

Add tests for:

- `embed <run_id>` command argument and credential behavior
- embedding payload construction
- payload-hash-based reuse
- SQLite embedding metadata writes
- SQLite chunk-to-embedding links
- LanceDB vector writes
- run-scoped nearest-neighbor lookup
- multi-version coexistence for the same payload when model or dimensions change

Prefer stubbed provider tests over live API calls.

## Implementation Boundaries

Suggested new modules:

- embedding provider module
- LanceDB storage module
- embedding orchestration module
- retrieval module for run-scoped vector lookup

Keep responsibilities separate:

- normalization/chunking should not know about embedding APIs
- provider code should not know about CLI parsing
- LanceDB persistence should not own SQLite metadata policy

## Open Decisions Resolved

Resolved in this design:

- separate `embed <run_id>` command
- Gemini-first provider
- LanceDB for vector storage and lookup
- embedding payload includes `title + heading_path + chunk.text`
- run-scoped nearest-neighbor lookup only
- fail fast on missing `GEMINI_API_KEY`
- reuse key is `(payload_hash, embedding_model, embedding_dimensions)`
- keep multiple embedding versions side by side

## Next Step

The next artifact should be an implementation plan for this design, broken into TDD-sized tasks covering schema changes, provider interface, LanceDB integration, CLI behavior, and run-scoped lookup.
