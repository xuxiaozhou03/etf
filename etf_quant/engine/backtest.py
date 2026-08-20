"""向量化回测引擎：信号 → 持仓 → 净值/回撤 → 交易明细。

时序约定（避免前视）：
- 信号于 T 日收盘生成（用 T 日及以前数据）；
- T 日实际持仓 = T-1 日信号（shift(1)），即信号次日生效；
- 收益归因用「收盘-收盘」：strat_ret[t] = pos_prev[t] * (adj_close[t]/adj_close[t-1] - 1) - 费用；
  当持仓恒 1 且零费用时，净值精确等于买持基准（不变式）。
- 交易日志记录「次日开盘价」为执行价（open-vs-close 差并入可配置滑点，简化模式）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from etf_quant.engine.data import limit_flags


@dataclass
class BacktestConfig:
    """回测成本与规则配置。"""
    commission_rate: float = 0.00025   # 佣金：双边各万 2.5
    min_commission: float = 0.0        # 单笔最低佣金（0 表示不设下限）
    slippage: float = 0.001            # 滑点：单边 0.1%
    initial_capital: float = 1_000_000
    limit_pct: float = 0.10            # 涨跌停限制；0 = 无涨跌停
    rf_annual: float = 0.0             # 无风险利率（年化）
    periods_per_year: int = 252
    benchmark_code: str = "510300.SH"  # 文档性字段：基准标的

    @property
    def cost_rate(self) -> float:
        return self.commission_rate + self.slippage


def run_backtest(df: pd.DataFrame, signals: pd.Series, config: BacktestConfig,
                 bench_adj_close: Optional[pd.Series] = None) -> Dict:
    """执行单标的回测。

    参数：
        df: load_adjusted_ohlc 输出（date 索引，含 adj_open/adj_close/prev_close）。
        signals: target position Series（0/1，与 df 索引对齐；rolling 温区 NaN 视为 0）。
        config: BacktestConfig。
        bench_adj_close: 基准前复权收盘价（与 df 索引对齐）；None 则无基准。

    返回 dict：nav / bench_nav / drawdown / bench_drawdown / position /
              returns / bench_returns / trades / metrics。
    """
    if df.empty:
        return {"nav": pd.Series(dtype=float), "metrics": {}}

    # ---- 目标仓位 → 实际持仓（信号次日生效）----
    target = signals.astype(float).fillna(0.0).clip(0.0, 1.0).reindex(df.index).fillna(0.0)
    pos = target.shift(1).fillna(0.0)

    # 涨跌停拦截：开盘即封板则当日持仓顺延（信号不变，次日自动重试）
    if config.limit_pct > 0:
        is_limit_up, is_limit_down = limit_flags(df, config.limit_pct)
        prev_pos = pos.shift(1).fillna(0.0)
        blocked_buy = (pos > prev_pos) & is_limit_up
        blocked_sell = (pos < prev_pos) & is_limit_down
        pos = pos.where(~(blocked_buy | blocked_sell), prev_pos)

    pos_prev = pos.shift(1).fillna(0.0)

    # ---- 收益归因（收盘-收盘）+ 费用 ----
    # pos[t] = target[t-1]：T 日实际持仓，赚取 T 日收盘-收盘收益
    ret = df["adj_close"].pct_change().fillna(0.0)
    gross = (pos * ret).fillna(0.0)
    trade = (pos - pos_prev).abs()
    strat_ret = gross - trade * config.cost_rate

    # 最低佣金修正（交易稀少，按前一日权益一次性近似）
    if config.min_commission > 0:
        nav_tmp = (1 + strat_ret).cumprod()
        eq_prev = nav_tmp.shift(1).fillna(1.0) * config.initial_capital
        td = trade > 0
        shortfall = np.maximum(0.0, config.min_commission - eq_prev * config.cost_rate)
        strat_ret = strat_ret.where(~td, strat_ret - shortfall / eq_prev)

    nav = (1 + strat_ret).cumprod()

    # ---- 基准 ----
    bench_nav = None
    bench_returns = None
    if bench_adj_close is not None:
        b = bench_adj_close.reindex(df.index)
        bench_returns = b.pct_change().fillna(0.0)
        bench_nav = (1 + bench_returns).cumprod()

    # ---- 回撤 ----
    drawdown = nav / nav.cummax() - 1.0
    bench_drawdown = None
    if bench_nav is not None:
        bench_drawdown = bench_nav / bench_nav.cummax() - 1.0

    trades = extract_trades(pos, df)

    metrics = _compute_metrics(nav, strat_ret, bench_returns, trades, config)

    return {
        "nav": nav, "bench_nav": bench_nav, "drawdown": drawdown, "bench_drawdown": bench_drawdown,
        "position": pos, "returns": strat_ret, "bench_returns": bench_returns,
        "trades": trades, "metrics": metrics,
    }


def extract_trades(pos: pd.Series, df: pd.DataFrame) -> List[Dict]:
    """从持仓变化提取 round-trip 交易（0/1 满仓进出）。

    每笔买事件开仓（记次日开盘价为执行价，份额归一化 1），卖事件配对平仓。
    returnPct = 卖价/买价 - 1；pnl 按初始资金满仓口径近似。
    """
    trades: List[Dict] = []
    entry: Optional[Dict] = None
    for i in range(len(pos)):
        dpos = pos.iloc[i] - (pos.iloc[i - 1] if i > 0 else 0.0)
        if dpos > 0:
            entry = {
                "buyDate": str(df.index[i].date()),
                "buyPrice": float(df["adj_open"].iloc[i]),
                "shares": 1.0,
            }
        elif dpos < 0 and entry is not None:
            sell_price = float(df["adj_open"].iloc[i])
            buy_price = entry["buyPrice"]
            ret = sell_price / buy_price - 1 if buy_price else 0.0
            trades.append({
                "buyDate": entry["buyDate"],
                "buyPrice": round(buy_price, 4),
                "sellDate": str(df.index[i].date()),
                "sellPrice": round(sell_price, 4),
                "shares": 1.0,
                "returnPct": round(ret, 4),
                "holdDays": int((df.index[i] - pd.Timestamp(entry["buyDate"])).days),
            })
            entry = None
    return trades


def _compute_metrics(nav: pd.Series, returns: pd.Series, bench_returns: Optional[pd.Series],
                     trades: List[Dict], config: BacktestConfig) -> Dict:
    from etf_quant.engine import metrics as m

    out = {
        "totalReturn": m.total_return(nav),
        "annualReturn": m.annualized_return(nav, config.periods_per_year),
        "annualVol": m.annualized_vol(returns, config.periods_per_year),
        "sharpe": m.sharpe(returns, config.rf_annual, config.periods_per_year),
        "sortino": m.sortino(returns, config.rf_annual, config.periods_per_year),
        "calmar": m.calmar(nav, config.periods_per_year),
        "annualTurnover": m.annual_turnover(len(nav), len(trades), config.periods_per_year),
        "tradeCount": len(trades),
        "winRate": m.win_rate(trades),
        "profitLossRatio": m.profit_loss_ratio(trades),
        "avgHoldDays": m.avg_hold_days(trades),
    }
    out.update(m.max_drawdown_info(nav))
    if bench_returns is not None:
        out["alpha"], out["beta"] = m.alpha_beta(returns, bench_returns, config.rf_annual,
                                                 config.periods_per_year)
        out["infoRatio"] = m.info_ratio(returns, bench_returns, config.periods_per_year)
    else:
        out.update({"alpha": None, "beta": None, "infoRatio": None})
    return out
