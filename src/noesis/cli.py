from __future__ import annotations

import argparse
import sys
from pathlib import Path

from noesis.discovery import DDGSDiscoverer
from noesis.fetching import HttpSourceFetcher
from noesis.normalization import normalize_run_html_sources
from noesis.orchestrator import collect_topic_sources_to_db
from noesis.storage import save_run_chunks, save_run_chunks_sqlite, save_run_corpus


def main() -> None:
    argv = sys.argv[1:]
    if argv and argv[0] not in {"collect", "normalize", "chunk"}:
        _run_collect(argv)
        return

    parser = argparse.ArgumentParser(description="Noesis corpus collection, normalization, and chunking.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Collect raw topic sources.")
    collect_parser.add_argument("topic", help="Topic to research and collect raw sources for.")

    normalize_parser = subparsers.add_parser("normalize", help="Normalize saved HTML sources in a run.")
    normalize_parser.add_argument("run_path", help="Path to a saved run under data/raw-runs.")

    chunk_parser = subparsers.add_parser("chunk", help="Generate evidence chunks for a normalized run.")
    chunk_parser.add_argument("run_path", help="Path to a saved run under data/raw-runs.")

    args = parser.parse_args(argv)
    if args.command == "collect":
        _collect_topic(args.topic)
    elif args.command == "normalize":
        normalized_paths = normalize_run_html_sources(Path(args.run_path))
        for path in normalized_paths:
            print(path)
    elif args.command == "chunk":
        from noesis.chunking import generate_run_chunks

        chunks = generate_run_chunks(Path(args.run_path))
        for index, chunk in enumerate(chunks):
            print(f"chunk[{index}] length={len(chunk.text)}")
        chunk_path = save_run_chunks(chunks, Path(args.run_path))
        sqlite_path = save_run_chunks_sqlite(chunks, Path(args.run_path))
        print(chunk_path)
        print(sqlite_path)


def _run_collect(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description="Collect raw topic sources for Noesis.")
    parser.add_argument("topic", help="Topic to research and collect raw sources for.")
    args = parser.parse_args(argv)
    _collect_topic(args.topic)


def _collect_topic(topic: str) -> None:
    db_path = Path("data") / "noesis.db"
    db_run = collect_topic_sources_to_db(
        topic=topic,
        discoverer=DDGSDiscoverer(max_results=10),
        fetcher=HttpSourceFetcher(),
        db_path=db_path,
        max_sources=10,
    )
    print(db_run.run_id)
    print(db_path)
