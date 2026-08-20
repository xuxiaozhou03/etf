"""回测路由：单策略单标的 + 参数网格批量。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from etf_quant.api.config import DB_PATH
from etf_quant.api.schemas import BacktestRequest, GridRequest
from etf_quant.api.services.backtest_service import BacktestService

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("")
def run_backtest(req: BacktestRequest):
    """单策略单标的回测，返回完整结果（净值/回撤/持仓/交易/指标）。"""
    try:
        return BacktestService(DB_PATH).run_single(req)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.post("/grid")
def run_grid(req: GridRequest):
    """参数网格批量回测，返回对比行（排序 + 热力图数据）。"""
    try:
        return BacktestService(DB_PATH).run_grid(req)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
