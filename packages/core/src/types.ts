/**
 * 核心类型定义（骨架）
 * 先落系统最常用的集合，其余按文档补齐：
 *  - docs/03 §2   DailyCandle
 *  - docs/04 §2   策略信号/风控/账户
 *  - docs/05 §2   执行/持仓/快照/费用
 *  - docs/06 §2   量化结果/基准对比
 */

/** 交易动作 */
export type Action = "buy" | "sell";

/** 交易信号：策略输出的完整交易指令 */
export interface Signal {
  action: Action;
  /** 交易股数（正数） */
  quantity: number;
  /** 交易价格（复权收盘价） */
  price: number;
  /** 交易理由（用于日志与分析） */
  reason?: string;
}

/** 日K线数据（系统内部格式，date 为 YYYYMMDD 整数） */
export interface DailyCandle {
  symbol: string;
  date: number;
  prevClose: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  /** 复权因子（前复权数据固定 1.0） */
  factor: number;
}

/** 账户余额 */
export interface Balance {
  free: number;
  total: number;
}

/** 持仓信息（按 symbol 索引） */
export interface Positions {
  [symbol: string]: {
    quantity: number;
    costPrice: number;
    profit: number;
    totalCost: number;
  };
}

/** 已成交订单（策略 onOrderFilled 接收） */
export interface FilledOrder {
  orderId: string;
  side: Action;
  symbol: string;
  quantity: number;
  price: number;
  totalAmount: number;
  tradeDate: Date;
  fee: number;
  status: "filled";
  reason?: string;
}

/** 费用配置（A股默认见 docs/05 §3） */
export interface FeeConfig {
  commissionRate: number;
  minCommission: number;
  stampTaxRate: number;
  transferFeeRate: number;
}

// TODO(骨架) 补充：RiskAction / RiskType、AdviceContext、Position、Account、
// TradeRecord、DailySnapshot、SnapshotPosition、ExecutionResult、ExecutionResultData、
// QuantResult、MonthlyReturn、BenchmarkComparison、BenchmarkConfig（依 docs/03~06）。
