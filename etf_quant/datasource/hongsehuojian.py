"""红火箭 ETF 列表/快照数据源。

接口：GET https://hongsehuojian.com/fundex-quote/allPage/findListByEtf
实测：pageSize=2000 一次返回全部约 1640 只；classA 为分类代码。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

log = logging.getLogger(__name__)

LIST_URL = "https://hongsehuojian.com/fundex-quote/allPage/findListByEtf"

# classA 分类代码（实测计数）
CLASS_A = {
    "01": "宽基指数",
    "02": "行业主题",
    "03": "策略指数",
    "04": "增强指数",
    "05": "跨境",
    "06": "商品",
    "07": "债券",
    "08": "货币",
}

# 列表快照字段（保留核心列，其余原始字段保留于 attrs）
SNAPSHOT_COLUMNS = [
    "securityCode", "securityName", "securityFullName", "scale", "amount",
    "price", "changePercent", "premiumRate", "trackingIndex", "trackIndex",
    "managementFee", "escrowFees", "managementcomp", "fundManager", "tradeDate",
    "weeklyPerformance", "monthlyPerformance", "quarterlyPerformance",
    "halfyearPerformance", "ytdPerformance", "yearlyPerformance",
    "threeYearPerformance", "fiveYearPerformance", "inceptionPerformance",
]


def fetch_etf_list(session: Optional[requests.Session] = None) -> pd.DataFrame:
    """全量拉取 ETF 列表快照（pageSize=2000，一次请求）。"""
    import requests
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
    df["tradeDate"] = pd.to_datetime(df["tradeDate"], unit="ms", errors="coerce")
    df["classA"] = [r.get("classA") for r in rows]
    df["classAName"] = df["classA"].map(CLASS_A)
    df.attrs["total"] = total
    df.attrs["raw"] = rows
    return df


def etf_list_summary(df: pd.DataFrame) -> str:
    """生成列表摘要文本（分类计数等）。"""
    lines = [f"ETF 总数: {len(df)}"]
    if "classAName" in df.columns:
        counts = df["classAName"].fillna("未分类").value_counts()
        lines.append("分类计数: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return "\n".join(lines)
