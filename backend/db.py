from __future__ import annotations
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

import duckdb

_DB_PATH = Path(__file__).parent.parent / "macro_terminal.duckdb"
_con: duckdb.DuckDBPyConnection | None = None
_lock = threading.Lock()


def _con_get() -> duckdb.DuckDBPyConnection:
    global _con
    if _con is None:
        _con = duckdb.connect(str(_DB_PATH))
        _con.execute("""
            CREATE TABLE IF NOT EXISTS series_cache (
                series_id TEXT PRIMARY KEY,
                data      TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )
        """)
    return _con


def get_cached(series_id: str, max_age_hours: float = 6.0) -> list[dict] | None:
    with _lock:
        try:
            row = _con_get().execute(
                "SELECT data, fetched_at FROM series_cache WHERE series_id = ?",
                [series_id],
            ).fetchone()
        except Exception:
            return None
        if row is None:
            return None
        data_json, fetched_str = row
        fetched_at = datetime.fromisoformat(fetched_str)
        age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
        if age > max_age_hours * 3600:
            return None
        return json.loads(data_json)


def set_cached(series_id: str, data: list[dict]) -> None:
    with _lock:
        try:
            now = datetime.now(timezone.utc).isoformat()
            _con_get().execute(
                "INSERT OR REPLACE INTO series_cache VALUES (?, ?, ?)",
                [series_id, json.dumps(data), now],
            )
        except Exception:
            pass
