"""回测编排：数据加载 → 策略 → 引擎 → 指标 → JSON。"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from etf_quant.api.schemas import BacktestRequest, GridRequest
from etf_quant.engine.backtest import BacktestConfig, run_backtest
from etf_quant.engine.data import default_limit_pct, load_adjusted_ohlc
from etf_quant.engine.grid import METRIC_FIELDS, run_grid
from etf_quant.storage import SQLiteStore
from etf_quant.strategies import get_strategy
from etf_quant.strategies.grid import make_grid


def _clean(v):
    """NaN → None（JSON 安全）。"""
    return None if v is None or (isinstance(v, float) and v != v) else v


class BacktestService:
    """单标的/网格回测编排（每请求用独立 store 连接，避免线程共享）。"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _store(self) -> SQLiteStore:
        return SQLiteStore(self.db_path)

    def _etf_name(self, code: str) -> str:
        store = self._store()
        try:
            df = store.load_etf_list()
            row = df[df["securityCode"] == code]
            return str(row.iloc[0]["securityName"]) if not row.empty else ""
        finally:
            store.close()

    def _config(self, req) -> BacktestConfig:
        limit_pct = req.limit_pct
        if limit_pct is None:
            limit_pct = default_limit_pct(self._etf_name(req.code))
        return BacktestConfig(
            commission_rate=req.commission_rate, min_commission=req.min_commission,
            slippage=req.slippage, initial_capital=req.initial_capital,
            limit_pct=limit_pct, rf_annual=req.rf_annual,
            benchmark_code=req.benchmark_code,
        )

    def _benchmark(self, code: str, benchmark_code: str):
        """基准前复权收盘价；基准缺数据时降级为标自身。"""
        store = self._store()
        try:
            if benchmark_code and benchmark_code != code:
                bench_df = load_adjusted_ohlc(store, benchmark_code)
                if not bench_df.empty:
                    return bench_df["adj_close"], benchmark_code
            return None, code
        finally:
            store.close()

    def run_single(self, req: BacktestRequest) -> Dict[str, Any]:
        strat = get_strategy(req.strategy)
        if strat is None:
            raise ValueError(f"未知策略: {req.strategy}")
        params = strat.normalize(req.params)

        store = self._store()
        try:
            df = load_adjusted_ohlc(store, req.code)
        finally:
            store.close()
        if df.empty:
            raise ValueError(f"标的 {req.code} 无日K线数据，请先更新数据")

        config = self._config(req)
        bench_adj_close, benchmark_code = self._benchmark(req.code, req.benchmark_code)
        sig = strat.generate_signals(df, **params)
        res = run_backtest(df, sig, config, bench_adj_close=bench_adj_close)

        return _build_result(req, config, params, res, df, benchmark_code)

    def run_grid(self, req: GridRequest) -> Dict[str, Any]:
        strat = get_strategy(req.strategy)
        if strat is None:
            raise ValueError(f"未知策略: {req.strategy}")

        combos = make_grid(req.param_grids)
        combos = [{**req.fixed_params, **c} for c in combos]
        if len(combos) > req.limit:
            combos = combos[: req.limit]
        if not combos:
            raise ValueError("参数网格为空")

        store = self._store()
        try:
            df = load_adjusted_ohlc(store, req.code)
        finally:
            store.close()
        if df.empty:
            raise ValueError(f"标的 {req.code} 无日K线数据，请先更新数据")

        config = self._config(req)
        bench_adj_close, benchmark_code = self._benchmark(req.code, req.benchmark_code)
        rows = run_grid(df, strat, combos, config, bench_adj_close=bench_adj_close,
                        sort_by=req.sort_by, limit=req.limit)
        return {
            "code": req.code, "strategy": req.strategy,
            "paramNames": list(req.param_grids.keys()),
            "sortBy": req.sort_by, "metricFields": METRIC_FIELDS,
            "benchmarkCode": benchmark_code,
            "rows": [{k: _clean(v) for k, v in row.items()} for row in rows],
        }


def _build_result(req, config: BacktestConfig, params, res, df, benchmark_code) -> Dict:
    def series_pairs(series, other=None):
        return [
            {"date": str(d.date()),
             "strategy": round(float(v), 6),
             **({"benchmark": round(float(o), 6)} if other is not None else {})}
            for d, v, o in zip(series.index, series.values,
                               other.values if other is not None else series.values)
        ]

    nav = res["nav"]
    drawdown = res["drawdown"]
    bench_drawdown = res.get("bench_drawdown")
    position = res["position"]
    metrics = {k: _clean(v) for k, v in res["metrics"].items()}

    return {
        "meta": {
            "code": req.code, "strategy": req.strategy, "params": params,
            "dataStart": str(df.index[0].date()), "dataEnd": str(df.index[-1].date()),
            "cost": {
                "commissionRate": config.commission_rate,
                "minCommission": config.min_commission,
                "slippage": config.slippage,
                "limitPct": config.limit_pct,
                "initialCapital": config.initial_capital,
                "rfAnnual": config.rf_annual,
            },
        },
        "metrics": metrics,
        "benchmarkCode": benchmark_code,
        "nav": series_pairs(nav, res.get("bench_nav")),
        "drawdown": series_pairs(drawdown, bench_drawdown),
        "position": [{"date": str(d.date()), "position": float(p)}
                     for d, p in zip(position.index, position.values)],
        "trades": res["trades"],
    }
