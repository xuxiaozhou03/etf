// 阶段收益计算器（骨架）
// 完整实现见 docs/02 §6：calculateAndSaveAll（周/月/季/年/YTD 全量重算覆盖）。

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
