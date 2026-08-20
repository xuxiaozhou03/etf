#!/usr/bin/env python3
"""数据落库校验：统计 + 字段约束检查（纯本地，无需网络）。

用法：
  python scripts/verify.py                     # 全库统计 + 抽样校验
  python scripts/verify.py --code 510300.SH    # 校验指定标的
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from etf_quant.storage import SQLiteStore

# 校验目标：每行 high>=max(open,close)、low<=min(open,close)、prev_close=前日close
PRICE_COLS = ("open", "close", "high", "low", "prev_close")


def check_code(store: SQLiteStore, code: str) -> None:
    df = store.load_kline(code)
    if df.empty:
        print(f"{code}: 无数据")
        return
    bad_high = (df["high"] < df[["open", "close"]].max(axis=1)).sum()
    bad_low = (df["low"] > df[["open", "close"]].min(axis=1)).sum()
    prev_mismatch = (df["prev_close"] != df["close"].shift(1)).sum() - (df["prev_close"].iloc[0] != df["close"].iloc[0])
    print(
        f"{code}: {len(df)} 行 ({df['date'].min()} ~ {df['date'].max()}) "
        f"high越界={bad_high} low越界={bad_low} prev_close不连续={prev_mismatch}"
    )
    if bad_high or bad_low or prev_mismatch:
        print(f"  !! {code} 校验失败，请检查数据")


def main() -> int:
    parser = argparse.ArgumentParser(description="ETF 数据校验")
    parser.add_argument("--db", default=str(Path(__file__).resolve().parent.parent / "data" / "etf.db"))
    parser.add_argument("--code", default="", help="只校验指定代码（如 510300.SH）")
    parser.add_argument("--sample", type=int, default=10, help="无 --code 时随机抽样的标的数")
    args = parser.parse_args()

    store = SQLiteStore(args.db)
    stats = store.stats()
    print(f"统计: ETF={stats['etf_count']} K线行数={stats['kline_rows']} 覆盖标的={stats['kline_codes']} "
          f"成功={stats['ok']} 失败={stats['error']}")

    if args.code:
        check_code(store, args.code)
    else:
        codes = store.load_etf_list()["securityCode"].tolist()
        import random
        for code in random.sample(codes, min(args.sample, len(codes))):
            check_code(store, code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
