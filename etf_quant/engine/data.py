"""回测数据准备：完整前复权 OHLC 加载 + 涨跌停限制推导与开盘封板标记。"""

from __future__ import annotations

import pandas as pd

from etf_quant.storage import SQLiteStore

# 无涨跌停的 ETF 名称关键词（商品 / 债券 / 货币类）
_NO_LIMIT_KEYWORDS = ("黄金", "货币", "债", "商品", "豆粕", "原油", "油气")
# 20% 涨跌停的 ETF 名称关键词（科创 / 创业板联动）
_PCT20_KEYWORDS = ("科创", "双创", "创业")


def load_adjusted_ohlc(store: SQLiteStore, code: str) -> pd.DataFrame:
    """加载完整前复权 OHLC，date 转为索引，补 ret 列（供策略与引擎共用）。"""
    df = store.load_adjusted_ohlc(code)
    if df.empty:
        return df
    df = df.set_index("date")
    df["ret"] = df["adj_close"].pct_change()
    return df


def default_limit_pct(name: str) -> float:
    """按 ETF 名称推导涨跌停限制：商品/债券/货币类 0，科创/创业联动 20%，其余 10%。"""
    if not name:
        return 0.10
    if any(kw in name for kw in _NO_LIMIT_KEYWORDS):
        return 0.0
    if any(kw in name for kw in _PCT20_KEYWORDS):
        return 0.20
    return 0.10


def limit_flags(df: pd.DataFrame, limit_pct: float):
    """开盘封板标记（用原始 open/prev_close 判定）。

    返回 (is_limit_up, is_limit_down)：开盘即封涨停不可买、开盘即封跌停不可卖。
    limit_pct=0 时全为 False（无涨跌停）。
    """
    if limit_pct <= 0:
        n = len(df)
        return pd.Series(False, index=df.index), pd.Series(False, index=df.index)
    up = df["open"] >= df["prev_close"] * (1 + limit_pct)
    down = df["open"] <= df["prev_close"] * (1 - limit_pct)
    return up.fillna(False), down.fillna(False)
