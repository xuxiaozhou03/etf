"""内置策略"""

from .sma import SMAStrategy
from .dca import DCAStrategy

# 策略注册表
STRATEGY_REGISTRY = {
    "sma": SMAStrategy,
    "dca": DCAStrategy,
}


def get_strategy_class(name: str):
    """获取策略类"""
    return STRATEGY_REGISTRY.get(name)


def list_strategies():
    """列出所有策略"""
    return [
        {"name": cls.name, "display_name": cls.display_name, "description": cls.description}
        for cls in STRATEGY_REGISTRY.values()
    ]


__all__ = [
    "SMAStrategy",
    "DCAStrategy",
    "get_strategy_class",
    "list_strategies",
]
