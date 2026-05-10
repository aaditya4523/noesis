import type { Artifact, HeadingReferenceItem } from "./types";

export const sourcePresets = ["Docs", "Web", "Papers", "Notes"];

export const processLogs = [
  "Collecting sources",
  "Normalizing material",
  "Preparing evidence",
  "Drafting handbook",
  "Finalizing artifact",
  "Handbook ready"
];

export const artifacts: Artifact[] = [
  {
    title: "Prompt Engineering Handbook",
    source: "Docs + Papers",
    status: "Ready",
    detail: "24 minutes ago",
    dateGroup: "Today",
    prompt: "Summarize prompt patterns that improve structured model outputs.",
    subtitle: "Operational brief for reusable prompt patterns",
    purpose:
      "Convert scattered prompt guidance into an auditable handbook with examples, failure modes, and review criteria attached to every recommendation.",
    markdown: `# Prompt Engineering Handbook

Operational brief for reusable prompt patterns

## What this artifact is for

Convert scattered prompt guidance into an auditable handbook with examples, failure modes, and review criteria attached to every recommendation.

> Summarize prompt patterns that improve structured model outputs.

## Summary

### Distilled findings

1. Instruction shape matters most when examples, constraints, and output format agree.
2. Evaluation prompts work better when failure modes are named before generation.
3. Reusable prompt handbooks should keep source notes beside each recommendation.

## Sources

### Evidence trail

- [Prompt Files](#prompt-files): source material retained beside the generated recommendation so the artifact can be audited without switching context.
- [Examples](#examples): source material retained beside the generated recommendation so the artifact can be audited without switching context.
- [Checklist](#checklist): source material retained beside the generated recommendation so the artifact can be audited without switching context.

## Recommendations

### Operating moves

- Keep every reusable prompt pattern paired with a concrete example, a failure mode, and a success criterion.
- Separate instruction shape, evidence handling, and output formatting into distinct review passes before publishing the handbook.
- Treat source diversity as a visible quality signal; a strong artifact should cite documents, examples, and checklist evidence independently.

## Evaluation checklist

### Reviewer gates

- Does the prompt state constraints before generation starts?
- Are examples aligned with the exact output shape requested?
- Can a reviewer trace each recommendation back to source material?
- Is the final artifact useful as a standalone markdown file?`
  },
  {
    title: "Retrieval Quality Notes",
    source: "Web + Notes",
    status: "Ready",
    detail: "Yesterday",
    dateGroup: "Yesterday",
    prompt: "Collect practical methods for diagnosing retrieval quality regressions.",
    subtitle: "Quality map for retrieval regression reviews",
    purpose:
      "Separate retrieval symptoms into observable categories so teams can compare rewrites, indexes, and source coverage without guessing.",
    markdown: `# Retrieval Quality Notes

Quality map for retrieval regression reviews

## What this artifact is for

Separate retrieval symptoms into observable categories so teams can compare rewrites, indexes, and source coverage without guessing.

> Collect practical methods for diagnosing retrieval quality regressions.

## Summary

### Distilled findings

1. Track empty, stale, and over-broad retrieval separately.
2. Compare query rewrites against a small golden set before expanding coverage.
3. Surface source diversity in the artifact view so weak evidence is visible.

## Sources

### Evidence trail

- [Web Captures](#web-captures): captured examples show query shape, result set, and source freshness beside the diagnosis.
- [Notes](#notes): reviewer observations remain attached to the retrieval run they describe.
- [Metrics](#metrics): quality signals are separated so stale retrieval does not hide behind aggregate scores.

## Recommendations

### Operating moves

- Review empty, stale, and over-broad retrieval as separate failure classes.
- Keep a compact golden query set before changing rewrite or ranking behavior.
- Show source diversity in the artifact view so weak evidence is visible before publication.

## Evaluation checklist

### Reviewer gates

- Are empty results counted separately from irrelevant results?
- Does every rewrite comparison use the same golden set?
- Can a reviewer see which source family produced each recommendation?
- Is source freshness visible before the artifact is accepted?`
  },
  {
    title: "Agent Planning Brief",
    source: "Docs",
    status: "Draft",
    detail: "This week",
    dateGroup: "Yesterday",
    prompt: "Turn agent planning rules into a compact implementation checklist.",
    subtitle: "Execution brief for agentic development plans",
    purpose:
      "Compress planning, delegation, and verification rules into a checklist that keeps ownership and proof visible during implementation.",
    markdown: `# Agent Planning Brief

Execution brief for agentic development plans

## What this artifact is for

Compress planning, delegation, and verification rules into a checklist that keeps ownership and proof visible during implementation.

> Turn agent planning rules into a compact implementation checklist.

## Summary

### Distilled findings

1. Clarify ownership before dispatching parallel work.
2. Keep verification commands close to the plan step they prove.
3. Review generated diffs before integrating any delegated output.

## Sources

### Evidence trail

- [Plan](#plan): implementation checkpoints are preserved with the task they validate.
- [Review](#review): review notes stay attached to the changed surface area.
- [Risks](#risks): unresolved assumptions are visible before integration.

## Recommendations

### Operating moves

- Assign explicit file ownership before parallel implementation starts.
- Require fresh verification evidence before calling a step complete.
- Inspect delegated diffs before merging any generated work into the main tree.

## Evaluation checklist

### Reviewer gates

- Is every parallel task independent enough to avoid write conflicts?
- Does each completed step name the command that proves it?
- Were generated diffs inspected before integration?
- Are remaining risks stated before the branch is closed?`
  }
];

export const headingReferenceItems: HeadingReferenceItem[] = [
  { id: "title", label: "Title", level: "H1" },
  { id: "what-this-artifact-is-for", label: "What this artifact is for", level: "H2" },
  { id: "summary", label: "Summary", level: "H2" },
  { id: "distilled-findings", label: "Distilled findings", level: "H3" },
  { id: "sources", label: "Sources", level: "H2" },
  { id: "evidence-trail", label: "Evidence trail", level: "H3" },
  { id: "recommendations", label: "Recommendations", level: "H2" },
  { id: "operating-moves", label: "Operating moves", level: "H3" },
  { id: "evaluation-checklist", label: "Evaluation checklist", level: "H2" },
  { id: "reviewer-gates", label: "Reviewer gates", level: "H3" }
];
