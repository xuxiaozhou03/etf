// 交易模块类型定义
export type OrderType = "LIMIT" | "MARKET" | "STOP";

export interface Order {
  id: string;
  symbol: string;
  type: OrderType;
  price?: number;
  volume: number;
  status: "NEW" | "FILLED" | "CANCELLED" | "PARTIAL";
  time: Date;
}

export interface Position {
  symbol: string;
  volume: number;
  avgPrice: number;
  pnl: number;
}

export interface Trade {
  orderId: string;
  symbol: string;
  price: number;
  volume: number;
  time: Date;
}
