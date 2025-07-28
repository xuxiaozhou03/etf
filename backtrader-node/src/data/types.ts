// 数据模块类型定义
export type Bar = {
  time: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  symbol: string;
};

export type Tick = {
  time: Date;
  price: number;
  volume: number;
  symbol: string;
};

export interface DataSource {
  fetchBars(symbol: string, from: Date, to: Date): Promise<Bar[]>;
  fetchTicks?(symbol: string, from: Date, to: Date): Promise<Tick[]>;
}
