from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any, Callable

from noesis.errors import VectorStoreError

try:
    import lancedb  # type: ignore
except ImportError:  # pragma: no cover - fallback exercised in tests
    lancedb = None


class LanceVectorStore:
    def __init__(
        self,
        root: Path,
        table_name: str = "chunk_embeddings",
        log: Callable[[str], None] | None = None,
    ) -> None:
        self._root = root
        self._table_name = table_name
        self._log = log

    def upsert_embeddings(self, records: list[dict[str, Any]]) -> None:
        if not records:
            return
        if lancedb is not None:
            self.migrate_fallback_vectors()
            self._upsert_lancedb(records)
            return
        self._upsert_fallback(records)

    def search(self, query_vector: list[float], *, run_id: str, limit: int) -> list[dict[str, Any]]:
        if lancedb is not None:
            self.migrate_fallback_vectors()
            return self._search_lancedb(query_vector, run_id=run_id, limit=limit)
        return self._search_fallback(query_vector, run_id=run_id, limit=limit)

    def migrate_fallback_vectors(self) -> int:
        if lancedb is None:
            raise VectorStoreError("LanceDB is not installed")
        return self._migrate_fallback_to_lancedb()

    def _upsert_lancedb(self, records: list[dict[str, Any]]) -> None:
        self._emit("vector-store: using lancedb backend for upsert")
        self._root.mkdir(parents=True, exist_ok=True)
        backend = _require_lancedb()
        database = backend.connect(str(self._root))
        try:
            table = database.open_table(self._table_name)
        except Exception:
            database.create_table(self._table_name, data=records)
            return
        existing_ids = {str(row["embedding_id"]) for row in _table_to_rows(table)}
        new_records = [row for row in records if str(row["embedding_id"]) not in existing_ids]
        if new_records:
            table.add(new_records)

    def _search_lancedb(self, query_vector: list[float], *, run_id: str, limit: int) -> list[dict[str, Any]]:
        self._emit("vector-store: using lancedb backend for search")
        backend = _require_lancedb()
        database = backend.connect(str(self._root))
        table = database.open_table(self._table_name)
        rows = table.search(query_vector).where(f"run_id = '{run_id}'").limit(limit).to_list()
        return [dict(row) for row in rows]

    def _upsert_fallback(self, records: list[dict[str, Any]]) -> None:
        self._emit("vector-store: using fallback json backend for upsert")
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._root / f"{self._table_name}.json"
        existing: list[dict[str, Any]] = []
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
        by_id = {str(row["embedding_id"]): row for row in existing}
        for record in records:
            by_id.setdefault(str(record["embedding_id"]), record)
        path.write_text(json.dumps(list(by_id.values()), indent=2), encoding="utf-8")

    def _search_fallback(self, query_vector: list[float], *, run_id: str, limit: int) -> list[dict[str, Any]]:
        self._emit("vector-store: using fallback json backend for search")
        path = self._root / f"{self._table_name}.json"
        if not path.exists():
            return []
        rows = [row for row in json.loads(path.read_text(encoding="utf-8")) if str(row["run_id"]) == run_id]
        scored = [
            (self._cosine_similarity(query_vector, [float(value) for value in row["vector"]]), row)
            for row in rows
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [row for _score, row in scored[:limit]]

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = sqrt(sum(value * value for value in left))
        right_norm = sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _emit(self, message: str) -> None:
        if self._log is not None:
            self._log(message)

    def _migrate_fallback_to_lancedb(self) -> int:
        path = self._root / f"{self._table_name}.json"
        if not path.exists():
            self._emit("vector-store: no fallback json file found")
            return 0

        fallback_rows = json.loads(path.read_text(encoding="utf-8"))
        if not fallback_rows:
            self._emit("vector-store: fallback json file is empty")
            return 0

        self._emit("vector-store: migrating fallback json rows into lancedb")
        self._root.mkdir(parents=True, exist_ok=True)
        backend = _require_lancedb()
        database = backend.connect(str(self._root))
        try:
            table = database.open_table(self._table_name)
        except Exception:
            database.create_table(self._table_name, data=fallback_rows)
            self._emit(f"vector-store: imported {len(fallback_rows)} fallback rows into lancedb")
            return len(fallback_rows)

        existing_ids = {str(row["embedding_id"]) for row in _table_to_rows(table)}
        new_rows = [row for row in fallback_rows if str(row["embedding_id"]) not in existing_ids]
        if new_rows:
            table.add(new_rows)
        self._emit(f"vector-store: imported {len(new_rows)} fallback rows into lancedb")
        return len(new_rows)


def _require_lancedb() -> Any:
    if lancedb is None:
        raise VectorStoreError("LanceDB is not installed")
    return lancedb


def _table_to_rows(table: Any) -> list[dict[str, Any]]:
    if hasattr(table, "to_list"):
        return [dict(row) for row in table.to_list()]
    if hasattr(table, "to_arrow"):
        return [dict(row) for row in table.to_arrow().to_pylist()]
    raise TypeError("unsupported LanceDB table object")
