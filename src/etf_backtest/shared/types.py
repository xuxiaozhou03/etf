"""公共类型定义"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
import uuid


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderDirection(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """订单"""
    code: str
    direction: OrderDirection
    shares: int
    price: float
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: OrderStatus = OrderStatus.PENDING
    filled_shares: int = 0
    filled_price: float = 0.0
    filled_amount: float = 0.0
    commission: float = 0.0
    message: str = ""
    create_time: datetime = field(default_factory=datetime.now)
    fill_time: Optional[datetime] = None


@dataclass
class Position:
    """持仓"""
    code: str
    name: str
    shares: int
    available_shares: int  # T+1
    cost_price: float
    current_price: float = 0.0

    @property
    def market_value(self) -> float:
        """市值"""
        return self.shares * self.current_price

    @property
    def profit_loss(self) -> float:
        """浮动盈亏"""
        return (self.current_price - self.cost_price) * self.shares

    @property
    def profit_loss_pct(self) -> float:
        """盈亏比例"""
        if self.cost_price == 0:
            return 0.0
        return (self.current_price - self.cost_price) / self.cost_price


@dataclass
class Trade:
    """成交记录"""
    date: date
    code: str
    name: str
    direction: OrderDirection
    shares: int
    price: float
    amount: float
    commission: float
    order_id: str


@dataclass
class DailyValue:
    """每日净值"""
    date: date
    cash: float
    position_value: float
    total_value: float
    benchmark_value: float = 0.0
    daily_return: float = 0.0
    cumulative_return: float = 0.0


@dataclass
class BacktestConfig:
    """回测配置"""
    start_date: date
    end_date: date
    initial_capital: float = 1_000_000.0

    # 交易成本
    commission_rate: float = 0.0003      # 佣金率
    min_commission: float = 5.0          # 最低佣金
    stamp_duty_rate: float = 0.001       # 印花税（仅卖出）
    transfer_fee_rate: float = 0.00001   # 过户费
    slippage_rate: float = 0.001         # 滑点率

    # 撮合设置
    price_type: str = "close"  # open / close

    # 基准
    benchmark: str = "000300"


@dataclass
class EtfInfo:
    """ETF基础信息"""
    code: str
    name: str
    type: int  # 0-上证 1-深证
    category: str = ""
    benchmark: str = ""
    tracking: str = ""
    asset_size: float = 0.0
    management_fee: float = 0.0
    custody_fee: float = 0.0


@dataclass
class Kline:
    """K线数据"""
    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    turnover_rate: float = 0.0
    change_pct: float = 0.0
