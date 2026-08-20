"""ETF 列表数据源（红火箭 hongsehuojian.com）。

接口：GET https://hongsehuojian.com/fundex-quote/allPage/findListByEtf
实测：pageSize=2000 一次返回全部约 1640 只。
仅保留元数据字段；行情与业绩指标由日K线实时推导（见 storage）。
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import requests

log = logging.getLogger(__name__)

LIST_URL = "https://hongsehuojian.com/fundex-quote/allPage/findListByEtf"

# 落库字段（仅元数据；行情/业绩指标由日K线实时推导，不在此列）
SNAPSHOT_COLUMNS = [
    "securityCode", "securityName", "scale", "premiumRate",
    "trackingIndex", "trackIndex",
]


def fetch_etf_list(session: Optional[requests.Session] = None) -> pd.DataFrame:
    """全量拉取 ETF 列表快照（pageSize=2000，一次请求）。"""
    sess = session or requests.Session()
    params = {
        "classA": "", "classB": "",
        "orderBy": "l.scale", "order": "desc",
        "pageSize": 2000, "pageNo": 1,
    }
    resp = sess.get(LIST_URL, params=params, timeout=30)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code") != "200":
        raise RuntimeError(f"findListByEtf 失败: {body.get('code')} {body.get('msg')}")
    data = body["data"]
    rows = data.get("data") or []
    total = data.get("total")
    if len(rows) < (total or 0):
        log.warning("列表不完整：total=%s 实返=%s", total, len(rows))
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for col in SNAPSHOT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[SNAPSHOT_COLUMNS]
    df.attrs["total"] = total
    df.attrs["raw"] = rows
    return df


def etf_list_summary(df: pd.DataFrame) -> str:
    """生成列表摘要文本。"""
    return f"ETF 总数: {len(df)}"
