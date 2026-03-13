"""组合管理"""

from .types import Order, OrderDirection, Position
from .cost import TransactionCost


class Portfolio:
    """投资组合管理"""

    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: dict[str, Position] = {}

    @property
    def total_value(self) -> float:
        """总资产"""
        return self.cash + sum(p.market_value for p in self.positions.values())

    def process_order(self, order: Order, etf_name: str = "") -> None:
        """处理订单"""
        if order.direction == OrderDirection.BUY:
            self._process_buy(order, etf_name)
        else:
            self._process_sell(order, etf_name)

    def _process_buy(self, order: Order, etf_name: str) -> None:
        """处理买入"""
        # 扣除资金
        total_cost = order.filled_amount + order.commission
        self.cash -= total_cost

        # 更新持仓
        code = order.code
        if code in self.positions:
            pos = self.positions[code]
            total_shares = pos.shares + order.filled_shares
            total_cost_price = pos.cost_price * pos.shares + order.filled_price * order.filled_shares
            pos.cost_price = total_cost_price / total_shares if total_shares > 0 else 0
            pos.shares = total_shares
            # T+1: 新买入的股份不可用
        else:
            self.positions[code] = Position(
                code=code,
                name=etf_name,
                shares=order.filled_shares,
                available_shares=0,  # T+1
                cost_price=order.filled_price,
                current_price=order.filled_price,
            )

    def _process_sell(self, order: Order, etf_name: str) -> None:
        """处理卖出"""
        code = order.code

        if code not in self.positions:
            return

        pos = self.positions[code]

        # 计算收入
        revenue = order.filled_amount - order.commission
        self.cash += revenue

        # 更新持仓
        pos.shares -= order.filled_shares
        pos.available_shares = min(pos.available_shares, pos.shares)

        # 清仓
        if pos.shares <= 0:
            del self.positions[code]

    def update_available_shares(self) -> None:
        """更新可用股份（每日开盘时调用）"""
        for pos in self.positions.values():
            pos.available_shares = pos.shares

    def get_position(self, code: str) -> Position | None:
        """获取持仓"""
        return self.positions.get(code)

    def get_available_shares(self, code: str) -> int:
        """获取可用股份"""
        pos = self.positions.get(code)
        return pos.available_shares if pos else 0