// 回测模块类型定义
import { Strategy } from "../strategy/types";
import { PerformanceStats } from "../analysis/types";
import { Trade } from "../trade/types";

export interface BacktestEngine {
  run(
    strategies: Strategy[],
    options: BacktestOptions
  ): Promise<BacktestResult>;
}

export type BacktestOptions = {
  start: Date;
  end: Date;
  initialCash: number;
  symbols: string[];
};

export type BacktestResult = {
  stats: PerformanceStats;
  trades: Trade[];
  logs: string[];
};
