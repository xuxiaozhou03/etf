"""参数网格批量回测：同一标的、同一策略，多参数组合对比。"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd

from etf_quant.engine.backtest import BacktestConfig, run_backtest

# 网格结果保留的指标字段（对比表 + 热力图用）
METRIC_FIELDS = [
    "totalReturn", "annualReturn", "annualVol", "maxDrawdown", "sharpe",
    "sortino", "calmar", "winRate", "profitLossRatio", "tradeCount",
    "annualTurnover", "alpha", "beta", "infoRatio",
]


def run_grid(df: pd.DataFrame, strategy_inst, combos: List[dict],
             config: BacktestConfig, bench_adj_close: Optional[pd.Series] = None,
             sort_by: str = "annualReturn", limit: int = 500) -> List[dict]:
    """批量回测：df 只加载一次，逐组合生成信号并回测，取指标子集。

    返回按 sort_by 降序排列（None 值排末位）的指标行列表。
    """
    results: List[dict] = []
    for combo in combos:
        sig = strategy_inst.generate_signals(df, **combo)
        res = run_backtest(df, sig, config, bench_adj_close=bench_adj_close)
        m = res["metrics"]
        row = dict(combo)
        for f in METRIC_FIELDS:
            row[f] = m.get(f)
        results.append(row)

    def key(row: dict):
        v = row.get(sort_by)
        return (v is None, v if v is not None else 0.0)

    results.sort(key=key, reverse=True)
    return results[:limit]
