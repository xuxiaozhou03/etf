"""行情路由：ETF 列表 / 详情 / K线。"""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from etf_quant.api.config import DB_PATH
from etf_quant.engine.data import load_adjusted_ohlc
from etf_quant.storage import SQLiteStore

router = APIRouter(prefix="/api/etfs", tags=["market"])


def _clean(v):
    return None if v is None or (isinstance(v, float) and v != v) else v


@router.get("")
def list_etfs(search: str = "", sort: str = "scale", order: str = "desc"):
    """ETF 列表：可搜索（代码/名称），按字段排序，附轻量最新行情。"""
    store = SQLiteStore(DB_PATH)
    try:
        df = store.load_etf_list()
        if search:
            q = search.strip().upper()
            df = df[df["securityName"].astype(str).str.upper().str.contains(q)
                    | df["securityCode"].astype(str).str.upper().str.contains(q)]
        if sort in df.columns:
            df = df.sort_values(sort, ascending=(order != "desc"))
        out = []
        for r in df.to_dict("records"):
            quote = store.latest_quote_fast(r["securityCode"])
            out.append({k: _clean(v) for k, v in r.items()})
            out[-1]["latest"] = quote
        return out
    finally:
        store.close()


@router.get("/{code}")
def get_etf(code: str):
    """单只 ETF：元数据 + 最新行情 + 区间收益 + 数据覆盖。"""
    store = SQLiteStore(DB_PATH)
    try:
        df = store.load_etf_list()
        row = df[df["securityCode"] == code]
        if row.empty:
            raise HTTPException(404, f"未找到标的 {code}")
        meta = {k: _clean(v) for k, v in row.iloc[0].to_dict().items()}
        latest = store.latest_quote_fast(code) or store.latest_quote(code)
        performance = store.period_returns(code)
        kline_count = store.conn.execute(
            "SELECT COUNT(*) FROM daily_kline WHERE code=?", (code,)
        ).fetchone()[0]
        return {
            **meta,
            "latest": {k: _clean(v) for k, v in latest.items()},
            "performance": {k: _clean(v) for k, v in performance.items()},
            "coverage": {"latestDate": store.latest_kline_date(code), "rows": kline_count},
        }
    finally:
        store.close()


@router.get("/{code}/kline")
def get_kline(code: str, ma: str = "5,10,20,60"):
    """前复权日K线 + MA 叠加（供 ECharts 蜡烛图）。

    返回 dates / ohlc[[o,c,l,h]] / volume / ma{"5":[...]}。
    """
    store = SQLiteStore(DB_PATH)
    try:
        df = load_adjusted_ohlc(store, code)
        if df.empty:
            raise HTTPException(404, f"标的 {code} 无日K线数据")
        ma_periods = [int(x) for x in ma.split(",") if x.strip().isdigit()]
        ma_map = {}
        for p in ma_periods:
            ma_map[str(p)] = [None if pd.isna(v) else round(float(v), 4)
                              for v in df["adj_close"].rolling(p).mean()]
        return {
            "code": code,
            "rows": len(df),
            "dates": [str(d.date()) for d in df.index],
            "ohlc": [[round(float(o), 4), round(float(c), 4), round(float(l), 4), round(float(h), 4)]
                     for o, c, l, h in zip(df["adj_open"], df["adj_close"], df["adj_low"], df["adj_high"])],
            "volume": [float(v) for v in df["volume"]],
            "ma": ma_map,
        }
    finally:
        store.close()
