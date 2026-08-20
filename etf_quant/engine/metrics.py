"""绩效指标计算：全部标量函数，输入 nav/returns/trades。"""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np
import pandas as pd


def total_return(nav: pd.Series) -> float:
    """总收益率（净值序列末值 - 1）。"""
    return round(float(nav.iloc[-1] - 1), 4) if len(nav) else 0.0


def annualized_return(nav: pd.Series, ppy: int = 252) -> float:
    """年化收益率（几何）。"""
    n = len(nav)
    if n < 2:
        return 0.0
    return round(float(nav.iloc[-1] ** (ppy / n) - 1), 4)


def annualized_vol(returns: pd.Series, ppy: int = 252) -> float:
    """年化波动率（标准差 × sqrt(252)）。"""
    if len(returns) < 2:
        return 0.0
    return round(float(returns.std(ddof=1) * np.sqrt(ppy)), 4)


def max_drawdown_info(nav: pd.Series) -> Dict:
    """最大回撤及峰值/谷底日期。"""
    if len(nav) == 0:
        return {"maxDrawdown": 0.0, "maxDrawdownPeak": None, "maxDrawdownTrough": None}
    dd = nav / nav.cummax() - 1.0
    trough_idx = dd.idxmin()
    trough_pos = nav.index.get_loc(trough_idx)
    peak_idx = nav.iloc[: trough_pos + 1].idxmax()
    return {
        "maxDrawdown": round(float(dd.min()), 4),
        "maxDrawdownPeak": str(peak_idx.date()),
        "maxDrawdownTrough": str(trough_idx.date()),
    }


def sharpe(returns: pd.Series, rf_annual: float = 0.0, ppy: int = 252) -> float:
    """夏普比率（无风险利率按日折算）。"""
    if len(returns) < 2:
        return 0.0
    excess = returns - rf_annual / ppy
    sd = excess.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return 0.0
    return round(float(excess.mean() / sd * np.sqrt(ppy)), 4)


def sortino(returns: pd.Series, rf_annual: float = 0.0, ppy: int = 252) -> float:
    """索提诺比率（下行波动率）。"""
    if len(returns) < 2:
        return 0.0
    excess = returns - rf_annual / ppy
    downside = excess[excess < 0]
    dsd = downside.std(ddof=1)
    if dsd == 0 or np.isnan(dsd):
        return 0.0
    return round(float(excess.mean() / dsd * np.sqrt(ppy)), 4)


def calmar(nav: pd.Series, ppy: int = 252) -> float:
    """卡玛比率 = 年化收益 / |最大回撤|。"""
    n = len(nav)
    if n < 2:
        return 0.0
    ann = nav.iloc[-1] ** (ppy / n) - 1
    mdd = abs(float((nav / nav.cummax() - 1.0).min()))
    if mdd == 0:
        return 0.0
    return round(float(ann / mdd), 4)


def alpha_beta(returns: pd.Series, bench_returns: pd.Series,
               rf_annual: float = 0.0, ppy: int = 252):
    """Alpha（年化）/ Beta（OLS 回归）。"""
    r = returns.to_numpy()
    b = bench_returns.to_numpy()
    mask = ~(np.isnan(r) | np.isnan(b))
    r, b = r[mask], b[mask]
    if len(r) < 2:
        return None, None
    er = r - rf_annual / ppy
    eb = b - rf_annual / ppy
    var_b = np.var(eb)
    beta = float(np.cov(er, eb)[0, 1] / var_b) if var_b > 0 else 0.0
    alpha_ann = float((er.mean() - beta * eb.mean()) * ppy)
    return round(alpha_ann, 4), round(beta, 4)


def info_ratio(returns: pd.Series, bench_returns: pd.Series, ppy: int = 252) -> float:
    """信息比率 = 超额收益均值 / 超额收益波动 × sqrt(252)。"""
    excess = returns - bench_returns
    sd = excess.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return 0.0
    return round(float(excess.mean() / sd * np.sqrt(ppy)), 4)


def annual_turnover(periods: int, trade_count: int, ppy: int = 252) -> float:
    """年化换手率：每笔 round-trip 换手 2 倍权益，除以年数。"""
    if trade_count == 0:
        return 0.0
    years = periods / ppy
    if years <= 0:
        return 0.0
    return round(2 * trade_count / years, 4)


def win_rate(trades: List[Dict]) -> Optional[float]:
    """胜率。"""
    if not trades:
        return None
    wins = sum(1 for t in trades if t["returnPct"] > 0)
    return round(wins / len(trades), 4)


def profit_loss_ratio(trades: List[Dict]) -> Optional[float]:
    """盈亏比 = 平均盈利 / 平均亏损（绝对值）。"""
    if not trades:
        return None
    wins = [t["returnPct"] for t in trades if t["returnPct"] > 0]
    losses = [abs(t["returnPct"]) for t in trades if t["returnPct"] <= 0]
    if not wins or not losses:
        return None
    return round(float(np.mean(wins) / np.mean(losses)), 4)


def avg_hold_days(trades: List[Dict]) -> Optional[float]:
    """平均持仓周期（自然日）。"""
    if not trades:
        return None
    return round(float(np.mean([t["holdDays"] for t in trades])), 1)
