// 策略模块类型定义
import { Bar, Tick } from "../data/types";
import { Order, Trade } from "../trade/types";
export interface Strategy {
  onBar(bar: Bar): void;
  onTick?(tick: Tick): void;
  onOrder?(order: Order): void;
  onTrade?(trade: Trade): void;
  params?: Record<string, any>;
}
