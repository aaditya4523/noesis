from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4
from datetime import UTC, datetime

from noesis.errors import DataNotFoundError, FetchError
from noesis.models import AcquisitionRun, CollectedSource
from noesis.normalization import normalize_html_document
from noesis.ranking import prioritize_candidates
from noesis.chunking import generate_document_chunks
from noesis.source_reuse import canonicalize_url, should_refresh_source
from noesis.storage import (
    ensure_shared_sqlite_schema,
    find_reusable_source_sqlite,
    link_run_to_existing_source_sqlite,
    save_run_record_sqlite,
    save_source_graph_sqlite,
)


def _require_int(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int | str):
        raise TypeError(f"{field_name} must be an int-compatible value")
    return int(value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("expected string-compatible value")
    return value


def _require_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string value")
    return value


def collect_topic_sources(
    topic: str,
    discoverer,
    fetcher,
    output_root: Path,
    max_sources: int = 10,
    on_fetch_error=None,
) -> AcquisitionRun:
    del output_root

    prioritized = prioritize_candidates(discoverer.discover(topic))
    collected: list[CollectedSource] = []

    for candidate in prioritized[:max_sources]:
        try:
            result = fetcher.fetch(candidate)
        except FetchError as exc:
            if on_fetch_error is not None:
                on_fetch_error(str(exc))
            continue
        except Exception as exc:
            if on_fetch_error is not None:
                on_fetch_error(f"failed to fetch {candidate.url}: {exc}")
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

    if not collected:
        raise DataNotFoundError(f"no sources were collected for topic '{topic}'")

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


def collect_topic_sources_to_db(
    topic: str,
    discoverer,
    fetcher,
    db_path: Path,
    max_sources: int = 10,
    ttl_days: int = 365,
    now: datetime | None = None,
    on_fetch_error=None,
) -> AcquisitionRun:
    ensure_shared_sqlite_schema(db_path)
    current_time = now or datetime.now(UTC)
    current_time_iso = current_time.isoformat()
    run_id = _build_run_id(topic)
    save_run_record_sqlite(db_path, run_id=run_id, topic=topic, created_at=current_time_iso)

    prioritized = prioritize_candidates(discoverer.discover(topic))
    collected: list[CollectedSource] = []
    linked_sources = 0

    for source_order, candidate in enumerate(prioritized[:max_sources]):
        candidate_canonical_url = canonicalize_url(candidate.url)
        existing = find_reusable_source_sqlite(
            db_path,
            canonical_url=candidate_canonical_url,
            now=current_time_iso,
        )
        if existing and not should_refresh_source(
            _optional_str(existing["last_fetched_at"]),
            now=current_time,
            ttl_days=_require_int(existing["refresh_ttl_days"], "refresh_ttl_days"),
        ):
            link_run_to_existing_source_sqlite(
                db_path,
                run_id=run_id,
                source_id=_require_str(existing["source_id"], "source_id"),
                source_order=source_order,
            )
            linked_sources += 1
            continue

        try:
            result = fetcher.fetch(candidate)
        except FetchError as exc:
            if on_fetch_error is not None:
                on_fetch_error(str(exc))
            continue
        except Exception as exc:
            if on_fetch_error is not None:
                on_fetch_error(f"failed to fetch {candidate.url}: {exc}")
            continue

        final_canonical_url = canonicalize_url(result.final_url)
        existing = find_reusable_source_sqlite(
            db_path,
            canonical_url=final_canonical_url,
            now=current_time_iso,
        )
        if existing and not should_refresh_source(
            _optional_str(existing["last_fetched_at"]),
            now=current_time,
            ttl_days=_require_int(existing["refresh_ttl_days"], "refresh_ttl_days"),
        ):
            link_run_to_existing_source_sqlite(
                db_path,
                run_id=run_id,
                source_id=_require_str(existing["source_id"], "source_id"),
                source_order=source_order,
            )
            linked_sources += 1
            continue

        source_id = _require_str(existing["source_id"], "source_id") if existing else f"source-{uuid4().hex[:12]}"
        raw_text = result.raw_content.decode("utf-8", errors="ignore")
        normalized = normalize_html_document(source_id=source_id, final_url=result.final_url, raw_html=raw_text)
        chunks = generate_document_chunks(
            run_id=run_id,
            normalized=normalized.to_dict(),
            source_type=candidate.source_type,
            fallback_source_id=source_id,
        )
        save_source_graph_sqlite(
            db_path,
            run_id=run_id,
            source_order=source_order,
            source_id=source_id,
            canonical_url=final_canonical_url,
            url=candidate.url,
            final_url=result.final_url,
            title=normalized.title or candidate.title,
            domain=candidate.domain,
            source_type=candidate.source_type,
            content_type=result.content_type,
            raw_content=result.raw_content,
            fetched_at=current_time_iso,
            refresh_ttl_days=ttl_days,
            normalized=normalized,
            chunks=chunks,
        )
        collected.append(
            CollectedSource(
                source_id=source_id,
                title=normalized.title or candidate.title,
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

    if not collected and linked_sources == 0:
        raise DataNotFoundError(f"no sources were collected for topic '{topic}'")

    return AcquisitionRun(
        run_id=run_id,
        topic=topic,
        max_sources=max_sources,
        sources=collected,
    )
