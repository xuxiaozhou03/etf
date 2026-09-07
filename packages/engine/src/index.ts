// @quant-backtest/engine —— 回测引擎（骨架）
// 规划：编排数据→策略→撮合→记账→结果的回测主流程。
// TODO(骨架)：实现 runBacktest 主循环。

export interface BacktestOptions {
  // TODO(骨架)
  // codes: string[];
  // strategyName: string;
  // startDate?: number;
  // endDate?: number;
}

export interface BacktestEngine {
  // TODO(骨架)
  // run(opts: BacktestOptions): Promise<QuantResult>;
}

export const VERSION = "0.1.0";

/** @deprecated 占位导出，确保可构建 */
export function placeholderEngine(): void {
  throw new Error("TODO(骨架): engine 层尚未实现");
}
