# Noesis Evidence Retrieval Design

Date: 2026-04-30
Status: Drafted from approved brainstorming decisions

## Goal

Define the MVP evidence-processing and retrieval architecture that sits between:

- Phase 2 completed normalization
- later handbook planning and handbook generation

The design is optimized for handbook creation as the MVP, not for generic chat or a standalone long-term knowledge base.

## Product Boundary

The MVP product goal is handbook creation.

Cross-run knowledge accumulation is useful, but it is not the primary user-facing goal. The system must work end-to-end for a single handbook run even without a large pre-existing shared corpus.

Persistence policy:

- data is stored locally by default
- evidence persists through handbook creation
- after handbook creation, persistence is optional
- a run may be deleted, archived, or selectively retained

## Approved Architecture Direction

### Application shape

The system should be:

- local-first for storage
- remote by default for embeddings and generation
- local optional for embeddings and generation
- handbook-oriented rather than generic RAG-oriented

The default user experience should be one recommended provider path with optional advanced overrides.

### Provider strategy

Default recommendation:

- one-key simplicity
- one recommended remote path
- provider-pluggable internals underneath

Approved default preference:

- remote by default
- local optional
- one recommended path, but options to choose

### Storage shape

Do not use one table per handbook.

Use logical per-handbook isolation via identifiers such as `run_id` or `handbook_id`, while keeping a stable schema.

Approved MVP storage split:

- `SQLite` for application state and structured records
- `LanceDB` for vector retrieval over chunk embeddings

SQLite responsibilities:

- runs
- sources
- chunk metadata
- handbook artifacts
- retention state

LanceDB responsibilities:

- chunk embeddings
- retrieval metadata filters
- nearest-neighbor search

## Evidence Preparation Design

### Input

Phase 3 begins from completed normalized source outputs.

Inputs are expected to include:

- cleaned source text
- source URL
- page title
- heading list / structure
- cleaned extracted links
- source metadata from earlier phases

### Chunk content

Chunks should contain only cleaned text.

They should not store raw HTML tags as chunk content.

However, chunks should preserve structure as metadata, such as:

- source URL
- page title
- heading path
- source tier such as `official` or `secondary`
- source identity / source ID

### Chunking strategy

Approved chunking strategy:

- rule-based structural chunking only for MVP
- no LLM-assisted chunking or summarization in MVP

Chunking order:

1. split by structural sections / heading boundaries first
2. use paragraphs as the primary chunk unit inside a section
3. if a paragraph is too large, split that paragraph by token length

Retrieval context policy:

- use small-to-big chunking
- if a small chunk matches the query, expand to the full paragraph as the primary context unit

This keeps retrieval precise while preserving enough surrounding explanation for handbook synthesis and citation use.

## Embedding Strategy

Approved embedding strategy:

- remote by default
- local optional
- eager embedding after chunking for the active handbook run

This means the active run lifecycle is:

1. collect
2. normalize
3. chunk
4. attach metadata
5. embed immediately
6. store in SQLite and LanceDB
7. retrieve during planning and writing

Rationale:

- retrieval becomes ready before handbook generation starts
- the system does not defer embedding work until the most timing-sensitive stage

## Retrieval Strategy

Approved retrieval strategy:

- hybrid retrieval for MVP

Hybrid retrieval means combining:

- semantic vector similarity
- lightweight lexical matching
- metadata filtering

Metadata filters may include:

- source tier such as `official`
- source identity / domain
- handbook or run scope
- heading/section constraints where useful

This is preferred over pure semantic search because Noesis is a technical study engine where exact terminology frequently matters.

## Recommended Default Stack

Approved recommended product posture:

- one recommended remote path
- one-key simplicity for default

Current recommended default stack direction:

- OpenAI for embeddings
- OpenAI for generation

Optional paths can later include:

- local embedding backends
- local generation backends
- alternate remote providers through internal abstractions

## Non-Goals For This Phase

Do not make this phase about:

- full hosted cloud infrastructure
- multi-user collaboration
- generalized persistent memory as the product
- LLM-generated chunk summaries
- broad autonomous crawling as the main focus
- UI-heavy app work

## Open Decisions

The major architecture direction is approved, but a few decisions remain open:

1. retrieval scoring formula
   - how to combine semantic score, lexical score, and source-tier boosts

2. reranking
   - whether to add a reranking stage in MVP or keep retrieval to hybrid search only

3. chunk schema details
   - exact fields for chunk metadata and paragraph expansion mapping

4. handbook planning boundary
   - where evidence retrieval ends and handbook outline / coverage planning begins

5. persistence lifecycle details
   - exact retention options after handbook creation and how promotion/deletion is represented in SQLite

## Recommended Next Step

The next implementation phase should be:

`Phase 3: Evidence Preparation and Retrieval Foundation`

That phase should cover:

- chunking normalized sources into evidence units
- attaching source-faithful metadata
- eager embedding
- local storage in SQLite and LanceDB
- hybrid retrieval over the active handbook run

It should not yet attempt full handbook generation in the same implementation slice.
