// @quant-backtest/strategy —— 策略层（骨架）
// 规划见 docs/01：策略定义 / 参数（ConfigurableBaseStrategy）/ 生成信号。
// TODO(骨架)：后续实现 Action / Signal 生产逻辑，见 docs/04。

export interface BaseStrategy {
  // TODO(骨架)
  // init(ctx: StrategyContext): Promise<void>;
  // onBar(bar: DailyCandle): Promise<Action[]>;
  // onComplete(ctx: StrategyContext): Promise<void>;
}

export const VERSION = "0.1.0";

/** @deprecated 占位导出，确保可构建 */
export function placeholderStrategy(): void {
  throw new Error("TODO(骨架): strategy 层尚未实现");
}
