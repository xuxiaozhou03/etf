"""数据模型：SQLite 表结构的单一来源，与数据库一一对应。

每个模型类定义一张表（表名 + 列定义 + 主键），
storage.py 据此生成建表语句与读写 SQL。
"""

from __future__ import annotations

from typing import ClassVar, List, Tuple

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


class EtfList(Model):
    """ETF 元数据（红火箭列表接口）。

    价格/成交额/涨跌幅/区间业绩等行情与收益指标不再落库，
    由 storage 查询时从 daily_kline + adjust_factors 实时推导。
    """

    table = "etf_list"
    columns: List[ColumnDef] = [
        ("securityCode", "TEXT", ""),
        ("securityName", "TEXT", ""),
        ("scale", "REAL", ""),
        ("premiumRate", "REAL", ""),
        ("trackingIndex", "TEXT", ""),
        ("trackIndex", "TEXT", ""),
    ]
    primary_keys: ClassVar[List[str]] = ["securityCode"]


class DailyKline(Model):
    """日K线（芝士财富 dayKV2，字段顺序 [date, prev_close, open, high, low, close, volume, amount]）。"""

    table = "daily_kline"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("open", "REAL", ""),
        ("close", "REAL", ""),
        ("high", "REAL", ""),
        ("low", "REAL", ""),
        ("prev_close", "REAL", ""),
        ("volume", "REAL", ""),
        ("amount", "REAL", ""),
    ]
    primary_keys: ClassVar[List[str]] = ["code", "date"]


class AdjustFactor(Model):
    """复权因子（分红日记录，date 为 YYYYMMDD 整数格式）。"""

    table = "adjust_factors"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("factor", "REAL", ""),
    ]
    primary_keys: ClassVar[List[str]] = ["code", "date"]


class FloatShare(Model):
    """流通份额（芝士财富 floatShares，[[date_int, shares], ...]，按日记录）。"""

    table = "float_shares"
    columns: List[ColumnDef] = [
        ("code", "TEXT", "NOT NULL"),
        ("date", "TEXT", "NOT NULL"),
        ("shares", "REAL", ""),
    ]
    primary_keys: ClassVar[List[str]] = ["code", "date"]


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
    primary_keys: ClassVar[List[str]] = ["code"]


ALL_MODELS: List[type] = [EtfList, DailyKline, AdjustFactor, FloatShare, CrawlState]
