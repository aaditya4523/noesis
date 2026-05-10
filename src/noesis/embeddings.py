from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from typing import Callable, Mapping, Protocol

import httpx

from noesis.errors import NoesisConfigurationError, ProviderError, extract_http_error_message
from noesis.models import EvidenceChunk
from noesis.storage import (
    find_embedding_record_sqlite,
    hydrate_lookup_rows_sqlite,
    link_chunk_embedding_sqlite,
    load_run_chunks_from_shared_sqlite,
    save_embedding_record_sqlite,
)
from noesis.vector_store import LanceVectorStore


class MissingGeminiApiKeyError(NoesisConfigurationError):
    pass


class EmbeddingProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class GeminiEmbeddingProvider:
    def __init__(self, *, api_key: str | None = None, model: str = "gemini-embedding-001") -> None:
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise MissingGeminiApiKeyError("GEMINI_API_KEY is required for the embed command")
        self._api_key = resolved_key
        self._model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        try:
            response = httpx.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:embedContent",
                params={"key": self._api_key},
                json={"content": {"parts": [{"text": text}]}, "taskType": "RETRIEVAL_DOCUMENT"},
                timeout=30.0,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = extract_http_error_message(exc) or "Gemini embedding request failed"
            raise ProviderError(message) from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Gemini embedding request failed: {exc}") from exc
        payload = response.json()
        values = payload.get("embedding", {}).get("values", [])
        if not values:
            raise ProviderError("Gemini embedding response did not contain embedding values")
        return [float(value) for value in values]


def build_embedding_payload(chunk: EvidenceChunk) -> str:
    headings = " > ".join(chunk.heading_path)
    return f"Title: {chunk.title}\nHeadings: {headings}\nContent: {chunk.text}"


def embed_run_chunks(
    *,
    db_path,
    vector_store: LanceVectorStore,
    run_id: str,
    provider: EmbeddingProvider,
    embedding_model: str,
    embedding_dimensions: int,
    provider_name: str,
    log: Callable[[str], None] | None = None,
) -> list[str]:
    _log(log, f"embed: loading chunks for run {run_id}")
    rows = load_run_chunks_from_shared_sqlite(db_path, run_id)
    chunks = [_row_to_chunk(row) for row in rows]
    chunk_ids = [_require_str(row, "chunk_id") for row in rows]
    _log(log, f"embed: loaded {len(chunks)} chunks")
    embedding_ids: list[str] = []
    pending_payloads: list[str] = []
    pending_chunks: list[tuple[str, EvidenceChunk, str]] = []

    _log(log, "embed: checking for reusable embeddings")
    for chunk_id, chunk in zip(chunk_ids, chunks, strict=False):
        payload = build_embedding_payload(chunk)
        payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        existing = find_embedding_record_sqlite(
            db_path,
            payload_hash=payload_hash,
            embedding_model=embedding_model,
            embedding_dimensions=embedding_dimensions,
        )
        if existing:
            embedding_id = str(existing["embedding_id"])
            link_chunk_embedding_sqlite(db_path, chunk_id=chunk_id, embedding_id=embedding_id, run_id=run_id)
            embedding_ids.append(embedding_id)
            continue
        pending_payloads.append(payload)
        pending_chunks.append((chunk_id, chunk, payload_hash))

    reused_count = len(embedding_ids)
    _log(
        log,
        f"embed: reusing {reused_count} embeddings, generating {len(pending_payloads)} new embeddings",
    )
    if pending_payloads:
        _log(log, "embed: requesting embeddings from provider")
        vectors = provider.embed_texts(pending_payloads)
        vector_rows: list[dict[str, object]] = []
        for (chunk_id, chunk, payload_hash), vector in zip(pending_chunks, vectors, strict=False):
            embedding_id = save_embedding_record_sqlite(
                db_path,
                payload_hash=payload_hash,
                embedding_model=embedding_model,
                embedding_dimensions=embedding_dimensions,
                provider=provider_name,
                created_at=datetime.now(UTC).isoformat(),
                status="completed",
            )
            vector_rows.append(
                {
                    "embedding_id": embedding_id,
                    "chunk_id": chunk_id,
                    "run_id": run_id,
                    "source_id": chunk.source_id,
                    "heading_path": chunk.heading_path,
                    "title": chunk.title,
                    "vector": vector,
                }
            )
            link_chunk_embedding_sqlite(db_path, chunk_id=chunk_id, embedding_id=embedding_id, run_id=run_id)
            embedding_ids.append(embedding_id)
        _log(log, f"embed: writing {len(vector_rows)} vectors to vector store")
        vector_store.upsert_embeddings(vector_rows)

    _log(log, "embed: completed")
    return embedding_ids


def lookup_similar_chunks(
    *,
    db_path,
    vector_store: LanceVectorStore,
    provider: EmbeddingProvider,
    run_id: str,
    query_text: str,
    embedding_model: str,
    embedding_dimensions: int,
    limit: int,
) -> list[dict[str, object]]:
    del embedding_model, embedding_dimensions
    query_vector = provider.embed_query(query_text)
    rows = vector_store.search(query_vector, run_id=run_id, limit=limit)
    chunk_ids = [str(row["chunk_id"]) for row in rows]
    return hydrate_lookup_rows_sqlite(db_path, chunk_ids)


def _row_to_chunk(row: Mapping[str, object]) -> EvidenceChunk:
    return EvidenceChunk(
        run_id=_require_str(row, "run_id"),
        source_id=_require_str(row, "source_id"),
        source_url=_require_str(row, "source_url"),
        title=_require_str(row, "title"),
        heading_path=_require_str_list(row, "heading_path"),
        source_type=_require_str(row, "source_type"),
        paragraph_index=_require_int(row, "paragraph_index"),
        chunk_index=_require_int(row, "chunk_index"),
        text=_require_str(row, "text"),
        parent_paragraph_text=_require_str(row, "parent_paragraph_text"),
    )


def _require_str(row: Mapping[str, object], key: str) -> str:
    value = row[key]
    if not isinstance(value, str):
        raise TypeError(f"{key} must be a string")
    return value


def _require_int(row: Mapping[str, object], key: str) -> int:
    value = row[key]
    if not isinstance(value, int):
        raise TypeError(f"{key} must be an int")
    return value


def _require_str_list(row: Mapping[str, object], key: str) -> list[str]:
    value = row[key]
    if not isinstance(value, list):
        raise TypeError(f"{key} must be a list")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"{key} must contain only strings")
        normalized.append(item)
    return normalized


def _log(logger: Callable[[str], None] | None, message: str) -> None:
    if logger is not None:
        logger(message)
