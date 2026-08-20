"""数据路由：覆盖统计 + 一键更新任务。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from etf_quant.api.config import DB_PATH
from etf_quant.api.services.crawl_service import get_task, start_crawl
from etf_quant.storage import SQLiteStore

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/stats")
def stats():
    """数据覆盖统计 + 每标的覆盖明细。"""
    store = SQLiteStore(DB_PATH)
    try:
        s = store.stats()
        etf = store.load_etf_list()
        name_map = dict(zip(etf["securityCode"], etf["securityName"]))
        coverage = []
        for code, cnt, start, end in store.conn.execute(
            "SELECT code, COUNT(*), MIN(date), MAX(date) FROM daily_kline GROUP BY code"
        ).fetchall():
            state = store.load_state().get(code) or {}
            coverage.append({
                "code": code, "name": name_map.get(code),
                "rows": cnt, "start": _str_or_none(start), "end": _str_or_none(end),
                "status": state.get("status"),
                "lastRunAt": state.get("last_run_at"),
            })
        return {
            "etfCount": s["etf_count"], "klineRows": s["kline_rows"],
            "klineCodes": s["kline_codes"], "ok": s["ok"], "error": s["error"],
            "coverage": coverage,
        }
    finally:
        store.close()


@router.post("/update")
def update(limit: int = 0, delay: float = 0.3):
    """启动后台数据更新任务（已有运行中任务则复用），返回 taskId。"""
    return {"taskId": start_crawl(DB_PATH, limit=limit, delay=delay)}


@router.get("/update/{task_id}")
def update_status(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")
    return task


def _str_or_none(v):
    return str(v) if v is not None else None
