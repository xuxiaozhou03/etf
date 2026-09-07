// @quant-backtest/presentation —— 展示/报表层（骨架）
// 规划见 docs/01：HTML 报告、榜单、可视化数据。
// TODO(骨架)：实现报告渲染（docs/07）。

export interface ReportRenderer {
  // TODO(骨架)
  // render(quantResult: QuantResult, comparisons: BenchmarkComparison[]): Promise<string>;
}

export const VERSION = "0.1.0";

/** @deprecated 占位导出，确保可构建 */
export function placeholderPresentation(): void {
  throw new Error("TODO(骨架): presentation 层尚未实现");
}
