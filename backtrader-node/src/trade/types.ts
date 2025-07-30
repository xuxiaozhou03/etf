// 交易模块类型定义

/**
 * 订单类型
 * - LIMIT: 限价单
 * - MARKET: 市价单
 * - STOP: 止损单
 */
export type OrderType = "LIMIT" | "MARKET" | "STOP";

/**
 * 订单接口
 * @property id 订单唯一标识
 * @property symbol 交易标的代码
 * @property type 订单类型
 * @property price 下单价格（市价单可选）
 * @property volume 下单数量
 * @property status 订单状态
 * @property time 下单时间
 */
export interface Order {
  id: string;
  symbol: string;
  type: OrderType;
  price?: number;
  volume: number;
  status: "NEW" | "FILLED" | "CANCELLED" | "PARTIAL";
  time: Date;
}

/**
 * 持仓接口
 * @property symbol 交易标的代码
 * @property volume 持仓数量
 * @property avgPrice 持仓均价
 * @property pnl 持仓盈亏
 */
export interface Position {
  symbol: string;
  volume: number;
  avgPrice: number;
  pnl: number;
}

/**
 * 成交接口
 * @property orderId 关联订单ID
 * @property symbol 交易标的代码
 * @property price 成交价格
 * @property volume 成交数量
 * @property time 成交时间
 */
export interface Trade {
  orderId: string;
  symbol: string;
  price: number;
  volume: number;
  time: Date;
}
