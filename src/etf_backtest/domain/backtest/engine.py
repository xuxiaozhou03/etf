"""回测引擎核心"""

from dataclasses import dataclass, field
from datetime import date
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING

from .types import BacktestConfig, Order, OrderDirection, OrderStatus, Trade, DailyValue
from .matcher import OrderMatcher
from .portfolio import Portfolio
from .cost import CostModel

if TYPE_CHECKING:
    from ...infrastructure.data import DataProvider
    from ..strategy.base import Strategy
    from ..strategy.context import StrategyContext


class BacktestResult:
    """回测结果"""

    def __init__(self):
        self.daily_values: list[DailyValue] = []
        self.trades: list[Trade] = []
        self.orders: list[Order] = []

    @property
    def nav_curve(self) -> pd.Series:
        """净值曲线"""
        if not self.daily_values:
            return pd.Series()
        df = pd.DataFrame([
            {"date": dv.date, "nav": dv.total_value}
            for dv in self.daily_values
        ])
        return df.set_index("date")["nav"]

    @property
    def return_curve(self) -> pd.Series:
        """收益率曲线"""
        nav = self.nav_curve
        if nav.empty:
            return pd.Series()
        return nav / nav.iloc[0] - 1


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        config: BacktestConfig,
        data_provider: "DataProvider",
    ):
        self.config = config
        self.data_provider = data_provider

        # 初始化组件
        self.matcher = OrderMatcher(config)
        self.portfolio = Portfolio(config.initial_capital)
        self.cost_model = CostModel(
            commission_rate=config.commission_rate,
            min_commission=config.min_commission,
            stamp_duty_rate=config.stamp_duty_rate,
            slippage_rate=config.slippage_rate,
        )

        # 结果
        self.result = BacktestResult()

        # 数据缓存
        self._kline_data: dict[str, pd.DataFrame] = {}
        self._trading_dates: list[date] = []
        self._benchmark_data: pd.DataFrame | None = None

    async def load_data(self, codes: list[str]) -> None:
        """加载K线数据"""
        import asyncio

        # 并行加载ETF数据
        tasks = [
            self.data_provider.get_klines(code, self.config.start_date, self.config.end_date)
            for code in codes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for code, result in zip(codes, results):
            if isinstance(result, Exception):
                print(f"Warning: Failed to load data for {code}: {result}")
                continue
            if result is not None and not result.empty:
                self._kline_data[code] = result

        # 获取交易日历
        if self._kline_data:
            first_df = list(self._kline_data.values())[0]
            self._trading_dates = first_df.index.get_level_values("date").unique().to_list()
            self._trading_dates = [d.date() if hasattr(d, "date") else d for d in self._trading_dates]

        # 加载基准数据
        try:
            self._benchmark_data = await self.data_provider.get_index_klines(
                self.config.benchmark,
                self.config.start_date,
                self.config.end_date,
            )
        except Exception as e:
            print(f"Warning: Failed to load benchmark data: {e}")

    def run(self, strategy: "Strategy") -> BacktestResult:
        """执行回测"""
        from ..strategy.context import StrategyContext

        codes = strategy.get_target_codes()

        # 初始化策略上下文
        context = StrategyContext(
            engine=self,
            portfolio=self.portfolio,
            kline_data=self._kline_data,
        )

        # 策略初始化
        strategy.init(context)

        # 事件驱动循环
        for i, trade_date in enumerate(self._trading_dates):
            # 设置当前日期
            context.set_current_date(trade_date)

            # 更新持仓价格
            self._update_positions_price(trade_date)

            # 触发策略on_bar
            bars = self._get_bars(trade_date, codes)
            if bars:
                strategy.on_bar(context, bars)

            # 处理订单
            self._process_orders(trade_date)

            # 记录每日净值
            self._record_daily_value(trade_date)

        # 策略结束
        strategy.on_end(context)

        return self.result

    def _update_positions_price(self, trade_date: date) -> None:
        """更新持仓价格"""
        for code, position in self.portfolio.positions.items():
            if code in self._kline_data:
                df = self._kline_data[code]
                try:
                    # 尝试不同的索引方式
                    if isinstance(df.index, pd.MultiIndex):
                        bar = df.loc[(code, pd.Timestamp(trade_date))]
                    else:
                        bar = df.loc[pd.Timestamp(trade_date)]
                    position.current_price = float(bar["close"])
                except (KeyError, TypeError):
                    pass  # 停牌或无数据

    def _get_bars(self, trade_date: date, codes: list[str]) -> dict:
        """获取当日行情"""
        bars = {}
        for code in codes:
            if code in self._kline_data:
                df = self._kline_data[code]
                try:
                    if isinstance(df.index, pd.MultiIndex):
                        bar = df.loc[(code, pd.Timestamp(trade_date))]
                    else:
                        bar = df.loc[pd.Timestamp(trade_date)]
                    bars[code] = bar.to_dict()
                except (KeyError, TypeError):
                    pass
        return bars

    def _process_orders(self, trade_date: date) -> None:
        """处理订单"""
        pending_orders = [o for o in self.result.orders if o.status == OrderStatus.PENDING]

        for order in pending_orders:
            # 获取成交价格
            bar = self._get_bar_for_order(order.code, trade_date)
            if bar is None:
                continue  # 停牌，无法成交

            # 撮合
            filled = self.matcher.match(order, bar)

            if filled:
                # 计算成本
                cost = self.cost_model.calculate(order)
                order.commission = cost.total_cost

                # 更新持仓
                etf_name = self._get_etf_name(order.code)
                self.portfolio.process_order(order, etf_name)

                # 记录成交
                trade = Trade(
                    date=trade_date,
                    code=order.code,
                    name=etf_name,
                    direction=order.direction,
                    shares=order.filled_shares,
                    price=order.filled_price,
                    amount=order.filled_amount,
                    commission=order.commission,
                    order_id=order.order_id,
                )
                self.result.trades.append(trade)

    def _get_bar_for_order(self, code: str, trade_date: date) -> dict | None:
        """获取订单成交用的行情"""
        if code not in self._kline_data:
            return None

        df = self._kline_data[code]
        try:
            if isinstance(df.index, pd.MultiIndex):
                bar = df.loc[(code, pd.Timestamp(trade_date))]
            else:
                bar = df.loc[pd.Timestamp(trade_date)]
            return bar.to_dict()
        except (KeyError, TypeError):
            return None

    def _get_etf_name(self, code: str) -> str:
        """获取ETF名称"""
        # 从缓存中获取
        if code in self._kline_data and not self._kline_data[code].empty:
            # 可以从数据中获取
            pass
        return code  # 暂时返回代码

    def _record_daily_value(self, trade_date: date) -> None:
        """记录每日净值"""
        position_value = sum(p.market_value for p in self.portfolio.positions.values())
        total_value = self.portfolio.cash + position_value

        # 获取基准值
        benchmark_value = 0.0
        if self._benchmark_data is not None and not self._benchmark_data.empty:
            try:
                if isinstance(self._benchmark_data.index, pd.MultiIndex):
                    bench_bar = self._benchmark_data.loc[(self.config.benchmark, pd.Timestamp(trade_date))]
                else:
                    bench_bar = self._benchmark_data.loc[pd.Timestamp(trade_date)]
                benchmark_value = float(bench_bar["close"])
            except (KeyError, TypeError):
                pass

        daily_value = DailyValue(
            date=trade_date,
            cash=self.portfolio.cash,
            position_value=position_value,
            total_value=total_value,
            benchmark_value=benchmark_value,
        )

        # 计算收益率
        if self.result.daily_values:
            prev_value = self.result.daily_values[-1].total_value
            daily_value.daily_return = (total_value - prev_value) / prev_value if prev_value > 0 else 0
            daily_value.cumulative_return = total_value / self.config.initial_capital - 1

        self.result.daily_values.append(daily_value)

    def submit_order(self, order: Order) -> Order:
        """提交订单"""
        self.result.orders.append(order)
        return order