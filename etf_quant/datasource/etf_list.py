"""ETF 列表数据源（红火箭 hongsehuojian.com）。

接口：GET https://hongsehuojian.com/fundex-quote/allPage/findListByEtf
实测：pageSize=2000 一次返回全部约 1640 只。

插入数据库前按前端 selectRepresentativeEtfs 规则精选：
  排除货币市场/债券/黑名单 ETF；只留规模超 3 亿元、有跟踪指数的标的，
  每个跟踪指数取规模最大的一只。
ETF 全名（securityFullName）仅用于内存过滤，不落库。
仅保留元数据字段；行情与业绩指标由日K线实时推导（见 storage）。
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional

import pandas as pd
import requests

log = logging.getLogger(__name__)

LIST_URL = "https://hongsehuojian.com/fundex-quote/allPage/findListByEtf"

# 落库字段（仅元数据；全名与行情/业绩指标不落库）
SNAPSHOT_COLUMNS = [
    "securityCode", "securityName", "scale", "premiumRate",
    "trackingIndex", "trackIndex",
]

# ---- 精选规则（对齐前端 selectRepresentativeEtfs）----

MIN_SCALE = 300_000_000  # 规模下限（元）：仅保留超 3 亿元的 ETF
EXCLUDED_ETF_NAMES = {"华宝添益ETF"}  # 明确不需要抓取详情的标的
_NAME_EXCLUDE_RE = re.compile(r"货币ETF|日利ETF|债|短融")
_FULLNAME_EXCLUDE_RE = re.compile(r"货币市场|债券")


def _scale_num(value) -> float:
    """scale 转数值；缺失/非法/NaN 按 -inf（对齐 JS `scale ?? -Infinity`）。"""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return float("-inf")
    return v if v == v else float("-inf")  # NaN → -inf


def _is_excluded_row(row: Dict) -> bool:
    """排除货币市场、债券类和明确不需要抓取详情的 ETF。"""
    name = str(row.get("securityName") or "")
    full_name = str(row.get("securityFullName") or "")
    return (
        name in EXCLUDED_ETF_NAMES
        or bool(_NAME_EXCLUDE_RE.search(name))
        or bool(_FULLNAME_EXCLUDE_RE.search(full_name))
    )


def select_representative_etfs(rows: List[Dict]) -> pd.DataFrame:
    """从原始行中精选代表标的（插入数据库前过滤）。

    跳过：无跟踪指数 / 规模缺失或 <= MIN_SCALE / 名称或全名命中排除规则；
    每个 trackIndex（trim 后）仅保留 scale 最大的一只，并列保留先出现者。
    返回 df 只含 SNAPSHOT_COLUMNS 列。
    """
    best: Dict[str, Dict] = {}
    for row in rows:
        idx = str(row.get("trackIndex") or "").strip()
        if not idx:
            continue
        if _scale_num(row.get("scale")) <= MIN_SCALE:
            continue
        if _is_excluded_row(row):
            continue
        row = {**row, "trackIndex": idx}
        cur = best.get(idx)
        if cur is None or _scale_num(row["scale"]) > _scale_num(cur["scale"]):
            best[idx] = row
    out = pd.DataFrame(best.values())
    if out.empty:
        return out
    for col in SNAPSHOT_COLUMNS:
        if col not in out.columns:
            out[col] = None
    return out[SNAPSHOT_COLUMNS]


def fetch_etf_list(session: Optional[requests.Session] = None) -> pd.DataFrame:
    """全量拉取 ETF 列表快照并精选代表标的（插入数据库前过滤）。

    返回 df 仅含：规模 > 3 亿、有跟踪指数、非货币/债券类、且每个跟踪
    指数规模最大的一只。原始全量数据保留在 attrs（raw_total / raw）。
    """
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
    selected = select_representative_etfs(rows)
    selected.attrs["raw_total"] = total
    selected.attrs["raw"] = rows
    log.info("列表精选：原始 %s 只 → 代表标的 %s 只", len(rows), len(selected))
    return selected


def etf_list_summary(df: pd.DataFrame) -> str:
    """生成列表摘要文本。"""
    raw = df.attrs.get("raw_total")
    if raw:
        return f"ETF 原始 {raw} 只，精选 {len(df)} 只"
    return f"ETF 精选 {len(df)} 只"
