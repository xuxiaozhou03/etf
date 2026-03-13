"""数据传输对象"""

from datetime import date, datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# ============ 通用响应 ============

class Response(BaseModel):
    """通用响应"""
    code: int = 0
    message: str = "success"
    data: Any = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    list: list
    total: int
    page: int
    page_size: int


# ============ ETF相关 ============

class EtfListItem(BaseModel):
    """ETF列表项"""
    code: str
    name: str
    type: int
    category: str = ""
    asset_size: float = 0.0


class EtfDetail(BaseModel):
    """ETF详情"""
    code: str
    name: str
    type: int
    category: str = ""
    benchmark: str = ""
    tracking: str = ""
    asset_size: float = 0.0
    management_fee: float = 0.0
    custody_fee: float = 0.0


class KlineItem(BaseModel):
    """K线数据项"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    turnover_rate: float = 0.0
    change_pct: float = 0.0


class KlineResponse(BaseModel):
    """K线响应"""
    code: str
    name: str
    klines: list[KlineItem]


# ============ 策略相关 ============

class StrategyParam(BaseModel):
    """策略参数定义"""
    name: str
    type: str  # int, float, str, bool, select
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[list[str]] = None
    description: str = ""


class StrategyInfo(BaseModel):
    """策略信息"""
    name: str
    display_name: str
    description: str
    params: list[StrategyParam]


# ============ 回测相关 ============

class BacktestCreateRequest(BaseModel):
    """创建回测请求"""
    name: str = Field(..., description="回测名称")
    strategy: str = Field(..., description="策略名称")
    params: dict = Field(default_factory=dict, description="策略参数")
    etfs: list[str] = Field(..., description="ETF代码列表")
    start_date: date = Field(..., description="起始日期")
    end_date: date = Field(..., description="结束日期")
    initial_capital: float = Field(default=1000000.0, description="初始资金")
    commission: float = Field(default=0.0003, description="佣金率")
    slippage: float = Field(default=0.001, description="滑点率")
    benchmark: str = Field(default="000300", description="基准指数")


class BacktestCreateResponse(BaseModel):
    """创建回测响应"""
    backtest_id: str
    status: str


class BacktestStatus(BaseModel):
    """回测状态"""
    backtest_id: str
    status: str  # pending, running, completed, failed
    progress: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class TradeRecord(BaseModel):
    """交易记录"""
    date: str
    code: str
    name: str
    direction: str
    shares: int
    price: float
    amount: float
    commission: float


class DailyValueRecord(BaseModel):
    """每日净值记录"""
    date: str
    value: float
    benchmark_value: float = 0.0


class PerformanceSummary(BaseModel):
    """绩效摘要"""
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    win_rate: float
    trade_count: int


class BacktestResult(BaseModel):
    """回测结果"""
    id: str
    name: str
    status: str
    summary: PerformanceSummary
    daily_values: list[DailyValueRecord]
    trades: list[TradeRecord]
