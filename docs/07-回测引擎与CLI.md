# 07-回测引擎与CLI

## 📖 文档概述

本文档详细描述量化回测系统的**回测引擎**和**命令行工具**，涵盖回测流程编排、策略生命周期管理、组合回测以及CLI命令的设计与实现。

**目标读者：** 全栈/后端开发工程师

## 1. 概述

### 1.1 回测引擎职责

| 职责                 | 说明                                          |
| :------------------- | :-------------------------------------------- |
| **流程编排**         | 协调数据层、策略层、执行层、结果层的协作      |
| **策略生命周期管理** | 管理策略的init/next/onOrderFilled/cleanup调用 |
| **上下文构建**       | 为策略构建决策上下文（AdviceContext）         |
| **结果整合**         | 整合执行结果并调用结果层分析                  |
| **组合回测**         | 支持多标的组合回测                            |

### 1.2 CLI职责

| 职责           | 说明                       |
| :------------- | :------------------------- |
| **命令行入口** | 提供统一的命令行界面       |
| **配置管理**   | 加载和管理回测配置         |
| **数据同步**   | 同步ETF列表和K线数据       |
| **批量回测**   | 支持批量运行多个策略或标的 |
| **参数优化**   | 运行参数优化任务           |

### 1.3 回测流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        回测流程                                 │
│                                                               │
│  1. 加载数据                                                   │
│     DataService.loadCandles() → DailyCandle[]                 │
│                                                               │
│  2. 初始化                                                     │
│     创建策略实例 → strategy.init()                             │
│     创建执行器 → new BacktestExecutor()                        │
│                                                               │
│  3. 回测循环 (每个交易日)                                      │
│     a. 构建上下文                                              │
│     b. 风控检查 → strategy.onRiskCheck()                      │
│     c. 策略决策 → strategy.next() → Signal                    │
│     d. 执行交易 → executor.executeSignal()                    │
│     e. 成交回调 → strategy.onOrderFilled()                    │
│     f. 持仓监控 → strategy.onPositionMonitor()                │
│     g. 生成快照 → executor.snapshot()                         │
│     h. 重置每日状态 → strategy.resetDailyState()              │
│                                                               │
│  4. 结果分析                                                   │
│     executor.getResult() → ExecutionResultData                │
│     analyzer.analyze() → QuantResult                          │
│                                                               │
│  5. 清理                                                       │
│     strategy.cleanup()                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 回测引擎实现

```typescript
// packages/engine/src/backtest-engine.ts

import {
  DailyCandle,
  AdviceContext,
  Balance,
  Positions,
  Signal,
  FilledOrder,
  FeeConfig,
  ExecutionResultData,
  QuantResult,
} from "@quant-backtest/core";
import { Strategy } from "@quant-backtest/strategy";
import { DataService } from "@quant-backtest/data";
import { BacktestExecutor } from "@quant-backtest/execution";
import { ResultAnalyzer, EnhancedResultAnalyzer } from "@quant-backtest/result";
import { BaseStrategy } from "@quant-backtest/strategy";

/**
 * 回测配置
 */
export interface BacktestConfig {
  /** 初始本金 */
  initialCash: number;
  /** 手续费配置 */
  feeConfig: FeeConfig;
  /** 股票代码 */
  symbol: string;
  /** 开始日期 YYYYMMDD */
  startDate: number;
  /** 结束日期 YYYYMMDD */
  endDate: number;
  /** 是否输出详细日志 */
  verbose?: boolean;
  /** 基准配置（可选） */
  benchmark?: {
    name: string;
    data: Array<{ date: Date; value: number }>;
  };
}

/**
 * 回测引擎
 * 负责回测流程的编排
 */
export class BacktestEngine {
  private dataService: DataService;
  private executor: BacktestExecutor | null = null;

  constructor(dataService: DataService) {
    this.dataService = dataService;
  }

  /**
   * 运行回测
   * @param strategy - 策略实例
   * @param config - 回测配置
   * @returns 量化分析结果
   */
  async run(strategy: Strategy, config: BacktestConfig): Promise<QuantResult> {
    const {
      symbol,
      initialCash,
      feeConfig,
      startDate,
      endDate,
      verbose = false,
      benchmark,
    } = config;

    // 1. 加载数据
    const candles = await this.dataService.loadCandles({
      code: symbol,
      startDate,
      endDate,
    });

    if (candles.length === 0) {
      throw new Error(
        `未找到股票 ${symbol} 在 ${startDate} ~ ${endDate} 的数据`,
      );
    }

    if (verbose) {
      console.log(`📊 加载 ${candles.length} 条K线数据`);
    }

    // 2. 验证数据
    const validation = this.dataService.validate(candles);
    if (!validation.isValid) {
      throw new Error(`数据验证失败: ${validation.errors.join("; ")}`);
    }

    // 3. 初始化执行器
    this.executor = new BacktestExecutor(initialCash, feeConfig);

    // 4. 初始化策略
    if (strategy.init) {
      strategy.init();
      if (verbose)
        console.log(`✅ 策略 ${strategy.name || "未命名"} 初始化完成`);
    }

    // 5. 回测循环
    for (let i = 0; i < candles.length; i++) {
      const candle = candles[i];

      // 构建上下文
      const context = this.buildContext(candle, candles.slice(0, i + 1));

      // 5a. 每日风控检查
      if (strategy.onRiskCheck) {
        const riskAction = strategy.onRiskCheck(context);
        if (riskAction?.signal) {
          const result = this.executor.executeSignal(riskAction.signal, candle);
          if (result.success && strategy.onOrderFilled) {
            strategy.onOrderFilled(result.order);
          } else if (!result.success && verbose) {
            console.warn(`⚠️ 风控执行失败: ${result.message}`);
          }
          // 风控交易后，跳过当日策略交易
          if (riskAction.signal) {
            this.recordSnapshot(candle, this.executor);
            this.resetStrategyState(strategy);
            continue;
          }
        }
      }

      // 5b. 策略决策
      const signal = strategy.next(candle, context);

      // 5c. 执行交易
      if (signal) {
        const result = this.executor.executeSignal(signal, candle);
        if (result.success) {
          if (strategy.onOrderFilled) {
            strategy.onOrderFilled(result.order);
          }
          if (verbose) {
            console.log(
              `[${new Date(candle.date).toISOString().split("T")[0]}] ` +
                `${signal.action === "buy" ? "买入" : "卖出"} ${signal.quantity}股 @ ${signal.price.toFixed(2)}`,
            );
          }
        } else {
          if (verbose) {
            console.warn(
              `⚠️ 交易执行失败: ${result.reason} - ${result.message}`,
            );
          }
        }
      }

      // 5d. 持仓监控
      if (strategy.onPositionMonitor) {
        const position = this.executor.getAccount().positions.get(symbol);
        if (position) {
          const monitorSignal = strategy.onPositionMonitor(position, context);
          if (monitorSignal) {
            const result = this.executor.executeSignal(monitorSignal, candle);
            if (result.success && strategy.onOrderFilled) {
              strategy.onOrderFilled(result.order);
            }
          }
        }
      }

      // 5e. 生成每日快照
      this.recordSnapshot(candle, this.executor);

      // 5f. 重置策略每日状态
      this.resetStrategyState(strategy);
    }

    // 6. 获取执行结果
    const executionResult = this.executor.getResult();

    // 7. 分析结果
    let quantResult: QuantResult;
    if (benchmark) {
      const analyzer = new EnhancedResultAnalyzer();
      quantResult = analyzer.analyzeWithBenchmark(
        executionResult,
        initialCash,
        benchmark,
      );
    } else {
      const analyzer = new ResultAnalyzer();
      quantResult = analyzer.analyze(executionResult, initialCash);
    }

    // 8. 清理策略
    if (strategy.cleanup) {
      strategy.cleanup();
      if (verbose) console.log(`✅ 策略 ${strategy.name || "未命名"} 清理完成`);
    }

    if (verbose) {
      console.log(
        `✅ 回测完成! 总收益率: ${(quantResult.totalReturn * 100).toFixed(2)}%`,
      );
    }

    return quantResult;
  }

  /**
   * 构建决策上下文
   */
  private buildContext(
    candle: DailyCandle,
    history: DailyCandle[],
  ): AdviceContext {
    const account = this.executor!.getAccount();

    // 计算总资产
    let marketValue = 0;
    for (const [symbol, pos] of account.positions) {
      const price = symbol === candle.symbol ? candle.close : 0;
      marketValue += pos.quantity * price;
    }
    const totalAssets = account.cash + marketValue;

    // 构建持仓信息
    const positions: Positions = {};
    for (const [symbol, pos] of account.positions) {
      const price = symbol === candle.symbol ? candle.close : 0;
      const marketValue2 = pos.quantity * price;
      positions[symbol] = {
        quantity: pos.quantity,
        costPrice: pos.costPrice,
        profit: marketValue2 - pos.totalCost,
        totalCost: pos.totalCost,
      };
    }

    return {
      symbol: candle.symbol,
      balances: {
        free: account.cash,
        total: totalAssets,
      },
      positions,
      historyCandles: history,
      currentDate: new Date(candle.date),
    };
  }

  /**
   * 记录每日快照
   */
  private recordSnapshot(
    candle: DailyCandle,
    executor: BacktestExecutor,
  ): void {
    const prices = new Map<string, number>();
    prices.set(candle.symbol, candle.close);
    // 如果有其他持仓，需要获取它们的价格
    for (const [symbol] of executor.getAccount().positions) {
      if (symbol !== candle.symbol) {
        // 从历史数据中获取价格
        const history = this.executor?.getAccount()?.positions?.get(symbol);
        // 简化处理：使用最近的收盘价
        prices.set(symbol, candle.close);
      }
    }
    executor.snapshot(new Date(candle.date), prices);
  }

  /**
   * 重置策略每日状态
   */
  private resetStrategyState(strategy: Strategy): void {
    if (strategy instanceof BaseStrategy) {
      strategy.resetDailyState();
    }
  }

  /**
   * 获取执行结果（分析前）
   */
  getExecutionResult(): ExecutionResultData | null {
    return this.executor?.getResult() || null;
  }
}
```

## 3. 组合回测引擎

```typescript
// packages/engine/src/portfolio-backtest-engine.ts

import {
  DailyCandle,
  PortfolioContext,
  PortfolioSignal,
  FeeConfig,
  ExecutionResultData,
  QuantResult,
} from "@quant-backtest/core";
import { PortfolioStrategy } from "@quant-backtest/strategy";
import { DataService } from "@quant-backtest/data";
import { PortfolioExecutor } from "@quant-backtest/execution";
import { ResultAnalyzer } from "@quant-backtest/result";

/**
 * 组合回测配置
 */
export interface PortfolioBacktestConfig {
  /** 初始本金 */
  initialCash: number;
  /** 手续费配置 */
  feeConfig: FeeConfig;
  /** 股票代码列表 */
  symbols: string[];
  /** 开始日期 YYYYMMDD */
  startDate: number;
  /** 结束日期 YYYYMMDD */
  endDate: number;
  /** 是否输出详细日志 */
  verbose?: boolean;
}

/**
 * 组合回测引擎
 * 支持多只股票同时回测
 */
export class PortfolioBacktestEngine {
  private dataService: DataService;
  private executor: PortfolioExecutor | null = null;

  constructor(dataService: DataService) {
    this.dataService = dataService;
  }

  /**
   * 运行组合回测
   */
  async run(
    strategy: PortfolioStrategy,
    config: PortfolioBacktestConfig,
  ): Promise<QuantResult> {
    const {
      symbols,
      initialCash,
      feeConfig,
      startDate,
      endDate,
      verbose = false,
    } = config;

    // 1. 加载所有股票数据
    const allCandles = await this.dataService.loadMultipleCandles(
      symbols,
      startDate,
      endDate,
    );

    // 2. 验证数据
    for (const [symbol, candles] of allCandles) {
      if (candles.length === 0) {
        throw new Error(`未找到股票 ${symbol} 的数据`);
      }
      const validation = this.dataService.validate(candles);
      if (!validation.isValid) {
        throw new Error(
          `股票 ${symbol} 数据验证失败: ${validation.errors.join("; ")}`,
        );
      }
    }

    if (verbose) {
      console.log(`📊 加载 ${allCandles.size} 只股票的数据`);
    }

    // 3. 初始化执行器
    this.executor = new PortfolioExecutor(initialCash, feeConfig);

    // 4. 初始化策略
    if (strategy.init) {
      strategy.init(symbols);
      if (verbose)
        console.log(`✅ 组合策略 ${strategy.name || "未命名"} 初始化完成`);
    }

    // 5. 获取所有日期（取所有股票日期的并集）
    const allDates = this.getAllDates(allCandles);

    // 6. 回测循环
    for (const date of allDates) {
      // 构建当日所有股票的K线数据
      const todayCandles = new Map<string, DailyCandle>();
      for (const [symbol, candles] of allCandles) {
        const candle = candles.find((c) => c.date === date);
        if (candle) {
          todayCandles.set(symbol, candle);
        }
      }

      if (todayCandles.size === 0) continue;

      // 构建组合上下文
      const context = this.buildPortfolioContext(todayCandles);

      // 策略决策
      const signals = strategy.next(todayCandles, context);

      // 执行交易
      if (signals) {
        const results = this.executor.executePortfolioSignal(
          signals,
          todayCandles,
        );
        for (const [symbol, result] of results) {
          if (result.success && strategy.onOrderFilled) {
            strategy.onOrderFilled(result.order);
          } else if (!result.success && verbose) {
            console.warn(`[${symbol}] 交易失败: ${result.message}`);
          }
        }
      }

      // 生成每日快照
      const prices = new Map<string, number>();
      for (const [symbol, candle] of todayCandles) {
        prices.set(symbol, candle.close);
      }
      this.executor.snapshot(new Date(date), prices);
    }

    // 7. 获取执行结果
    const executionResult = this.executor.getResult();

    // 8. 分析结果
    const analyzer = new ResultAnalyzer();
    const quantResult = analyzer.analyze(executionResult, initialCash);

    // 9. 清理策略
    if (strategy.cleanup) {
      strategy.cleanup();
      if (verbose)
        console.log(`✅ 组合策略 ${strategy.name || "未命名"} 清理完成`);
    }

    if (verbose) {
      console.log(
        `✅ 组合回测完成! 总收益率: ${(quantResult.totalReturn * 100).toFixed(2)}%`,
      );
    }

    return quantResult;
  }

  /**
   * 获取所有日期
   */
  private getAllDates(allCandles: Map<string, DailyCandle[]>): number[] {
    const dateSet = new Set<number>();
    for (const [, candles] of allCandles) {
      for (const c of candles) {
        dateSet.add(c.date);
      }
    }
    return Array.from(dateSet).sort((a, b) => a - b);
  }

  /**
   * 构建组合上下文
   */
  private buildPortfolioContext(
    todayCandles: Map<string, DailyCandle>,
  ): PortfolioContext {
    const account = this.executor!.getAccount();
    const symbols = Array.from(todayCandles.keys());

    // 计算总资产
    let marketValue = 0;
    const positions: any = {};
    for (const [symbol, pos] of account.positions) {
      const price = todayCandles.get(symbol)?.close || 0;
      const mv = pos.quantity * price;
      marketValue += mv;
      positions[symbol] = {
        quantity: pos.quantity,
        costPrice: pos.costPrice,
        profit: mv - pos.totalCost,
        totalCost: pos.totalCost,
      };
    }

    const totalAssets = account.cash + marketValue;

    return {
      symbols,
      balances: {
        free: account.cash,
        total: totalAssets,
      },
      positions,
      historyCandles: new Map(),
      currentDate: new Date(),
    };
  }

  /**
   * 获取执行结果
   */
  getExecutionResult(): ExecutionResultData | null {
    return this.executor?.getResult() || null;
  }
}
```

## 4. CLI工具实现

```typescript
// packages/cli/src/index.ts

import { Command } from "commander";
import {
  DataService,
  DataWriter,
  ETFFilterOptions,
} from "@quant-backtest/data";
import { BacktestEngine } from "@quant-backtest/engine";
import { ConsolePresenter } from "@quant-backtest/presentation";
import { FeeConfig } from "@quant-backtest/core";
import { SafeDoubleMAStrategy } from "./strategies/safe-double-ma";

const program = new Command();

program.name("quant").description("量化回测系统 CLI").version("5.2.0");

// ============================================================
// sync 命令 - 同步K线数据
// ============================================================

program
  .command("sync")
  .description("同步ETF K线数据")
  .option("-c, --code <code>", "股票代码")
  .option("-n, --name <name>", "ETF名称")
  .option("--config <path>", "配置文件路径（JSON）")
  .option("--incremental", "增量同步", true)
  .option("--full", "全量同步")
  .option("--begin <date>", "开始日期 YYYYMMDD")
  .action(async (options) => {
    const dataWriter = new DataWriter();

    try {
      if (options.config) {
        // 从配置文件批量同步
        const config = JSON.parse(await Bun.file(options.config).text());
        const result = await dataWriter.syncETFs(config.etfs, {
          incremental: !options.full,
          beginDate: options.begin,
        });
        console.log(
          `✅ 同步完成: ${result.success.length} 个成功, ${result.failed.length} 个失败`,
        );
      } else if (options.code && options.name) {
        // 单只ETF同步
        const result = await dataWriter.syncETF(options.code, options.name, {
          incremental: !options.full,
          beginDate: options.begin,
        });
        if (result.ok) {
          console.log(
            `✅ ${options.code} 同步完成: 新增 ${result.value.klineInserted} 条`,
          );
        } else {
          console.error(`❌ 同步失败: ${result.error}`);
        }
      } else {
        console.error("请指定 --code 和 --name，或 --config");
      }
    } finally {
      await dataWriter.disconnect();
    }
  });

// ============================================================
// sync:etfs 命令 - 同步ETF列表
// ============================================================

program
  .command("sync:etfs")
  .description("同步ETF列表")
  .option("--min-scale <number>", "最小规模（亿元）", "3")
  .option("--no-filter-null", "不过滤trackingIndex为null")
  .option("--no-keep-largest", "不按指数去重")
  .option("--sync-kline", "同步K线数据")
  .option("--begin <date>", "K线同步开始日期")
  .action(async (options) => {
    const dataWriter = new DataWriter();

    try {
      const filterOptions: ETFFilterOptions = {
        minScale: parseFloat(options.minScale),
        filterNullTracking: options.filterNull,
        keepLargestByIndex: options.keepLargest,
      };

      if (options.syncKline) {
        const result = await dataWriter.syncAllETFs({
          ...filterOptions,
          syncKline: true,
          klineBeginDate: options.begin,
        });
        console.log(`✅ ETF列表: ${result.etfListResult.total} 只`);
        console.log(
          `✅ K线同步: ${result.klineResults.filter((r) => r.success).length}/${result.klineResults.length}`,
        );
      } else {
        const result = await dataWriter.syncETFList(filterOptions);
        if (result.ok) {
          console.log(`✅ 同步完成: ${result.value.total} 只ETF`);
          for (const etf of result.value.etfs) {
            console.log(
              `  ${etf.code} ${etf.name} | ${etf.category} | ${(etf.scale / 1e8).toFixed(1)}亿`,
            );
          }
        } else {
          console.error(`❌ 同步失败: ${result.error}`);
        }
      }
    } finally {
      await dataWriter.disconnect();
    }
  });

// ============================================================
// backtest 命令 - 运行回测
// ============================================================

program
  .command("backtest")
  .description("运行回测")
  .option("-c, --code <code>", "股票代码", "510300.SH")
  .option("--start <date>", "开始日期 YYYYMMDD", "20240101")
  .option("--end <date>", "结束日期 YYYYMMDD", "20241231")
  .option("--initial-cash <amount>", "初始本金", "100000")
  .option("--strategy <name>", "策略名称", "safe-ma")
  .option("--config <path>", "配置文件路径")
  .option("--verbose", "详细日志", false)
  .action(async (options) => {
    const dataService = new DataService();

    try {
      // 构建策略
      let strategy: any;
      if (options.strategy === "safe-ma") {
        strategy = new SafeDoubleMAStrategy(5, 20, {
          stopLossRate: 0.05,
          takeProfitRate: 0.1,
          maxPositionRate: 0.8,
        });
      } else {
        console.error(`未知策略: ${options.strategy}`);
        return;
      }

      // 构建配置
      const feeConfig: FeeConfig = {
        commissionRate: 0.00025,
        minCommission: 5,
        stampTaxRate: 0.001,
        transferFeeRate: 0.00001,
      };

      const config = {
        symbol: options.code,
        initialCash: parseFloat(options.initialCash),
        feeConfig,
        startDate: parseInt(options.start),
        endDate: parseInt(options.end),
        verbose: options.verbose,
      };

      // 运行回测
      const engine = new BacktestEngine(dataService);
      console.log(`🚀 开始回测 ${options.code}...`);
      const result = await engine.run(strategy, config);

      // 展示结果
      const presenter = new ConsolePresenter();
      presenter.printReport(result, {
        showTrades: options.verbose,
        precision: 2,
      });
    } finally {
      await dataService.disconnect();
    }
  });

// ============================================================
// ranking 命令 - 查看排行榜
// ============================================================

program
  .command("ranking")
  .description("查看ETF排行榜")
  .option(
    "--period <type>",
    "周期类型: weekly/monthly/quarterly/yearly/ytd",
    "monthly",
  )
  .option("--key <key>", "周期标识，如 2024-12")
  .option("--limit <number>", "返回数量", "20")
  .option("--category <category>", "分类筛选")
  .option("--market <market>", "市场筛选 SH/SZ")
  .option("--min-days <number>", "最少交易天数", "10")
  .action(async (options) => {
    const dataService = new DataService();

    try {
      const result = await dataService.getRanking({
        periodType: options.period,
        periodKey: options.key,
        sortBy: "monthlyReturn",
        order: "desc",
        limit: parseInt(options.limit),
        minTradeDays: parseInt(options.minDays),
        category: options.category,
        market: options.market,
      });

      if (result.ok) {
        console.log(
          `📊 ${options.period} 收益排行 (${options.key || "最新"}):`,
        );
        console.log("  排名\t代码\t名称\t收益\t天数");
        result.value.forEach((item, index) => {
          console.log(
            `  ${(index + 1).toString().padStart(3)}\t${item.code}\t${item.name.slice(0, 10)}\t${(item.returnRate * 100).toFixed(2)}%\t${item.tradeDays}天`,
          );
        });
      } else {
        console.error(`❌ 查询失败: ${result.error}`);
      }
    } finally {
      await dataService.disconnect();
    }
  });

// ============================================================
// compare 命令 - 对比分析
// ============================================================

program
  .command("compare")
  .description("对比多个ETF收益")
  .option("-c, --codes <codes>", "股票代码列表，逗号分隔")
  .option("--months <months>", "月份列表，逗号分隔")
  .action(async (options) => {
    const dataService = new DataService();

    try {
      const codes = options.codes.split(",").map((s: string) => s.trim());
      const months = options.months.split(",").map((s: string) => s.trim());

      const comparison = await dataService.getComparison(codes, months);

      console.log("📊 多ETF收益对比:");
      console.log("代码\t" + months.join("\t"));
      for (const [code, returns] of comparison) {
        const row = months.map((m) => {
          const r = returns.get(m);
          return r !== undefined ? `${(r * 100).toFixed(2)}%` : "-";
        });
        console.log(`${code}\t${row.join("\t")}`);
      }
    } finally {
      await dataService.disconnect();
    }
  });

// ============================================================
// 启动CLI
// ============================================================

program.parse();
```

## 5. 配置文件示例

```json
// config/backtest.json
{
  "symbol": "510300.SH",
  "initialCash": 100000,
  "startDate": 20240101,
  "endDate": 20241231,
  "strategy": "safe-ma",
  "strategyParams": {
    "shortPeriod": 5,
    "longPeriod": 20,
    "stopLossRate": 0.05,
    "takeProfitRate": 0.1,
    "maxPositionRate": 0.8
  },
  "feeConfig": {
    "commissionRate": 0.00025,
    "minCommission": 5,
    "stampTaxRate": 0.001,
    "transferFeeRate": 0.00001
  }
}
```

```json
// config/etfs.json
{
  "etfs": [
    { "code": "510300.SH", "name": "沪深300ETF华泰柏瑞", "category": "宽基" },
    { "code": "510050.SH", "name": "华夏上证50ETF", "category": "宽基" },
    { "code": "510500.SH", "name": "南方中证500ETF", "category": "宽基" },
    { "code": "513100.SH", "name": "纳指ETF", "category": "跨境" },
    { "code": "513050.SH", "name": "中概互联网ETF", "category": "主题" }
  ]
}
```

## 6. 使用示例

### 6.1 运行回测

```bash
# 基础回测
pnpm backtest --code 510300.SH --start 20240101 --end 20241231

# 带详细日志
pnpm backtest --code 510300.SH --verbose

# 使用配置文件
pnpm backtest --config ./config/backtest.json
```

### 6.2 数据同步

```bash
# 同步ETF列表
pnpm sync:etfs

# 同步ETF列表并拉取K线
pnpm sync:etfs --sync-kline --begin 20200101

# 同步单只ETF
pnpm sync --code 510300.SH --name 沪深300ETF华泰柏瑞

# 批量同步
pnpm sync --config ./config/etfs.json
```

### 6.3 查询排行榜

```bash
# 月度排行
pnpm ranking --period monthly --key 2024-12 --limit 10

# 年度排行
pnpm ranking --period yearly --key 2024 --limit 10

# 按分类筛选
pnpm ranking --period monthly --category 宽基 --limit 10
```

### 6.4 对比分析

```bash
pnpm compare --codes 510300.SH,510050.SH,510500.SH --months 2024-10,2024-11,2024-12
```

## 7. 相关文档

| 序号 | 文档名称                                     | 说明                       |
| :--- | :------------------------------------------- | :------------------------- |
| 01   | [项目总览](./01-项目总览.md)                 | 系统概述、技术架构         |
| 02   | [数据采集与存储层](./02-数据采集与存储层.md) | API采集、SQLite存储        |
| 03   | [数据服务层](./03-数据服务层.md)             | 数据读取、阶段收益、排行榜 |
| 04   | [策略层](./04-策略层.md)                     | 策略接口、风控、参数配置   |
| 05   | [执行层](./05-执行层.md)                     | 模拟交易、账户管理         |
| 06   | [结果与展示层](./06-结果与展示层.md)         | 量化指标、基准对比         |
| 07   | **回测引擎与CLI**                            | 本文档                     |
| 08   | [快速开发指南](./08-快速开发指南.md)         | 开发环境、流程             |

**📌 下一步**：请继续阅读 [08-快速开发指南](./08-快速开发指南.md) 了解开发环境和调试技巧。
