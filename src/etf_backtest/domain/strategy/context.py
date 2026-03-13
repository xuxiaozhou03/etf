"""策略上下文"""

from typing import TYPE_CHECKING
import pandas as pd

from ...shared.types import Order, OrderDirection, Position

if TYPE_CHECKING:
    from ..backtest.engine import BacktestEngine
    from ..backtest.portfolio import Portfolio


class StrategyContext:
    """策略上下文 - 策略与回测引擎的交互接口"""

    def __init__(
        self,
        engine: "BacktestEngine",
        portfolio: "Portfolio",
        kline_data: dict[str, pd.DataFrame],
    ):
        self._engine = engine
        self._portfolio = portfolio
        self._kline_data = kline_data
        self._current_date = None
        self._logs: list[str] = []

    @property
    def cash(self) -> float:
        """可用现金"""
        return self._portfolio.cash

    @property
    def total_value(self) -> float:
        """总资产"""
        return self._portfolio.total_value

    @property
    def positions(self) -> dict[str, Position]:
        """当前持仓"""
        return self._portfolio.positions

    @property
    def current_date(self) -> pd.Timestamp | None:
        """当前日期"""
        return self._current_date

    def set_current_date(self, date) -> None:
        """设置当前日期"""
        self._current_date = pd.Timestamp(date)

    def history(
        self,
        code: str,
        count: int,
        fields: str | list[str] = "close"
    ) -> pd.DataFrame | pd.Series:
        """
        获取历史K线

        Args:
            code: ETF代码
            count: 返回条数
            fields: 字段名

        Returns:
            历史数据
        """
        if code not in self._kline_data:
            raise ValueError(f"Code {code} not found in kline data")

        df = self._kline_data[code]

        # 获取到当前日期为止的数据
        if self._current_date is not None:
            if isinstance(df.index, pd.MultiIndex):
                dates = df.index.get_level_values("date")
                df = df[dates <= self._current_date]
            else:
                df = df[df.index <= self._current_date]

        # 取最后count条
        df = df.tail(count)

        if isinstance(fields, str):
            return df[fields] if fields in df.columns else df
        return df[fields] if all(f in df.columns for f in fields) else df

    def get_data(self, code: str) -> dict | None:
        """获取当日数据"""
        if code not in self._kline_data:
            return None

        df = self._kline_data[code]
        try:
            if isinstance(df.index, pd.MultiIndex):
                bar = df.loc[(code, self._current_date)]
            else:
                bar = df.loc[self._current_date]
            return bar.to_dict()
        except KeyError:
            return None

    def buy(self, code: str, shares: int) -> Order:
        """
        买入

        Args:
            code: ETF代码
            shares: 买入数量（必须是100的整数倍）

        Returns:
            订单
        """
        # 检查数量是否为100的整数倍
        shares = (shares // 100) * 100
        if shares <= 0:
            raise ValueError("Shares must be at least 100")

        # 获取当前价格
        bar = self.get_data(code)
        if bar is None:
            raise ValueError(f"No data for {code} on {self._current_date}")

        price = bar.get("close", 0)

        # 创建订单
        order = Order(
            code=code,
            direction=OrderDirection.BUY,
            shares=shares,
            price=price,
        )

        return self._engine.submit_order(order)

    def sell(self, code: str, shares: int) -> Order:
        """
        卖出

        Args:
            code: ETF代码
            shares: 卖出数量

        Returns:
            订单
        """
        # 检查持仓
        if code not in self.positions:
            raise ValueError(f"No position for {code}")

        position = self.positions[code]
        shares = min(shares, position.available_shares)
        shares = (shares // 100) * 100

        if shares <= 0:
            raise ValueError("No available shares to sell")

        # 获取当前价格
        bar = self.get_data(code)
        if bar is None:
            raise ValueError(f"No data for {code} on {self._current_date}")

        price = bar.get("close", 0)

        # 创建订单
        order = Order(
            code=code,
            direction=OrderDirection.SELL,
            shares=shares,
            price=price,
        )

        return self._engine.submit_order(order)

    def order_target(self, code: str, target_shares: int) -> Order | None:
        """
        调整至目标仓位

        Args:
            code: ETF代码
            target_shares: 目标数量

        Returns:
            订单，如果无需调整则返回None
        """
        target_shares = (target_shares // 100) * 100

        current_shares = self.positions.get(code, Position(code, "", 0, 0, 0)).shares

        diff = target_shares - current_shares

        if diff > 0:
            return self.buy(code, diff)
        elif diff < 0:
            return self.sell(code, -diff)

        return None

    def log(self, message: str) -> None:
        """记录日志"""
        date_str = self._current_date.strftime("%Y-%m-%d") if self._current_date else "N/A"
        log_entry = f"[{date_str}] {message}"
        self._logs.append(log_entry)
        print(log_entry)