"""抓取状态表：schema + 状态写入/读取。

记录每只 ETF 最近一次抓取任务的完成时间与状态：
- status 区分成功（ok）/ 失败（error）；
- last_run_at 为该次任务的完成时间（成败均记），供重跑判定使用——
  失败直接重跑；成功则按该时间对比最近一个 A 股交易日收盘时刻判断是否过期。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Dict, List, Optional

from etf_quant.models.base import ColumnDef, Model


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class CrawlState(Model):
    """抓取状态（断点续传）。"""

    table = "crawl_state"
    columns: List[ColumnDef] = [
        ("code", "TEXT", ""),
        ("status", "TEXT", ""),
        ("last_run_at", "TEXT", ""),
    ]
    primary_keys: List[str] = ["code"]

    @classmethod
    def mark_success(cls, conn: sqlite3.Connection, code: str) -> None:
        conn.execute(
            f"INSERT INTO {cls.table} (code, status, last_run_at) VALUES (?, 'ok', ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='ok', last_run_at=excluded.last_run_at",
            (code, _now()),
        )
        conn.commit()

    @classmethod
    def mark_error(cls, conn: sqlite3.Connection, code: str) -> None:
        conn.execute(
            f"INSERT INTO {cls.table} (code, status, last_run_at) VALUES (?, 'error', ?) "
            f"ON CONFLICT(code) DO UPDATE SET status='error', last_run_at=excluded.last_run_at",
            (code, _now()),
        )
        conn.commit()

    @classmethod
    def load_state(cls, conn: sqlite3.Connection) -> Dict[str, Dict[str, Optional[str]]]:
        rows = conn.execute(f"SELECT code, status, last_run_at FROM {cls.table}").fetchall()
        return {code: {"status": status, "last_run_at": last_run_at} for code, status, last_run_at in rows}
