"""RSI 择时策略：RSI 低于超卖线买入、高于超买线卖出（Wilder 平滑）。"""

from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd

from etf_quant.strategies.base import ParamSpec, Strategy


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Wilder RSI（ewm alpha=1/window 近似 Wilder 平滑）。"""
    delta = close.diff()
    gain = delta.clip(lower=0.0).ewm(alpha=1.0 / window, adjust=False).mean()
    loss = (-delta.clip(upper=0.0)).ewm(alpha=1.0 / window, adjust=False).mean()
    loss = loss.replace(0.0, np.nan)  # 无下跌 → RSI=100（不触发超卖）
    rs = gain / loss
    return 100.0 - 100.0 / (1.0 + rs)


class RSI(Strategy):
    name = "rsi"
    display_name = "RSI 择时"
    description = "RSI 低于超卖线买入、高于超买线卖出，区间内维持仓位"
    params = [
        ParamSpec("window", "RSI 周期", "int", 14, 2, 100, 1, "RSI 计算窗口"),
        ParamSpec("buy", "超卖线", "float", 30.0, 5.0, 50.0, 1.0, "低于此线买入"),
        ParamSpec("sell", "超买线", "float", 70.0, 50.0, 95.0, 1.0, "高于此线卖出"),
    ]

    def generate_signals(self, df: pd.DataFrame, **params) -> pd.Series:
        p = self.normalize(params)
        rsi = compute_rsi(df["adj_close"], int(p["window"]))
        sig = pd.Series(np.nan, index=df.index)
        sig[rsi < p["buy"]] = 1.0
        sig[rsi > p["sell"]] = 0.0
        return sig.ffill().fillna(0.0)
