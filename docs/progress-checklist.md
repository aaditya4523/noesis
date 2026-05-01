# Noesis Progress Checklist

## Phase 1: Raw Source Acquisition - Status: completed

- [x] Build topic-based raw source acquisition.
- [x] Accept only `topic` as input.
- [x] Fetch internet sources for that topic.
- [x] Save raw source contents locally.
- [x] Save source metadata alongside raw contents.
- [x] Assume default values for `depth`, `width`, `time`, and `style`.
- [x] Do not accept user-provided sources in this phase.
- [x] Prefer official sources first, then high-credibility secondary sources.
- [x] Keep a fixed fetch cap per run.
- [x] Do not add summarization, embeddings, chunking, or handbook generation in this phase.
- [x] Add a reusable Python package and CLI for collection.
- [x] Add tests for prioritization, capped collection, failure tolerance, unique run IDs, and raw corpus persistence.
- [x] Verify live collection writes a local corpus under `data/raw-runs/`.

## Phase 2: HTML Normalization and Link Extraction - Status: completed

- [x] Read saved `raw.html` files from an existing run corpus.
- [x] Extract clean text, page title, headings, and cleaned links from HTML sources only.
- [x] Save the normalized result alongside the raw source without modifying raw files.
- [x] Store links as structured records with `url` and link text.
- [x] Exclude obvious noise links such as social/share/auth-policy links from normalized link storage.
- [x] Skip non-HTML sources in this phase.
- [x] Do not add PDF extraction, page-kind classification, chunking, embeddings, ranking changes, or handbook generation in this phase.
- [x] Add tests for HTML normalization, link extraction, normalized file persistence, and content-root selection.
- [x] Add CLI support for run-level normalization.
- [x] Verify normalization on a real collected corpus.

## Phase 3: Evidence Chunking and Local Persistence - Status: completed

- [x] Read saved `normalized.json` files from an existing run corpus.
- [x] Convert normalized source text into structured evidence chunks.
- [x] Split chunks by section structure first and by paragraph boundaries inside each section.
- [x] Split oversized paragraphs by token-length fallback while preserving paragraph lineage.
- [x] Store only cleaned text in chunk content, not raw HTML tags.
- [x] Attach source-faithful metadata to every chunk, including `run_id`, `source_id`, `url`, `title`, `heading_path`, `chunk_index`, `paragraph_index`, and `source_type`.
- [x] Preserve the small-to-big retrieval relationship so a fine-grained match can expand back to paragraph-level context later.
- [x] Persist chunk records locally for the active handbook run.
- [x] Do not add embeddings, vector search, reranking, handbook generation, or iterative web expansion in this phase.
- [x] Add tests for chunk boundaries, metadata shape, paragraph fallback splitting, and local persistence.
- [x] Add CLI support for run-level chunk generation.
- [x] Verify chunk generation on a real normalized corpus.

## Phase 4: Structured Evidence Storage Foundation - Status: completed

- [x] Read completed run artifacts and persist them into a local `SQLite` database.
- [x] Define a durable schema for `runs`, `sources`, and `chunks` using `run_id`-based isolation rather than per-handbook tables.
- [x] Store chunk text and chunk metadata as structured records so later embedding and retrieval stages read from SQLite instead of JSON files.
- [x] Preserve source-faithful chunk lineage and retrieval metadata, including `source_id`, `source_url`, `title`, `heading_path`, `source_type`, `paragraph_index`, `chunk_index`, and `parent_paragraph_text`.
- [x] Keep storage local-first and limit this phase to structured persistence; do not add embeddings, vector indexing, hybrid retrieval, reranking, or handbook generation.
- [x] Add storage helpers and CLI behavior needed to write Phase 3 chunk outputs into SQLite for the active run.
- [x] Add tests for schema creation, record persistence, and run-scoped reads over stored `run`, `source`, and `chunk` records.
- [x] Verify SQLite-backed persistence on a real collected run.

## Phase 5: DB-First Evidence Pipeline Completion - Status: planned

- [x] Make `SQLite` the canonical store for `runs`, `sources`, `run_sources`, `sections`, and `chunks`.
- [x] Complete source reuse in the live pipeline using canonical URL identity plus TTL-based refresh rules.
- [ ] Persist normalized section structure directly to `SQLite` instead of writing `normalized.json` for the main path.
- [ ] Read section records from `SQLite` during chunk generation instead of relying on filesystem run artifacts.
- [ ] Remove `manifest.json`, `normalized.json`, `chunks.json`, and other `raw-runs` dependencies from the main `collect -> normalize -> chunk` flow.
- [ ] Keep any remaining file-based artifacts as optional debug exports only, not as canonical storage.
- [ ] Update CLI behavior so the primary path operates on shared `data/noesis.db`.
- [ ] Add tests for DB-first collection, normalization, chunk generation, and source reuse across runs.
- [ ] Update docs to reflect the DB-first pipeline and retirement of `raw-runs` as the main storage path.

## Phase 6: Embeddings and Vector Retrieval Foundation - Status: planned

- [ ] Define the embedding input policy for chunks, including how section heading context is incorporated.
- [ ] Generate embeddings eagerly after chunk persistence for active handbook runs.
- [ ] Add `LanceDB` as the vector store for chunk embeddings while keeping `SQLite` as the source of truth.
- [ ] Persist embedding metadata and vector references in structured records linked back to chunk identity.
- [ ] Support reusing existing embeddings when a source is reused and remains within the refresh window.
- [ ] Add vector lookup over the active run with metadata-aware filtering by source, source type, and section context.
- [ ] Add tests for embedding writes, vector-store integration, reuse behavior, and run-scoped retrieval.
- [ ] Verify end-to-end that a collected topic produces retrievable vectorized evidence without filesystem artifact dependencies.
