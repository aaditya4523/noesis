from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from noesis.models import AcquisitionRun, CollectedSource
from noesis.ranking import prioritize_candidates


def collect_topic_sources(
    topic: str,
    discoverer,
    fetcher,
    output_root: Path,
    max_sources: int = 10,
) -> AcquisitionRun:
    del output_root

    prioritized = prioritize_candidates(discoverer.discover(topic))
    collected: list[CollectedSource] = []

    for candidate in prioritized[:max_sources]:
        try:
            result = fetcher.fetch(candidate)
        except Exception:
            continue

        index = len(collected) + 1
        collected.append(
            CollectedSource(
                source_id=f"source-{index:03d}",
                title=candidate.title,
                url=candidate.url,
                final_url=result.final_url,
                domain=candidate.domain,
                source_type=candidate.source_type,
                snippet=candidate.snippet,
                status_code=result.status_code,
                content_type=result.content_type,
                raw_content=result.raw_content,
                published_date=result.published_date,
            )
        )

    return AcquisitionRun(
        run_id=_build_run_id(topic),
        topic=topic,
        max_sources=max_sources,
        sources=collected,
    )


def _build_run_id(topic: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    prefix = normalized or "topic"
    return f"{prefix}-{uuid4().hex[:8]}"
