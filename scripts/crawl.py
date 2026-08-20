#!/usr/bin/env python3
"""ETF 数据爬虫：红火箭 ETF 列表 + 芝士财富日K线，落 SQLite。

用法：
  python scripts/crawl.py --limit 10          # 试跑：只抓前 10 只
  python scripts/crawl.py                     # 全量抓取（增量，已成功的跳过）
  python scripts/crawl.py --force             # 强制重抓已成功的标的
  python scripts/crawl.py --codes 510300.SH,159915.SZ
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etf_quant.datasource.cheesefortune import CheeseFortuneClient, normalize_code
from etf_quant.datasource.etf_list import fetch_etf_list, etf_list_summary
from etf_quant.storage import SQLiteStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("crawl")


def crawl_kline(store: SQLiteStore, client: CheeseFortuneClient, code: str,
                force: bool, delay: float) -> None:
    """抓取单只 ETF 日K线并落库。"""
    state = store.load_state()
    latest = store.latest_kline_date(code)
    if not force and state.get(code) == "ok" and latest:
        return  # 增量跳过

    norm = normalize_code(code)
    for attempt in range(3):
        try:
            df = client.fetch_daily(norm)
            if df.empty:
                raise RuntimeError("返回空数据")
            df = df.copy()
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")
            factors = df.attrs.get("factors") or []
            n = store.upsert_kline(code, df)
            nf = store.upsert_factors(code, factors)
            store.mark_success(code)
            log.info("OK %s rows=%d factors=%d latest=%s", code, n, nf, df["date"].iloc[-1])
            return
        except Exception as exc:  # noqa: BLE001
            wait = 2 ** attempt
            if attempt < 2:
                log.warning("%s 失败(%s)，%.0fs 后重试", code, exc, wait)
                time.sleep(wait)
            else:
                store.mark_error(code, str(exc))
                log.error("FAIL %s: %s", code, exc)
    time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser(description="ETF 数据爬虫")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parent.parent / "data" / "etf.db"))
    parser.add_argument("--limit", type=int, default=0, help="只抓前 N 只（0=全部）")
    parser.add_argument("--force", action="store_true", help="强制重抓已成功标的")
    parser.add_argument("--delay", type=float, default=0.3, help="请求间隔（秒）")
    parser.add_argument("--list-only", action="store_true", help="只抓 ETF 列表")
    parser.add_argument("--no-list", action="store_true", help="跳过列表抓取")
    parser.add_argument("--codes", default="", help="指定代码列表，逗号分隔")
    args = parser.parse_args()

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteStore(args.db)
    client = CheeseFortuneClient()

    try:
        if not args.no_list:
            log.info("抓取 ETF 列表 ...")
            df = fetch_etf_list()
            store.upsert_etf_list(df)
            log.info("列表保存完成：%s", etf_list_summary(df).replace("\n", "；"))
            if args.list_only:
                return 0

        if args.codes:
            codes = [c.strip() for c in args.codes.split(",") if c.strip()]
        else:
            etf = store.load_etf_list()
            if etf.empty:
                log.error("ETF 列表为空，先运行 --list-only 或去掉 --no-list")
                return 1
            codes = etf["securityCode"].tolist()
            if args.limit:
                codes = codes[: args.limit]

        log.info("开始抓取日K线，共 %d 只（delay=%.1fs）", len(codes), args.delay)
        ok = 0
        for i, code in enumerate(codes, 1):
            before = store.stats()
            crawl_kline(store, client, code, args.force, args.delay)
            after = store.stats()
            if after["kline_rows"] > before["kline_rows"]:
                ok += 1
            if i % 50 == 0 or i == len(codes):
                s = store.stats()
                log.info("进度 %d/%d，K线行数=%d，成功=%d 失败=%d",
                         i, len(codes), s["kline_rows"], s["ok"], s["error"])

        stats = store.stats()
        log.info("完成：ETF=%d K线行数=%d 覆盖标的=%d 成功=%d 失败=%d",
                 stats["etf_count"], stats["kline_rows"], stats["kline_codes"],
                 stats["ok"], stats["error"])
        return 0
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
