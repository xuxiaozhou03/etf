"""流通份额表：schema + 读写。"""

from __future__ import annotations

import sqlite3
from typing import List

from etf_quant.models.base import ColumnDef, Model


class FloatShare(Model):
    """流通份额（芝士财富 floatShares，[[date_int, shares], ...]，按日记录）。"""

    table = "float_shares"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("shares", "REAL", ""),
    ]
    primary_keys: List[str] = ["code", "date"]

    @classmethod
    def upsert(cls, conn: sqlite3.Connection, code: str, shares: List[List]) -> int:
        """写入流通份额（shares: [[date_int, shares], ...]）。"""
        if not shares:
            return 0
        sql = cls.upsert_sql()
        values = [(code, str(s[0]), float(s[1])) for s in shares]
        conn.executemany(sql, values)
        conn.commit()
        return len(values)

    @classmethod
    def load(cls, conn: sqlite3.Connection, code: str) -> List[List]:
        """流通份额 [[date_int, shares], ...]，按日期升序。"""
        rows = conn.execute(
            f"SELECT date, shares FROM {cls.table} WHERE code=? ORDER BY date", (code,)
        ).fetchall()
        return [[r[0], r[1]] for r in rows]
