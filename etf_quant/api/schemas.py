"""API 请求模型（Python 3.9 兼容：用 Optional/List，不用 `X | None` 语法）。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class BacktestRequest(BaseModel):
    code: str
    strategy: str
    params: Dict[str, Any] = {}
    commission_rate: float = 0.00025      # 佣金：双边各万 2.5
    min_commission: float = 0.0
    slippage: float = 0.001               # 滑点：单边 0.1%
    initial_capital: float = 1_000_000
    rf_annual: float = 0.0
    limit_pct: Optional[float] = None     # None → 按标的名称自动推导
    benchmark_code: str = "510300.SH"


class GridRequest(BaseModel):
    code: str
    strategy: str
    param_grids: Dict[str, List[Any]]     # 例：{'fast': [5,10,20], 'slow': [20,40,60]}
    fixed_params: Dict[str, Any] = {}
    sort_by: str = "annualReturn"
    limit: int = 500                      # 组合数防呆上限
    commission_rate: float = 0.00025
    min_commission: float = 0.0
    slippage: float = 0.001
    initial_capital: float = 1_000_000
    rf_annual: float = 0.0
    limit_pct: Optional[float] = None
    benchmark_code: str = "510300.SH"
