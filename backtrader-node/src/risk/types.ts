// 风控模块类型定义
import { Order, Position } from "../trade/types";
export interface RiskRule {
  check(order: Order, positions: Position[]): boolean;
  name: string;
}
