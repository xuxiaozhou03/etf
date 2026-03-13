"""订单撮合器"""

from .types import BacktestConfig, Order, OrderStatus, OrderDirection


class OrderMatcher:
    """订单撮合器"""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def match(self, order: Order, bar: dict) -> bool:
        """
        撮合订单

        Args:
            order: 订单
            bar: 当日行情 {'open': x, 'high': x, 'low': x, 'close': x, ...}

        Returns:
            是否成交
        """
        # 检查涨跌停
        if self._is_limit_up(order, bar):
            order.status = OrderStatus.REJECTED
            order.message = "涨停无法买入"
            return False

        if self._is_limit_down(order, bar):
            order.status = OrderStatus.REJECTED
            order.message = "跌停无法卖出"
            return False

        # 计算成交价格
        if self.config.price_type == "open":
            fill_price = bar.get("open", bar.get("close", 0))
        else:
            fill_price = bar.get("close", 0)

        # 应用滑点
        if order.direction == OrderDirection.BUY:
            fill_price *= (1 + self.config.slippage_rate)
        else:
            fill_price *= (1 - self.config.slippage_rate)

        # 更新订单
        order.filled_price = fill_price
        order.filled_shares = order.shares
        order.filled_amount = fill_price * order.shares
        order.status = OrderStatus.FILLED

        return True

    def _is_limit_up(self, order: Order, bar: dict) -> bool:
        """检查是否涨停"""
        if order.direction != OrderDirection.BUY:
            return False

        close = bar.get("close", 0)
        open_price = bar.get("open", close)

        # 涨停判断：收盘价等于开盘价的1.1倍（近似）
        if open_price > 0:
            limit_up = open_price * 1.10
            if close >= limit_up * 0.998:
                return True

        return False

    def _is_limit_down(self, order: Order, bar: dict) -> bool:
        """检查是否跌停"""
        if order.direction != OrderDirection.SELL:
            return False

        close = bar.get("close", 0)
        open_price = bar.get("open", close)

        # 跌停判断
        if open_price > 0:
            limit_down = open_price * 0.90
            if close <= limit_down * 1.002:
                return True

        return False