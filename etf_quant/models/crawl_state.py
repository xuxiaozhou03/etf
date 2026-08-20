"""抓取状态表：schema + 状态写入/读取。"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List

from etf_quant.models.base import ColumnDef, Model


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CrawlState(Model):
    """抓取状态（断点续传）。"""

    table = "crawl_state"
    columns: List[ColumnDef] = [
        ("code", "TEXT", ""),
        ("status", "TEXT", ""),
        ("last_success_at", "TEXT", ""),
        ("last_error", "TEXT", ""),
        ("updated_at", "TEXT", ""),
    ]
    primary_keys: List[str] = ["code"]

    @classmethod
    def mark_success(cls, conn: sqlite3.Connection, code: str) -> None:
        conn.execute(
            f"INSERT INTO {cls.table} (code, status, last_success_at, updated_at) VALUES (?, 'ok', ?, ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='ok', last_success_at=excluded.last_success_at, "
            f"last_error=NULL, updated_at=excluded.updated_at",
            (code, _now(), _now()),
        )
        conn.commit()

    @classmethod
    def mark_error(cls, conn: sqlite3.Connection, code: str, error: str) -> None:
        conn.execute(
            f"INSERT INTO {cls.table} (code, status, last_error, updated_at) VALUES (?, 'error', ?, ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='error', last_error=excluded.last_error, "
            f"updated_at=excluded.updated_at",
            (code, error[:500], _now()),
        )
        conn.commit()

    @classmethod
    def load_status(cls, conn: sqlite3.Connection) -> Dict[str, str]:
        rows = conn.execute(f"SELECT code, status FROM {cls.table}").fetchall()
        return {code: status for code, status in rows}
