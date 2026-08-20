"""双均线交叉策略：快线上穿慢线买入（金叉），下穿卖出（死叉）。"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from etf_quant.strategies.base import ParamSpec, Strategy


class DualMA(Strategy):
    name = "dual_ma"
    display_name = "双均线交叉"
    description = "快线上穿慢线买入（金叉）、下穿卖出（死叉），趋势跟踪"
    params = [
        ParamSpec("fast", "快线周期", "int", 5, 1, 250, 1, "快线 MA 周期"),
        ParamSpec("slow", "慢线周期", "int", 20, 2, 500, 1, "慢线 MA 周期"),
    ]

    def generate_signals(self, df: pd.DataFrame, **params) -> pd.Series:
        p = self.normalize(params)
        fast = df["adj_close"].rolling(int(p["fast"])).mean()
        slow = df["adj_close"].rolling(int(p["slow"])).mean()
        return (fast > slow).astype(int)
