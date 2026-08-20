#!/usr/bin/env python3
"""回测引擎正确性自检（纯本地，无需网络）。

用例：
  1. 不变式：全仓零成本 → 净值精确等于买持基准，totalReturn == adj_close[-1]/adj_close[0]-1
  2. 双均线手算对照：首个金叉日 T → position 在 T+1 置 1、首笔买入执行于 adj_open[T+1]
  3. 交易计数一致性：round-trip 数 == 持仓翻转次数 / 2
  4. 2015 股灾最大回撤窗口
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from etf_quant.engine.backtest import BacktestConfig, run_backtest
from etf_quant.engine.data import load_adjusted_ohlc
from etf_quant.storage import SQLiteStore

FAILED = []


def check(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILED.append(name)


def main() -> int:
    store = SQLiteStore(str(Path(__file__).resolve().parent.parent / "data" / "etf.db"))
    code = "510300.SH"
    df = load_adjusted_ohlc(store, code)
    assert len(df) > 3000, f"{code} 数据不足，先运行 scripts/crawl.py"

    # ---- 1. 不变式：全仓零成本 == 买持基准 ----
    # 信号次日生效：target 恒 1 → pos = shift(1) 为 [0,1,1,...]，
    # 第 1 根起持仓完整吃到收益（day-1 由 target[0] 决定），
    # 故 nav 精确等于 adj_close[-1]/adj_close[0]（完整买持）。
    signals = pd.Series(1.0, index=df.index)
    config = BacktestConfig(commission_rate=0.0, slippage=0.0, min_commission=0.0)
    res = run_backtest(df, signals, config, bench_adj_close=df["adj_close"])
    nav, metrics = res["nav"], res["metrics"]
    bench_expected = df["adj_close"].iloc[-1] / df["adj_close"].iloc[0]
    check("不变式 nav==基准(1e-9)", abs(nav.iloc[-1] - bench_expected) < 1e-9,
          f"nav={nav.iloc[-1]:.9f} expected={bench_expected:.9f}")
    # totalReturn 在指标层 round 到 4 位小数（展示口径），容差放宽到 1e-4
    check("totalReturn 与 adj 一致", abs(metrics["totalReturn"] - (bench_expected - 1)) < 1e-4)
    check("全仓零成本换手=0", metrics["annualTurnover"] == 0)

    # ---- 2. 双均线手算对照（MA5/MA20，前 60 行窗口）----
    from etf_quant.strategies import get_strategy
    dual_ma = get_strategy("dual_ma")
    assert dual_ma is not None
    sub = df.iloc[:60]
    ma5 = sub["adj_close"].rolling(5).mean()
    ma20 = sub["adj_close"].rolling(20).mean()
    golden = (ma5 > ma20).astype(int)
    # 首个金叉日：出现 ma5>ma20 的第一天
    cross_up_day = golden[golden == 1].index[0]
    cross_up_pos = sub.index.get_loc(cross_up_day)
    # 信号于 T 收盘生成，T+1 生效
    golden_full = dual_ma.generate_signals(df, fast=5, slow=20)
    check("策略信号与手算一致", (golden_full.iloc[:60] == golden).all())
    res2 = run_backtest(df, golden_full, config, bench_adj_close=df["adj_close"])
    pos = res2["position"]
    t_plus1 = sub.index[cross_up_pos + 1]
    check("金叉次日持仓=1", float(pos.loc[t_plus1]) == 1.0,
          f"T={cross_up_day.date()} T+1={t_plus1.date()}")
    trades = res2["trades"]
    check("首笔买入执行于金叉次日", trades and trades[0]["buyDate"] == str(t_plus1.date()),
          f"first buy={trades[0]['buyDate'] if trades else None} expected={t_plus1.date()}")
    check("首笔买入价==次日 adj_open", trades and abs(trades[0]["buyPrice"] - round(df["adj_open"].loc[t_plus1], 4)) < 1e-6)

    # ---- 3. 交易计数一致性 ----
    flips = int((pos.diff().abs() > 0).sum())
    closed_trades = len([t for t in trades if t["sellDate"]])
    # 每笔 round-trip = 买入+卖出两次翻转；末尾未平仓的开仓会多 1 次翻转
    expected = (flips - (1 if float(pos.iloc[-1]) > 0 else 0)) // 2
    check("round-trip 数一致", closed_trades == expected,
          f"trades={closed_trades} flips={flips} expected={expected}")

    # ---- 4. 2015 股灾最大回撤窗口 ----
    mdd = metrics["maxDrawdown"]
    check("2015 股灾回撤 > 30%", mdd < -0.30, f"maxDrawdown={mdd}")
    check("回撤峰值/谷底落在 2015", "2015" in metrics["maxDrawdownPeak"] or "2015" in metrics["maxDrawdownTrough"],
          f"peak={metrics['maxDrawdownPeak']} trough={metrics['maxDrawdownTrough']}")

    # ---- 5. 全部内置策略可跑通且无异常 ----
    for name in ("dual_ma", "bollinger", "rsi", "buy_hold"):
        strat = get_strategy(name)
        sig = strat.generate_signals(df, **{p.name: p.default for p in strat.params})
        r = run_backtest(df, sig, config, bench_adj_close=df["adj_close"])
        check(f"策略 {name} 可回测", r["nav"].notna().all() and len(r["nav"]) == len(df),
              f"nav 尾值={r['nav'].iloc[-1]:.4f} trades={r['metrics']['tradeCount']}")

    store.close()
    print()
    if FAILED:
        print(f"自检失败：{len(FAILED)} 项 -> {FAILED}")
        return 1
    print("回测引擎自检全部通过 ✔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
