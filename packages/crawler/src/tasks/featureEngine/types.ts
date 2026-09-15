export interface Kline {
  code: string;
  date: number; // YYYYMMDD
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  change: number;
  changePercent: number;
}

export interface FeatureRow {
  code: string;
  date: number;

  // 均线
  ma5: number | null;
  ma20: number | null;
  ma60: number | null;
  ma5_ma20: number | null;
  ma20_ma60: number | null;
  close_ma20: number | null;

  // 动量 / 区间收益率
  ret1w: number | null; // 近一周
  ret1m: number | null; // 近一月
  ret6m: number | null; // 近6月
  ret1y: number | null; // 近1年
  retYtd: number | null; // 今年来
  ret3y: number | null; // 近3年
  ret6y: number | null; // 近6年
  retSince: number | null; // 成立以来
  rsi14: number | null;

  // 波动率
  vol20: number | null;
  atr14_norm: number | null;
  bb_width20: number | null;

  // 量价
  vol_ratio5: number | null;
  vol_ma5_ma20: number | null;
  obv: number | null;

  // 标签
  label_ret1: number | null;
  label_ret5: number | null;
}
