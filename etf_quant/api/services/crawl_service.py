"""后台数据更新任务：线程内自开 SQLite 连接，单实例锁，进度可轮询。

复用 datasource/kline 的抓取逻辑；增量跳过规则对齐 scripts/crawl.py：
失败重抓，成功且 last_run_at 晚于最近 A 股交易日收盘则跳过。
"""

from __future__ import annotations

import datetime as dt
import logging
import threading
import time
import uuid
from typing import Dict, Optional

from etf_quant.datasource.kline import KlineClient, normalize_code
from etf_quant.storage import SQLiteStore

log = logging.getLogger(__name__)

TZ_CN = dt.timezone(dt.timedelta(hours=8))


def _last_trading_close_utc() -> dt.datetime:
    """最近一个 A 股交易日收盘时刻（北京 15:00）对应的 UTC 时间。"""
    now = dt.datetime.now(TZ_CN)
    day = now - dt.timedelta(days=1) if now.time() < dt.time(15, 0) else now
    while day.weekday() >= 5:
        day -= dt.timedelta(days=1)
    return day.replace(hour=15, minute=0, second=0, microsecond=0).astimezone(dt.timezone.utc)


def _needs_rerun(state: Optional[Dict]) -> bool:
    if not state or state.get("status") != "ok" or not state.get("last_run_at"):
        return True
    last = dt.datetime.fromisoformat(state["last_run_at"])
    if last.tzinfo is None:
        last = last.replace(tzinfo=dt.timezone.utc)
    return last < _last_trading_close_utc()


_TASKS: Dict[str, dict] = {}
_LOCK = threading.Lock()


def start_crawl(db_path: str, limit: int = 0, delay: float = 0.3) -> str:
    """启动后台数据更新任务，返回 taskId（已有运行中任务则复用）。"""
    with _LOCK:
        for t in _TASKS.values():
            if t["status"] == "running":
                return t["taskId"]
        task_id = uuid.uuid4().hex[:8]
        task = {
            "taskId": task_id, "status": "running", "total": 0, "done": 0,
            "current": "", "message": "启动中", "ok": 0, "error": 0,
        }
        _TASKS[task_id] = task
        threading.Thread(target=_run_crawl, args=(db_path, task, limit, delay),
                         daemon=True).start()
        return task_id


def get_task(task_id: str) -> Optional[dict]:
    return _TASKS.get(task_id)


def _run_crawl(db_path: str, task: dict, limit: int, delay: float) -> None:
    store = SQLiteStore(db_path)  # 线程内自开连接
    client = KlineClient()
    try:
        etf = store.load_etf_list()
        if etf.empty:
            task["status"] = "error"
            task["message"] = "ETF 列表为空，请先抓取列表"
            return
        codes = etf["securityCode"].tolist()
        if limit:
            codes = codes[: limit]
        task["total"] = len(codes)
        state = store.load_state()
        ok = error = 0
        for i, code in enumerate(codes, 1):
            task["current"] = code
            if _needs_rerun(state.get(code)):
                try:
                    df = client.fetch_daily(normalize_code(code))
                    if df.empty:
                        raise RuntimeError("返回空数据")
                    df = df.copy()
                    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
                    store.upsert_kline(code, df)
                    store.upsert_factors(code, df.attrs.get("factors") or [])
                    store.upsert_float_shares(code, df.attrs.get("float_shares") or [])
                    store.mark_success(code)
                    ok += 1
                except Exception as exc:  # noqa: BLE001
                    store.mark_error(code)
                    error += 1
                    log.warning("更新失败 %s: %s", code, exc)
                time.sleep(delay)
            task["done"] = i
            task["ok"], task["error"] = ok, error
            if i % 10 == 0 or i == len(codes):
                task["message"] = f"进度 {i}/{len(codes)}：成功 {ok}，失败 {error}"
        task["message"] = f"完成：共 {len(codes)} 只，成功 {ok}，失败 {error}"
    except Exception as exc:  # noqa: BLE001
        task["status"] = "error"
        task["message"] = f"任务异常：{exc}"
    else:
        task["status"] = "done"
    finally:
        store.close()
