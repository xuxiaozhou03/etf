// @quant-backtest/data —— 日K 抓取（骨架）
// 负责从数据源抓日K 并解析：fetchKlineData（p-retry + 429 限流）、parseKlineResponse、parseDateToInt、incrementDate。
// 只抓不存；写库由 @quant-backtest/crawler 的 DataWriter 完成。

import { Result } from "@quant-backtest/core";

export interface RawKlineItem {
  week: string;
  tradeDate: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  change: number;
  changePercent: number;
}

export interface DataFetchError {
  type: "API_ERROR" | "NETWORK_ERROR" | "PARSE_ERROR";
  code?: string;
  message: string;
}

// TODO(骨架)：实现 fetchKlineData / parseKlineResponse / parseDateToInt / incrementDate
export async function fetchKlineData(
  _code: string,
  _beginDate?: string,
  _count = -1000,
): Promise<Result<RawKlineItem[], DataFetchError>> {
  throw new Error("TODO(骨架): 实现 fetchKlineData");
}
