// @quant-backtest/crawler —— 调度爬虫 + 落库出口。
// 职责：编排同步任务（sync/），从 @quant-backtest/data 取数，
// 用本层 DataWriter / PeriodReturnCalculator 写入数据库（Prisma 见 @quant-backtest/db）。
//   · sync/  —— 两阶段调度：etf_list → [code]_kline，含「收盘后已完成 → 跳过」规则
//   · data-writer.ts —— 入库写原语（syncETF / syncETFList 等）
//   · period-return-calculator.ts —— 阶段收益计算并保存

export * from "./sync/types";
export * from "./sync/rule";
export * from "./sync/tasks";
export * from "./sync/scheduler";
export * from "./data-writer";
export * from "./period-return-calculator";
