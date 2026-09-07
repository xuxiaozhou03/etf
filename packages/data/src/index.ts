// @quant-backtest/data —— 取数层出口：上游 HTTP 抓取解析 + 给回测的读服务。
//   · 抓取（不落库）：etf-fetcher（ETF 列表）/ data-fetcher（日K）
//   · 读服务：DataService（loadCandles 等，供 @quant-backtest/engine 取数）
// 底层 Prisma 见 @quant-backtest/db；调度爬虫与落库编排见 @quant-backtest/crawler。

export * from "./data-fetcher";
export * from "./etf-fetcher";
export * from "./data-service";
