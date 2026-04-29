# Noesis MVP Plan: Handbook Engine First

## Summary
Build `Noesis` as a `handbook-generation engine` first, not as a full SaaS app. The MVP should accept a learning goal, optional user-provided resources, and a small set of standardized controls (`depth`, `width`, `time`, `style`), then gather authoritative sources, build a coverage-aware study plan, and output a `source-cited Markdown handbook` optimized for serious exam/interview preparation.

Use a `Python engine + TypeScript app shell` split:
- `Python` owns ingestion, retrieval, ranking, planning, generation, citations, and evaluation.
- `TypeScript` is a thin local/BYO-key UI/API shell for input, job orchestration, and artifact viewing/export.
- Defer auth, billing, team features, and non-handbook artifact generation until the handbook engine proves quality.

## Recommended Architecture
Choose this over a NotebookLM-style broad clone:
1. `Plan-first engine`
   - First classify the request, detect topic breadth, and create a module plan before generation.
   - Broad topics like `AWS` or `system design` become a sequence of handbook modules, not one oversized artifact.
2. `Research-first retrieval`
   - Build a source pack from `official docs first`, then `high-credibility secondary sources`.
   - Persist normalized source metadata: title, URL/path, publisher, publish/update date, section anchors, images, and extraction provenance.
3. `Generate from evidence, not memory`
   - The generator only writes from the selected evidence pack plus user instructions.
   - Every major section must carry citations and source metadata.
4. `Evaluation before expansion`
   - Handbook quality must be measured before adding cheat sheets, quizzes, audio, or SaaS layers.

## Key Implementation Changes
### 1. Product boundary and public interfaces
Define a minimal request contract for the engine:
- `topic`: free-text learning goal
- `template`: initially fixed to `handbook`
- `controls`: `depth`, `width`, `time`, `style`
- `custom_directions`: optional free-text instructions
- `user_sources`: uploaded files, pasted text, URLs
- `source_policy`: default `official_first`, optional `disable_auto_gather`
- `provider_config`: BYO keys and/or local model settings

Define a minimal response contract:
- `module_plan`: ordered modules if topic is broad
- `selected_module`: module generated in this run
- `source_pack`: normalized source list with metadata
- `coverage_map`: required subtopics, covered subtopics, gaps
- `artifact_markdown`: final handbook
- `citations`: section-level citation map
- `generation_report`: warnings, weak-coverage flags, skipped sources

### 2. Python engine subsystems
Implement the engine as isolated units with explicit contracts:
- `Source ingestion`
  - Parse local files, web pages, and pasted text.
  - Normalize metadata and extract clean text + structure.
  - Keep raw extraction and cleaned representation separate.
- `Source acquisition`
  - Query official sources first.
  - Use secondary sources only to fill pedagogical or coverage gaps.
  - Attach confidence and source tier to every candidate.
- `Source ranking and filtering`
  - Rank by authority, topicality, freshness when relevant, and metadata completeness.
  - Deduplicate near-identical sources and preserve canonical URLs.
- `Topic decomposition`
  - Detect when one handbook would be too broad.
  - Produce ordered modules with prerequisites and coverage rationale.
- `Coverage planner`
  - Turn the selected module into a required topic graph.
  - Map each required topic to supporting sources before generation.
- `Handbook generator`
  - Produce a standardized but adaptive handbook spine.
  - Stable sections should include: objective, key concepts, foundations, exam/interview-relevant mechanisms, worked examples, pitfalls, quick checks, and cited references.
  - Section presence and ordering may adapt by domain.
- `Citation and evidence layer`
  - Section-level citations are mandatory.
  - Preserve dates, source identity, and anchors in a compact standardized citation format.
- `Markdown renderer`
  - Emit a clean Markdown handbook with deterministic section formatting.
  - Include a compact source appendix and metadata block.

### 3. Retrieval and generation strategy
Avoid a naive RAG pipeline. Use:
- `Query planning` from the user goal and selected module
- `Multi-query retrieval` for subtopics rather than one broad search
- `Authority-aware reranking`
- `Coverage checking` before final synthesis
- `Gap handling`
  - If key topics lack strong evidence, surface a warning and optionally fetch more
  - Do not silently generate mastery-claim content from weak evidence

Generation policy:
- Use strong API models by default when a user supplies a key.
- Support local models as a secondary mode for privacy/offline workflows.
- Make the final synthesis provider-pluggable so the engine is not tied to one vendor.

### 4. TypeScript shell
Build only the minimum shell needed to exercise the engine:
- Single-user local app
- Job submission form for topic, controls, directions, and source uploads
- Source review pane showing gathered sources and metadata
- Generated handbook viewer with section navigation and source appendix
- “Generate next module” action for broad topics
- Local persistence for runs and artifacts
- BYO-key management stored locally, not in hosted infrastructure

### 5. Storage and data model
Persist four primary entities:
- `Run`
  - user request, provider settings snapshot, status, selected module, warnings
- `Source`
  - normalized source metadata, extracted text reference, authority tier, provenance
- `CoveragePlan`
  - module graph, required subtopics, evidence mapping, missing coverage
- `Artifact`
  - final Markdown, citation map, generation report, rendered metadata

Use a relational store or document DB for app state, but keep the engine interfaces storage-agnostic. Use a vector index only as a retrieval aid, not as the primary source of truth.

### 6. What to defer
Do not include in this first implementation plan:
- auth
- billing/credits
- collaboration/sharing
- audio/video outputs
- quiz book / cheat sheet / interview guide generation
- browser-heavy agent tooling
- large conversational memory systems

## Test Plan
### Engine correctness
- Generate a handbook from only user-uploaded files.
- Generate a handbook from auto-gathered official sources only.
- Generate a hybrid handbook from user sources plus auto-gathered sources.
- Reject or warn when coverage is weak for mastery-level output.
- Decompose a broad topic into modules instead of producing one bloated handbook.

### Evidence and citation behavior
- Every major section has at least one citation.
- Citation metadata includes source identity and date when available.
- Unsupported claims are not introduced in the final artifact.
- Duplicate sources are collapsed without losing provenance.

### Retrieval and planning
- Official sources outrank secondary sources when both cover the same subtopic.
- Multi-query retrieval improves subtopic coverage versus one-shot retrieval.
- Coverage planner flags missing required areas before generation.
- Topic decomposition is stable for representative inputs like `AWS cert prep`, `system design`, and `game theory`.

### Output quality
- Handbook remains standardized in format but adapts section emphasis by topic.
- Output is concise in wording but broad in coverage.
- Worked examples appear when the selected style or domain implies they are necessary.
- Markdown renders predictably and exports cleanly.

### Local/BYO-key shell
- User can run with only a local model configuration.
- User can run with only provider API keys.
- Keys remain local to the machine.
- Failed runs preserve partial diagnostics and source acquisition logs.

## Assumptions and Defaults
- First artifact is `handbook` only.
- MVP is `single-user local/BYO-key`, not hosted SaaS.
- Auto-gather is enabled by default, with an explicit opt-out.
- Source policy is `official documentation first`, then `high-credibility secondary sources`.
- The engine may use local models for ingestion/retrieval helpers, but the best-quality final synthesis path assumes a user-supplied API key.
- Broad topics are handled as `module sequences`; each run generates one module handbook and offers continuation.
- The product promise for MVP is `high-confidence study material`, not guaranteed pass-rate claims.
