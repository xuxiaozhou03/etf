"""策略接口：ParamSpec（参数 schema）与 Strategy 基类。

策略输入 load_adjusted_ohlc 输出的 df（date 索引，含 adj_close），
输出 target position Series（0/1，与 df 索引对齐）。引擎负责时序（次日生效）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class ParamSpec:
    """策略参数声明，用于前端表单渲染与服务端参数归一化。"""
    name: str
    label: str
    ptype: str = "int"            # 'int' | 'float'
    default: Any = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    description: str = ""

    def asdict(self) -> Dict:
        return {
            "name": self.name, "label": self.label, "ptype": self.ptype,
            "default": self.default, "min": self.min, "max": self.max,
            "step": self.step, "description": self.description,
        }


class Strategy:
    name: str = ""
    display_name: str = ""
    description: str = ""
    params: List[ParamSpec] = field(default_factory=list)

    def generate_signals(self, df: pd.DataFrame, **params) -> pd.Series:
        """生成 target position（0/1），与 df.index 对齐。"""
        raise NotImplementedError

    def normalize(self, params: Dict) -> Dict:
        """按 ParamSpec 补默认、转类型、截断到 [min, max]。"""
        out: Dict[str, Any] = {}
        for p in self.params:
            v = params.get(p.name, p.default)
            try:
                if p.ptype == "int":
                    v = int(round(float(v)))
                else:
                    v = float(v)
            except (TypeError, ValueError):
                v = p.default
            if p.min is not None:
                v = max(v, p.min)
            if p.max is not None:
                v = min(v, p.max)
            out[p.name] = v
        return out
