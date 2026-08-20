"""策略注册表：内置策略按名称索引，供 API 与网格批量使用。"""

from __future__ import annotations

from typing import List

from etf_quant.strategies.base import ParamSpec, Strategy
from etf_quant.strategies.ma import DualMA
from etf_quant.strategies.bollinger import Bollinger
from etf_quant.strategies.rsi import RSI
from etf_quant.strategies.buyhold import BuyHold

STRATEGIES = {
    "dual_ma": DualMA,
    "bollinger": Bollinger,
    "rsi": RSI,
    "buy_hold": BuyHold,
}


def get_strategy(name: str):
    """按名称取策略实例（未注册返回 None）。"""
    cls = STRATEGIES.get(name)
    return cls() if cls else None


def list_strategies() -> List[dict]:
    """策略元数据 + 参数 schema（前端表单由此生成）。"""
    out = []
    for name, cls in STRATEGIES.items():
        inst = cls()
        out.append({
            "name": inst.name,
            "displayName": inst.display_name,
            "description": inst.description,
            "params": [p.asdict() for p in inst.params],
        })
    return out


__all__ = ["ParamSpec", "Strategy", "STRATEGIES", "get_strategy", "list_strategies"]
