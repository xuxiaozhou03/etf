// @quant-backtest/data —— 数据读服务（骨架）
// loadCandles / getPeriodReturns / getRanking / getMultiPeriodRanking 等，供回测引擎取数。
// 底层 Prisma 来自 @quant-backtest/db；本层不含调度与写库。

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
