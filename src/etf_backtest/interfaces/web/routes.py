"""Web页面路由"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from ...infrastructure.storage import EtfStore
from ...domain.strategy.built_in import list_strategies
from config import settings

router = APIRouter()

# 模板配置
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """首页"""
    store = EtfStore(settings.data_dir)
    etfs = store.load_etfs()
    meta = store.get_metadata()

    # 统计数据
    stats = {
        "etf_count": len(etfs),
        "strategy_count": 4,  # 内置策略数量
        "backtest_count": 0,  # 可以从任务存储获取
        "last_update": meta.get("updated_at", "-"),
    }

    # 最近回测（示例数据）
    recent_backtests = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats,
            "recent_backtests": recent_backtests,
        }
    )


@router.get("/etfs", response_class=HTMLResponse)
async def etfs_page(request: Request):
    """ETF列表页"""
    store = EtfStore(settings.data_dir)
    etfs = store.load_etfs()

    return templates.TemplateResponse(
        "etfs.html",
        {
            "request": request,
            "etfs": etfs,
        }
    )


@router.get("/backtest", response_class=HTMLResponse)
async def backtest_page(request: Request):
    """创建回测页"""
    from datetime import date, timedelta

    store = EtfStore(settings.data_dir)
    etfs = store.load_etfs()

    # 获取策略列表
    strategies = [
        {
            "name": s["name"],
            "display_name": s["display_name"],
            "description": s["description"],
            "params": [],
        }
        for s in [
            {"name": "sma", "display_name": "双均线策略", "description": "短期均线上穿长期均线买入，下穿卖出"},
            {"name": "dca", "display_name": "定投策略", "description": "定期定额买入"},
        ]
    ]

    # 默认日期
    today = date.today()
    default_start = (today - timedelta(days=365*3)).strftime("%Y-%m-%d")
    default_end = today.strftime("%Y-%m-%d")

    return templates.TemplateResponse(
        "backtest.html",
        {
            "request": request,
            "etfs": etfs,
            "strategies": strategies,
            "default_start": default_start,
            "default_end": default_end,
        }
    )


@router.get("/result/{backtest_id}", response_class=HTMLResponse)
async def result_page(request: Request, backtest_id: str):
    """回测结果页"""
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "backtest_id": backtest_id,
            "backtest_name": f"回测 {backtest_id}",
        }
    )
