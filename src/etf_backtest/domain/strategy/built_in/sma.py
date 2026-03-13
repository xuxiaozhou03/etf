"""双均线策略"""

from ..base import Strategy, StrategyParam
from ..context import StrategyContext
from ...shared.types import OrderStatus


class SMAStrategy(Strategy):
    """双均线策略"""

    name = "sma"
    display_name = "双均线策略"
    description = "短期均线上穿长期均线买入，下穿卖出"

    def __init__(
        self,
        codes: list[str],
        short_period: int = 5,
        long_period: int = 20,
    ):
        self.codes = codes
        self.short_period = short_period
        self.long_period = long_period

    @classmethod
    def get_params(cls) -> list[StrategyParam]:
        return [
            StrategyParam(
                name="short_period",
                type="int",
                default=5,
                min=1,
                max=60,
                description="短期均线周期",
            ),
            StrategyParam(
                name="long_period",
                type="int",
                default=20,
                min=1,
                max=120,
                description="长期均线周期",
            ),
        ]

    def get_target_codes(self) -> list[str]:
        return self.codes

    def init(self, ctx: StrategyContext) -> None:
        """初始化"""
        self.ctx = ctx
        ctx.log(f"初始化双均线策略: short={self.short_period}, long={self.long_period}")

    def on_bar(self, ctx: StrategyContext, bars: dict[str, dict]) -> None:
        """每根K线"""
        for code in self.codes:
            self._process_code(ctx, code)

    def _process_code(self, ctx: StrategyContext, code: str) -> None:
        """处理单个代码"""
        # 获取历史收盘价
        closes = ctx.history(code, self.long_period + 2, "close")

        if len(closes) < self.long_period + 1:
            return

        # 计算均线
        short_ma = closes.rolling(self.short_period).mean()
        long_ma = closes.rolling(self.long_period).mean()

        # 判断交叉
        # 金叉：短期均线上穿长期均线
        golden_cross = (
            short_ma.iloc[-1] > long_ma.iloc[-1] and
            short_ma.iloc[-2] <= long_ma.iloc[-2]
        )

        # 死叉：短期均线下穿长期均线
        death_cross = (
            short_ma.iloc[-1] < long_ma.iloc[-1] and
            short_ma.iloc[-2] >= long_ma.iloc[-2]
        )

        # 获取当前价格和现金
        current_price = closes.iloc[-1]
        cash = ctx.cash

        # 金叉买入
        if golden_cross:
            # 计算可买数量
            max_shares = int(cash / current_price)
            shares = (max_shares // 100) * 100

            if shares >= 100:
                try:
                    ctx.buy(code, shares)
                    ctx.log(f"{code} 金叉买入 {shares} 股")
                except Exception as e:
                    ctx.log(f"{code} 买入失败: {e}")

        # 死叉卖出
        elif death_cross:
            if code in ctx.positions:
                position = ctx.positions[code]
                if position.available_shares > 0:
                    try:
                        ctx.sell(code, position.available_shares)
                        ctx.log(f"{code} 死叉卖出 {position.available_shares} 股")
                    except Exception as e:
                        ctx.log(f"{code} 卖出失败: {e}")