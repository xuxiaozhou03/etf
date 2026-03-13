"""回测相关路由"""

import asyncio
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from ...application.dto import (
    Response,
    BacktestCreateRequest,
    BacktestCreateResponse,
    BacktestStatus,
)
from ...infrastructure.data import EfinanceProvider
from ...infrastructure.storage import EtfStore
from config import settings

router = APIRouter()

# 任务存储（生产环境应使用Redis）
_tasks: dict = {}


def get_etf_store() -> EtfStore:
    return EtfStore(settings.data_dir)


def get_data_provider() -> EfinanceProvider:
    return EfinanceProvider(cache_dir=settings.cache_dir)


@router.post("", response_model=Response)
async def create_backtest(
    request: BacktestCreateRequest,
    background_tasks: BackgroundTasks,
):
    """创建回测任务"""
    backtest_id = f"bt_{uuid.uuid4().hex[:8]}"

    _tasks[backtest_id] = {
        "backtest_id": backtest_id,
        "status": "pending",
        "progress": 0,
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "request": request.model_dump(),
    }

    # 后台执行回测
    background_tasks.add_task(run_backtest_task, backtest_id, request)

    return Response(data={
        "backtest_id": backtest_id,
        "status": "pending",
    })


@router.get("/{backtest_id}", response_model=Response)
async def get_backtest_status(backtest_id: str):
    """获取回测状态"""
    if backtest_id not in _tasks:
        raise HTTPException(status_code=404, detail="Backtest not found")

    task = _tasks[backtest_id]
    return Response(data={
        "backtest_id": task["backtest_id"],
        "status": task["status"],
        "progress": task["progress"],
        "started_at": task["started_at"],
        "completed_at": task["completed_at"],
        "error": task["error"],
    })


@router.get("/{backtest_id}/result", response_model=Response)
async def get_backtest_result(backtest_id: str):
    """获取回测结果"""
    if backtest_id not in _tasks:
        raise HTTPException(status_code=404, detail="Backtest not found")

    task = _tasks[backtest_id]

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Backtest status: {task['status']}")

    return Response(data=task["result"])


async def run_backtest_task(backtest_id: str, request: BacktestCreateRequest):
    """执行回测任务"""
    from ....domain.backtest.engine import BacktestEngine
    from ....domain.backtest.types import BacktestConfig
    from ....domain.strategy.built_in import get_strategy_class

    task = _tasks[backtest_id]

    try:
        task["status"] = "running"
        task["started_at"] = datetime.now().isoformat()

        # 创建配置
        config = BacktestConfig(
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            commission_rate=request.commission,
            slippage_rate=request.slippage,
            benchmark=request.benchmark,
        )

        # 创建数据提供者
        provider = EfinanceProvider(cache_dir=settings.cache_dir)

        # 创建引擎
        engine = BacktestEngine(config, provider)

        task["progress"] = 10

        # 加载数据
        await engine.load_data(request.etfs)

        task["progress"] = 30

        # 创建策略
        strategy_class = get_strategy_class(request.strategy)
        if strategy_class is None:
            raise ValueError(f"Unknown strategy: {request.strategy}")

        strategy = strategy_class(
            codes=request.etfs,
            **request.params
        )

        task["progress"] = 40

        # 执行回测
        result = engine.run(strategy)

        task["progress"] = 80

        # 计算指标
        from ....domain.analysis.metrics import MetricsCalculator
        calculator = MetricsCalculator(result.daily_values, result.trades)
        metrics = calculator.calculate()

        task["progress"] = 90

        # 构建结果
        task["result"] = {
            "id": backtest_id,
            "name": request.name,
            "status": "completed",
            "summary": {
                "total_return": metrics.total_return,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "calmar_ratio": metrics.calmar_ratio,
                "win_rate": metrics.win_rate,
                "trade_count": metrics.total_trades,
            },
            "daily_values": [
                {
                    "date": dv.date.isoformat(),
                    "value": dv.total_value,
                    "benchmark_value": dv.benchmark_value,
                }
                for dv in result.daily_values
            ],
            "trades": [
                {
                    "date": t.date.isoformat(),
                    "code": t.code,
                    "name": t.name,
                    "direction": t.direction.value,
                    "shares": t.shares,
                    "price": t.price,
                    "amount": t.amount,
                    "commission": t.commission,
                }
                for t in result.trades
            ],
        }

        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        task["progress"] = 100

    except Exception as e:
        import traceback
        task["status"] = "failed"
        task["error"] = str(e)
        task["completed_at"] = datetime.now().isoformat()
        print(f"Backtest failed: {e}")
        traceback.print_exc()
