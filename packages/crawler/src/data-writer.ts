// @quant-backtest/crawler —— 数据入库写原语（骨架）
// syncETF / syncETFs / syncETFList / syncAllETFs：把取到的 ETF 列表与日K 写入 DB。
// 取数来自 @quant-backtest/data；调度编排见本层 sync/；Prisma 来自 @quant-backtest/db。

import { Result } from "@quant-backtest/core";

export interface SyncResult {
  code: string;
  name: string;
  klineInserted: number;
  klineUpdated: number;
  periodCount: number;
  isIncremental: boolean;
}

export class DataWriter {
  // TODO(骨架)：实现 syncETF / syncETFs / syncETFList / syncAllETFs / disconnect

  async syncETF(
    _code: string,
    _name: string,
    _options?: {
      market?: string;
      category?: string;
      incremental?: boolean;
      beginDate?: string;
    },
  ): Promise<Result<SyncResult, string>> {
    throw new Error("TODO(骨架): 实现 DataWriter.syncETF");
  }

  async disconnect(): Promise<void> {
    throw new Error("TODO(骨架): 实现 DataWriter.disconnect");
  }
}
