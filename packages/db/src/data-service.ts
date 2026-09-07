// @quant-backtest/db —— 数据服务（骨架）
// 完整实现见 docs/03 §3：loadCandles / getPeriodReturns / getRanking / getMultiPeriodRanking 等。

import { DailyCandle } from "@quant-backtest/core";

export interface DataLoadConfig {
  code: string;
  startDate?: number;
  endDate?: number;
  limit?: number;
}

export class DataService {
  // TODO(骨架)：实现 loadCandles / loadMultipleCandles / getPeriodReturns /
  // getReturnSummary / getRanking / getMultiPeriodRanking / getComparison /
  // getAvailableSymbols / getDateRange / getETFList / disconnect

  async loadCandles(_config: DataLoadConfig): Promise<DailyCandle[]> {
    throw new Error("TODO(骨架): 实现 DataService.loadCandles");
  }

  async disconnect(): Promise<void> {
    throw new Error("TODO(骨架): 实现 DataService.disconnect");
  }
}
