// @quant-backtest/crawler —— 阶段收益计算器（骨架）
// calculateAndSaveAll：基于已入库日K 计算周/月/季/年/YTD 收益并全量重算保存。
// Prisma 来自 @quant-backtest/db；在 sync 落库后调用。

export class PeriodReturnCalculator {
  // TODO(骨架)：实现 calculateAndSaveAll / disconnect
  async calculateAndSaveAll(_code: string): Promise<{
    weekly: number;
    monthly: number;
    quarterly: number;
    yearly: number;
    ytd: number;
  }> {
    throw new Error("TODO(骨架): 实现 PeriodReturnCalculator.calculateAndSaveAll");
  }
}
