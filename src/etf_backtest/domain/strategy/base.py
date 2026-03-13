"""策略基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class StrategyParam:
    """策略参数定义"""
    name: str
    type: str  # 'int', 'float', 'str', 'bool', 'select'
    default: Any
    min: float | None = None
    max: float | None = None
    options: list[str] | None = None
    description: str = ""


class Strategy(ABC):
    """策略基类"""

    # 策略元信息
    name: str = "base"
    display_name: str = "基础策略"
    description: str = ""

    @classmethod
    @abstractmethod
    def get_params(cls) -> list[StrategyParam]:
        """获取策略参数定义"""
        pass

    @abstractmethod
    def get_target_codes(self) -> list[str]:
        """获取目标交易代码"""
        pass

    @abstractmethod
    def init(self, ctx: "StrategyContext") -> None:
        """策略初始化"""
        pass

    @abstractmethod
    def on_bar(self, ctx: "StrategyContext", bars: dict[str, dict]) -> None:
        """
        每根K线触发

        Args:
            ctx: 策略上下文
            bars: 当日行情 {code: {'open': x, 'high': x, ...}}
        """
        pass

    def on_order(self, ctx: "StrategyContext", order) -> None:
        """订单成交回调"""
        pass

    def on_end(self, ctx: "StrategyContext") -> None:
        """回测结束"""
        pass