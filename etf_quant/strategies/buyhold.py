"""买入持有策略：全程满仓（基准对照）。"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from etf_quant.strategies.base import ParamSpec, Strategy


class BuyHold(Strategy):
    name = "buy_hold"
    display_name = "买入持有"
    description = "全程满仓持有，作为基准对照"
    params = []

    def generate_signals(self, df: pd.DataFrame, **params) -> pd.Series:
        return pd.Series(1.0, index=df.index)
