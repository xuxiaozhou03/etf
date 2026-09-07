// @quant-backtest/result —— 结果/绩效层（骨架）
// 规划：QuantResult、日频快照、基准对比、收益计算。
// TODO(骨架)：实现结果聚合与绩效计算。

export interface QuantResult {
  // TODO(骨架)
  // totalReturn: number;
  // annualReturn: number;
  // maxDrawdown: number;
  // sharpe: number;
}

export const VERSION = "0.1.0";

/** @deprecated 占位导出，确保可构建 */
export function placeholderResult(): void {
  throw new Error("TODO(骨架): result 层尚未实现");
}
