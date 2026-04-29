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
