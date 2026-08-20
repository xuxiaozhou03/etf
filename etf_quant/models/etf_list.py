"""ETF 元数据表：schema + 读写。"""

from __future__ import annotations

from typing import List

from etf_quant.models.base import ColumnDef, Model


class EtfList(Model):
    """ETF 元数据（红火箭列表接口）。

    价格/成交额/涨跌幅/区间业绩等行情与收益指标不落库，
    由 DailyKline 查询时从日K线实时推导。
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
    primary_keys: List[str] = ["securityCode"]
