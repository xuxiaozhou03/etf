// @quant-backtest/crawler —— ETF 列表采集与过滤（骨架）
// 完整实现见 docs/02 §4：分页抓取 + 过滤（trackingIndex≠null、规模>3亿、同指数取最大）+ 类别推断。
// 只负责抓取与过滤，写入 Security 表归 @quant-backtest/data。

import { Result } from "@quant-backtest/core";

export interface RawETFItem {
  securityName: string;
  securityCode: string;
  scale: number;
  trackingIndex: string | null;
  managementFee: string;
  price: string;
  changePercent: string;
  managementcomp: string;
  fundManager: string;
}

export interface FilteredETF {
  code: string;
  name: string;
  market: "SH" | "SZ";
  category: string;
  trackingIndex: string;
  scale: number;
}

export interface ETFFilterOptions {
  minScale?: number; // 默认 3 亿
  filterNullTracking?: boolean; // 默认 true
  keepLargestByIndex?: boolean; // 默认 true
  pageSize?: number; // 默认 100
}

export class ETFFetcher {
  // TODO(骨架)：实现 fetchAllETFs / fetchAndFilter（复用 docs/02 §4 逻辑）
  async fetchAndFilter(
    _options: ETFFilterOptions = {},
  ): Promise<Result<FilteredETF[], string>> {
    throw new Error("TODO(骨架): 实现 ETFFetcher.fetchAndFilter");
  }
}
