// 扩展接口类型定义
import { Bar } from "../data/types";
export interface Indicator {
  name: string;
  calculate(bars: Bar[]): number[];
}

export interface Plugin {
  name: string;
  install(): void;
}

export interface ExternalAPI {
  fetchRealtime(symbol: string): Promise<any>;
}
