"""交易成本模型"""

from dataclasses import dataclass
from .types import Order, OrderDirection


@dataclass
class TransactionCost:
    """交易成本"""
    commission: float = 0.0       # 佣金
    stamp_duty: float = 0.0       # 印花税
    transfer_fee: float = 0.0     # 过户费
    slippage_cost: float = 0.0    # 滑点成本（已计入成交价）

    @property
    def total_cost(self) -> float:
        return self.commission + self.stamp_duty + self.transfer_fee


class CostModel:
    """A股交易成本模型"""

    def __init__(
        self,
        commission_rate: float = 0.0003,
        min_commission: float = 5.0,
        stamp_duty_rate: float = 0.001,
        transfer_fee_rate: float = 0.00001,
        slippage_rate: float = 0.001,
    ):
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.stamp_duty_rate = stamp_duty_rate
        self.transfer_fee_rate = transfer_fee_rate
        self.slippage_rate = slippage_rate

    def calculate(self, order: Order) -> TransactionCost:
        """计算交易成本"""
        amount = order.filled_amount

        cost = TransactionCost()

        # 佣金（买卖都收，最低5元）
        cost.commission = max(amount * self.commission_rate, self.min_commission)

        # 印花税（仅卖出）
        if order.direction == OrderDirection.SELL:
            cost.stamp_duty = amount * self.stamp_duty_rate

        # 过户费（买卖都收，沪市ETF免收）
        cost.transfer_fee = amount * self.transfer_fee_rate

        return cost