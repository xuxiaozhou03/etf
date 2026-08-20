"""Model 基类：声明式表结构 + 通用 SQL 生成与写入/读取。

每张表一个模块（本包其他文件），继承本基类并自维护持久化方法。
"""

from __future__ import annotations

import sqlite3
from typing import ClassVar, List, Tuple

import pandas as pd

# 列定义：(列名, SQL 类型, 附加约束)
ColumnDef = Tuple[str, str, str]


class Model:
    table: ClassVar[str] = ""
    columns: ClassVar[List[ColumnDef]] = []
    primary_keys: ClassVar[List[str]] = []

    @classmethod
    def create_sql(cls) -> str:
        """生成 CREATE TABLE IF NOT EXISTS 语句。"""
        parts = [f"{name} {ctype} {constraint}".strip() for name, ctype, constraint in cls.columns]
        if cls.primary_keys:
            parts.append(f"PRIMARY KEY ({', '.join(cls.primary_keys)})")
        return f"CREATE TABLE IF NOT EXISTS {cls.table} ({', '.join(parts)});"

    @classmethod
    def names(cls) -> List[str]:
        """全部列名（按定义顺序）。"""
        return [c[0] for c in cls.columns]

    @classmethod
    def non_key_names(cls) -> List[str]:
        """除主键外的列名（用于 UPDATE 分支）。"""
        return [c[0] for c in cls.columns if c[0] not in cls.primary_keys]

    @classmethod
    def upsert_sql(cls) -> str:
        """生成 INSERT ... ON CONFLICT DO UPDATE 语句。"""
        cols = cls.names()
        placeholders = ",".join(["?"] * len(cols))
        updates = ",".join(f"{c}=excluded.{c}" for c in cls.non_key_names())
        return (
            f"INSERT INTO {cls.table} ({','.join(cols)}) VALUES ({placeholders}) "
            f"ON CONFLICT({', '.join(cls.primary_keys)}) DO UPDATE SET {updates}"
        )

    @classmethod
    def upsert(cls, conn: sqlite3.Connection, df: pd.DataFrame) -> int:
        """通用 upsert：df 列名与模型一致，缺失列自动补空。"""
        if df.empty:
            return 0
        rows = df.copy()
        for col in cls.names():
            if col not in rows.columns:
                rows[col] = None
        cols = cls.names()
        sql = cls.upsert_sql()
        values = [
            tuple(None if pd.isna(v) else v for v in row)
            for row in rows[cols].itertuples(index=False)
        ]
        conn.executemany(sql, values)
        conn.commit()
        return len(rows)

    @classmethod
    def load(cls, conn: sqlite3.Connection) -> pd.DataFrame:
        """读取全表。"""
        return pd.read_sql_query(f"SELECT * FROM {cls.table}", conn)
