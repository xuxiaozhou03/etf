// 数据写入（骨架）
// 完整实现见 docs/02 §5：syncETF / syncETFs / syncETFList / syncAllETFs。

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
