from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from noesis.answering import GeminiAnswerGenerator, answer_question
from noesis.embeddings import GeminiEmbeddingProvider, embed_run_chunks, lookup_similar_chunks
from noesis.discovery import DDGSDiscoverer
from noesis.errors import DataNotFoundError, NoesisError
from noesis.fetching import HttpSourceFetcher
from noesis.normalization import normalize_run_html_sources, normalize_run_html_sources_sqlite
from noesis.storage import (
    load_run_embedding_config_sqlite,
    replace_run_chunks_shared_sqlite,
    save_run_chunks,
    save_run_chunks_sqlite,
)
from noesis.vector_store import LanceVectorStore

load_dotenv()


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0] not in {"collect", "normalize", "chunk", "embed", "query", "answer", "migrate-vectors"}:
        try:
            _run_collect(argv)
        except NoesisError as exc:
            _print_error_and_exit(exc)
        return

    parser = argparse.ArgumentParser(description="Noesis corpus collection, normalization, and chunking.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Collect raw topic sources.")
    collect_parser.add_argument("topic", help="Topic to research and collect raw sources for.")
    collect_parser.add_argument(
        "--max-sources",
        type=int,
        default=10,
        help="Maximum number of sources to fetch and persist for the run.",
    )

    normalize_parser = subparsers.add_parser("normalize", help="Normalize sources for a collected run in shared SQLite.")
    normalize_parser.add_argument("run_id", nargs="?", help="Run ID stored in shared data/noesis.db.")
    normalize_parser.add_argument(
        "--debug-run-path",
        help="Legacy debug-only path to a saved run under data/raw-runs.",
    )

    chunk_parser = subparsers.add_parser("chunk", help="Generate evidence chunks for a run in shared SQLite.")
    chunk_parser.add_argument("run_id", nargs="?", help="Run ID stored in shared data/noesis.db.")
    chunk_parser.add_argument(
        "--debug-run-path",
        help="Legacy debug-only path to a saved run under data/raw-runs.",
    )
    embed_parser = subparsers.add_parser("embed", help="Generate embeddings for a run in shared SQLite.")
    embed_parser.add_argument("run_id", help="Run ID stored in shared data/noesis.db.")
    query_parser = subparsers.add_parser("query", help="Query retrieved chunks for a run from shared SQLite and LanceDB.")
    query_parser.add_argument("run_id", help="Run ID stored in shared data/noesis.db.")
    query_parser.add_argument("query_text", help="Question or query text to retrieve matching chunks for.")
    query_parser.add_argument("--limit", type=int, default=5, help="Maximum number of chunk matches to return.")
    query_parser.add_argument("--json", action="store_true", dest="json_output", help="Emit results as JSON.")
    answer_parser = subparsers.add_parser("answer", help="Generate a final answer for a run using retrieved chunks.")
    answer_parser.add_argument("run_id", help="Run ID stored in shared data/noesis.db.")
    answer_parser.add_argument("question", help="Question to answer from the run evidence.")
    answer_parser.add_argument("--limit", type=int, default=5, help="Maximum number of chunk matches to use as evidence.")
    subparsers.add_parser("migrate-vectors", help="Import fallback chunk_embeddings.json into real LanceDB.")

    args = parser.parse_args(argv)
    try:
        if args.command == "collect":
            _collect_topic(args.topic, max_sources=args.max_sources)
        elif args.command == "normalize":
            debug_run_path = getattr(args, "debug_run_path", None)
            if debug_run_path:
                run_ref = Path(debug_run_path)
                normalized_paths = normalize_run_html_sources(run_ref)
                for path in normalized_paths:
                    print(path)
                return

            run_id = _resolve_run_id_argument(parser, args.run_id)
            db_path = Path("data") / "noesis.db"
            source_ids = normalize_run_html_sources_sqlite(db_path, run_id)
            for source_id in source_ids:
                print(source_id)
            print(db_path)
        elif args.command == "chunk":
            from noesis.chunking import generate_run_chunks, generate_run_chunks_sqlite

            debug_run_path = getattr(args, "debug_run_path", None)
            if debug_run_path:
                run_ref = Path(debug_run_path)
                chunks = generate_run_chunks(run_ref)
                for index, chunk in enumerate(chunks):
                    print(f"chunk[{index}] length={len(chunk.text)}")
                chunk_path = save_run_chunks(chunks, run_ref)
                sqlite_path = save_run_chunks_sqlite(chunks, run_ref)
                print(chunk_path)
                print(sqlite_path)
                return

            run_id = _resolve_run_id_argument(parser, args.run_id)
            db_path = Path("data") / "noesis.db"
            chunks = generate_run_chunks_sqlite(db_path, run_id)
            for index, chunk in enumerate(chunks):
                print(f"chunk[{index}] length={len(chunk.text)}")
            replace_run_chunks_shared_sqlite(db_path, run_id, chunks)
            print(db_path)
        elif args.command == "embed":
            _embed_run(args.run_id)
        elif args.command == "query":
            _query_run(args.run_id, args.query_text, limit=args.limit, json_output=args.json_output)
        elif args.command == "answer":
            _answer_run(args.run_id, args.question, limit=args.limit)
        elif args.command == "migrate-vectors":
            _migrate_vectors()
    except NoesisError as exc:
        _print_error_and_exit(exc)


def _run_collect(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Collect raw topic sources for Noesis.")
    parser.add_argument("topic", help="Topic to research and collect raw sources for.")
    parser.add_argument(
        "--max-sources",
        type=int,
        default=10,
        help="Maximum number of sources to fetch and persist for the run.",
    )
    args = parser.parse_args(argv)
    _collect_topic(args.topic, max_sources=args.max_sources)


def _collect_topic(topic: str, *, max_sources: int) -> None:
    from noesis.orchestrator import collect_topic_sources_to_db

    db_path = Path("data") / "noesis.db"
    db_run = collect_topic_sources_to_db(
        topic=topic,
        discoverer=DDGSDiscoverer(max_results=max_sources),
        fetcher=HttpSourceFetcher(),
        db_path=db_path,
        max_sources=max_sources,
        on_fetch_error=_print_warning,
    )
    print(db_run.run_id)
    print(db_path)


def _embed_run(run_id: str) -> None:
    db_path = Path("data") / "noesis.db"
    vector_store = LanceVectorStore(Path("data") / "lancedb")
    provider = GeminiEmbeddingProvider()
    embedding_ids = embed_run_chunks(
        db_path=db_path,
        vector_store=vector_store,
        run_id=run_id,
        provider=provider,
        embedding_model="gemini-embedding-001",
        embedding_dimensions=3072,
        provider_name="gemini",
        log=print,
    )
    for embedding_id in embedding_ids:
        print(embedding_id)
    print(db_path)


def _migrate_vectors() -> None:
    vector_root = Path("data") / "lancedb"
    vector_store = LanceVectorStore(vector_root, log=print)
    imported = vector_store.migrate_fallback_vectors()
    print(f"migrated {imported} vectors")
    print(vector_root)


def _query_run(run_id: str, query_text: str, *, limit: int, json_output: bool) -> None:
    results = _retrieve_run_chunks(run_id, query_text, limit=limit)
    if json_output:
        print(json.dumps(results, indent=2))
        return

    for index, row in enumerate(results, start=1):
        headings = " > ".join(_coerce_heading_path(row.get("heading_path")))
        print(f"result[{index}]")
        print(f"title: {row['title']}")
        print(f"headings: {headings}")
        print(f"source_url: {row['source_url']}")
        print(f"text: {row['text']}")
        if index != len(results):
            print()


def _answer_run(run_id: str, question: str, *, limit: int) -> None:
    evidence_rows = _retrieve_run_chunks(run_id, question, limit=limit)
    generator = GeminiAnswerGenerator(model="gemini-3-flash-preview")
    answer = answer_question(question=question, evidence_rows=evidence_rows, generator=generator)
    print(answer)


def _retrieve_run_chunks(run_id: str, query_text: str, *, limit: int) -> list[dict[str, object]]:
    db_path = Path("data") / "noesis.db"
    config = load_run_embedding_config_sqlite(db_path, run_id)
    if config is None:
        raise DataNotFoundError(f"no embeddings found for run {run_id}")

    embedding_model = _require_str(config.get("embedding_model"), "embedding_model")
    embedding_dimensions = _require_int(config.get("embedding_dimensions"), "embedding_dimensions")
    vector_store = LanceVectorStore(Path("data") / "lancedb")
    provider = GeminiEmbeddingProvider(model=embedding_model)
    results = lookup_similar_chunks(
        db_path=db_path,
        vector_store=vector_store,
        provider=provider,
        run_id=run_id,
        query_text=query_text,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions,
        limit=limit,
    )
    return results


def _resolve_run_id_argument(parser: argparse.ArgumentParser, run_id: str | None) -> str:
    if not run_id:
        parser.error("run_id is required unless --debug-run-path is provided")
    run_ref = Path(run_id)
    if run_ref.exists():
        parser.error("filesystem run paths are debug-only; use --debug-run-path for raw-runs paths")
    return run_id


def _coerce_heading_path(value: object) -> list[str]:
    if not isinstance(value, list):
        raise TypeError("heading_path must be a list")
    headings: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError("heading_path items must be strings")
        headings.append(item)
    return headings


def _require_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _require_int(value: object, field_name: str) -> int:
    if not isinstance(value, int):
        raise TypeError(f"{field_name} must be an int")
    return value


def _print_warning(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


def _print_error_and_exit(exc: NoesisError) -> None:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(1)
