// 数据采集：K线 API（骨架）
// 完整实现见 docs/02 §3：fetchKlineData（p-retry + 429 限流）、parseKlineResponse、parseDateToInt、incrementDate。

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
