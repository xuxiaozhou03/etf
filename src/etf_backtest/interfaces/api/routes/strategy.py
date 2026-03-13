"""策略相关路由"""

from fastapi import APIRouter

from ...application.dto import Response, StrategyInfo

router = APIRouter()


# 内置策略列表
BUILTIN_STRATEGIES = [
    {
        "name": "dca",
        "display_name": "定投策略",
        "description": "定期定额买入",
        "params": [
            {
                "name": "period",
                "type": "select",
                "default": "weekly",
                "options": ["daily", "weekly", "monthly"],
                "description": "定投周期",
            },
            {
                "name": "amount",
                "type": "int",
                "default": 10000,
                "min": 100,
                "max": 1000000,
                "description": "每次买入金额",
            },
        ],
    },
    {
        "name": "sma",
        "display_name": "双均线策略",
        "description": "短期均线上穿长期均线买入，下穿卖出",
        "params": [
            {
                "name": "short_period",
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 60,
                "description": "短期均线周期",
            },
            {
                "name": "long_period",
                "type": "int",
                "default": 20,
                "min": 1,
                "max": 120,
                "description": "长期均线周期",
            },
        ],
    },
    {
        "name": "bollinger",
        "display_name": "布林带策略",
        "description": "价格跌破布林带下轨买入，突破上轨卖出",
        "params": [
            {
                "name": "period",
                "type": "int",
                "default": 20,
                "min": 5,
                "max": 60,
                "description": "布林带周期",
            },
            {
                "name": "std_dev",
                "type": "float",
                "default": 2.0,
                "min": 1.0,
                "max": 3.0,
                "description": "标准差倍数",
            },
        ],
    },
    {
        "name": "momentum",
        "display_name": "动量轮动策略",
        "description": "选择近期涨幅最大的ETF持有",
        "params": [
            {
                "name": "lookback",
                "type": "int",
                "default": 20,
                "min": 5,
                "max": 60,
                "description": "回顾期",
            },
            {
                "name": "top_n",
                "type": "int",
                "default": 1,
                "min": 1,
                "max": 10,
                "description": "持有数量",
            },
        ],
    },
]


@router.get("", response_model=Response)
async def get_strategies():
    """获取策略列表"""
    return Response(data=BUILTIN_STRATEGIES)


@router.get("/{name}", response_model=Response)
async def get_strategy(name: str):
    """获取策略详情"""
    for strategy in BUILTIN_STRATEGIES:
        if strategy["name"] == name:
            return Response(data=strategy)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Strategy {name} not found")
