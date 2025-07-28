// 结果分析模块类型定义
import { Trade } from "../trade/types";
export type PerformanceStats = {
  totalReturn: number;
  sharpe: number;
  maxDrawdown: number;
  winRate: number;
};

export interface Analysis {
  calculateStats(trades: Trade[]): PerformanceStats;
  plot?(trades: Trade[]): void;
  log?(msg: string): void;
}
