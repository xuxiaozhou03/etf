"""定投策略"""

from ..base import Strategy, StrategyParam
from ..context import StrategyContext


class DCAStrategy(Strategy):
    """定投策略"""

    name = "dca"
    display_name = "定投策略"
    description = "定期定额买入"

    def __init__(
        self,
        codes: list[str],
        period: str = "weekly",
        amount: float = 10000,
    ):
        self.codes = codes
        self.period = period  # daily, weekly, monthly
        self.amount = amount
        self._last_buy_date = None

    @classmethod
    def get_params(cls) -> list[StrategyParam]:
        return [
            StrategyParam(
                name="period",
                type="select",
                default="weekly",
                options=["daily", "weekly", "monthly"],
                description="定投周期",
            ),
            StrategyParam(
                name="amount",
                type="int",
                default=10000,
                min=100,
                max=1000000,
                description="每次买入金额",
            ),
        ]

    def get_target_codes(self) -> list[str]:
        return self.codes

    def init(self, ctx: StrategyContext) -> None:
        """初始化"""
        ctx.log(f"初始化定投策略: period={self.period}, amount={self.amount}")

    def on_bar(self, ctx: StrategyContext, bars: dict[str, dict]) -> None:
        """每根K线"""
        current_date = ctx.current_date

        # 检查是否需要买入
        should_buy = self._should_buy(current_date)

        if should_buy:
            for code in self.codes:
                if code in bars:
                    bar = bars[code]
                    price = bar.get("close", 0)

                    if price > 0:
                        shares = int(self.amount / price)
                        shares = (shares // 100) * 100

                        if shares >= 100:
                            try:
                                ctx.buy(code, shares)
                                ctx.log(f"{code} 定投买入 {shares} 股")
                            except Exception as e:
                                ctx.log(f"{code} 买入失败: {e}")

            self._last_buy_date = current_date

    def _should_buy(self, current_date) -> bool:
        """判断是否应该买入"""
        if self._last_buy_date is None:
            return True

        if self.period == "daily":
            return True
        elif self.period == "weekly":
            # 每周买入一次
            days_diff = (current_date - self._last_buy_date).days
            return days_diff >= 7
        elif self.period == "monthly":
            # 每月买入一次
            days_diff = (current_date - self._last_buy_date).days
            return days_diff >= 30

        return False