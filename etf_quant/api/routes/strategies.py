"""策略路由：元数据 + 参数 schema。"""

from __future__ import annotations

from fastapi import APIRouter

from etf_quant.strategies import list_strategies

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("")
def get_strategies():
    """内置策略列表（含参数 schema，前端表单由此生成）。"""
    return list_strategies()
