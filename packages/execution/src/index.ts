// @quant-backtest/execution —— 撮合/执行层（骨架）
// 规划见 docs/01：Bar→Order→成交撮合→持仓/资金更新；手数取整、费用计算。
// TODO(骨架)：实现撮合引擎（FeeConfig / FilledOrder），见 docs/05。

export interface ExecutionEngine {
  // TODO(骨架)
  // execute(action: Action, price: number, date: number): Promise<FilledOrder[]>;
}

export const VERSION = "0.1.0";

/** @deprecated 占位导出，确保可构建 */
export function placeholderExecution(): void {
  throw new Error("TODO(骨架): execution 层尚未实现");
}
