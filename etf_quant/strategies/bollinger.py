"""布林带均值回归策略：收盘跌破下轨买入，涨破上轨卖出，带内维持仓位。"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from etf_quant.strategies.base import ParamSpec, Strategy


class Bollinger(Strategy):
    name = "bollinger"
    display_name = "布林带反转"
    description = "收盘跌破下轨买入、涨破上轨卖出，带内维持原仓位（均值回归）"
    params = [
        ParamSpec("window", "窗口周期", "int", 20, 2, 250, 1, "中轨 MA 与标准差窗口"),
        ParamSpec("k", "标准差倍数", "float", 2.0, 0.5, 5.0, 0.1, "上下轨带宽（倍σ）"),
    ]

    def generate_signals(self, df: pd.DataFrame, **params) -> pd.Series:
        p = self.normalize(params)
        close = df["adj_close"]
        mid = close.rolling(int(p["window"])).mean()
        std = close.rolling(int(p["window"])).std()
        upper = mid + p["k"] * std
        lower = mid - p["k"] * std
        sig = pd.Series(np.nan, index=df.index)
        sig[close < lower] = 1.0
        sig[close > upper] = 0.0
        return sig.ffill().fillna(0.0)
