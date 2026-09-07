// @quant-backtest/db —— 存储基础设施：Prisma schema + 客户端，仅此而已。
// 不承担任何业务读写：取数（DataService）见 @quant-backtest/data，
// 调度与落库（DataWriter / PeriodReturnCalculator）见 @quant-backtest/crawler。

export * from "./client";
