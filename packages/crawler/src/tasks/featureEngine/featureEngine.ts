import { FeatureRow, Kline } from "./types";
import { sma, ema, std, safeDiv, returns, yearStartIndex } from "./utils";

export function buildFeatures(klines: Kline[]): FeatureRow[] {
  const data = [...klines].sort((a, b) => a.date - b.date);
  const n = data.length;

  const close = data.map((k) => k.close);
  const high = data.map((k) => k.high);
  const low = data.map((k) => k.low);
  const volume = data.map((k) => k.volume);

  // ---------- 均线 ----------
  const ma5 = sma(close, 5);
  const ma20 = sma(close, 20);
  const ma60 = sma(close, 60);

  // ---------- 区间收益率 ----------
  const ret1w = new Array<number | null>(n).fill(null);
  const ret1m = new Array<number | null>(n).fill(null);
  const ret6m = new Array<number | null>(n).fill(null);
  const ret1y = new Array<number | null>(n).fill(null);
  const retYtd = new Array<number | null>(n).fill(null);
  const ret3y = new Array<number | null>(n).fill(null);
  const ret6y = new Array<number | null>(n).fill(null);
  const retSince = new Array<number | null>(n).fill(null);

  for (let i = 0; i < n; i++) {
    if (i >= 5) ret1w[i] = close[i] / close[i - 5] - 1;
    if (i >= 20) ret1m[i] = close[i] / close[i - 20] - 1;
    if (i >= 120) ret6m[i] = close[i] / close[i - 120] - 1;
    if (i >= 250) ret1y[i] = close[i] / close[i - 250] - 1;
    if (i >= 750) ret3y[i] = close[i] / close[i - 750] - 1;
    if (i >= 1500) ret6y[i] = close[i] / close[i - 1500] - 1;

    // 今年来
    const startIdx = yearStartIndex(data, i);
    if (startIdx < i) retYtd[i] = close[i] / close[startIdx] - 1;

    // 成立以来
    if (i > 0) retSince[i] = close[i] / close[0] - 1;
  }

  // RSI14
  const rsi14 = new Array<number | null>(n).fill(null);
  {
    const period = 14;
    const gains: number[] = [0];
    const losses: number[] = [0];
    for (let i = 1; i < n; i++) {
      const diff = close[i] - close[i - 1];
      gains.push(Math.max(diff, 0));
      losses.push(Math.max(-diff, 0));
    }
    let avgGain = 0;
    let avgLoss = 0;
    for (let i = 1; i <= period && i < n; i++) {
      avgGain += gains[i];
      avgLoss += losses[i];
    }
    if (n > period) {
      avgGain /= period;
      avgLoss /= period;
      for (let i = period; i < n; i++) {
        if (i > period) {
          avgGain = (avgGain * (period - 1) + gains[i]) / period;
          avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
        }
        if (avgLoss === 0) {
          rsi14[i] = 100;
        } else {
          const rs = avgGain / avgLoss;
          rsi14[i] = 100 - 100 / (1 + rs);
        }
      }
    }
  }

  // ---------- 波动率 ----------
  const dailyRet = returns(close);
  const vol20 = new Array<number | null>(n).fill(null);
  for (let i = 19; i < n; i++) {
    const window = dailyRet
      .slice(i - 19, i + 1)
      .filter((x): x is number => x !== null);
    if (window.length === 20) {
      vol20[i] = std(window) * Math.sqrt(252);
    }
  }

  // ATR14 归一化
  const atr14Norm = new Array<number | null>(n).fill(null);
  {
    const period = 14;
    const tr: number[] = [0];
    for (let i = 1; i < n; i++) {
      const hl = high[i] - low[i];
      const hc = Math.abs(high[i] - close[i - 1]);
      const lc = Math.abs(low[i] - close[i - 1]);
      tr.push(Math.max(hl, hc, lc));
    }
    const atr = ema(tr, period);
    for (let i = 0; i < n; i++) {
      if (i >= period && close[i] !== 0) {
        atr14Norm[i] = atr[i] / close[i];
      }
    }
  }

  // 布林带宽度20
  const bbWidth20 = new Array<number | null>(n).fill(null);
  for (let i = 19; i < n; i++) {
    const window = close.slice(i - 19, i + 1);
    const mid = window.reduce((a, b) => a + b, 0) / 20;
    const sd = std(window);
    if (mid !== 0) {
      bbWidth20[i] = (4 * sd) / mid;
    }
  }

  // ---------- 量价 ----------
  const volMa5 = sma(volume, 5);
  const volMa20 = sma(volume, 20);
  const volRatio5 = new Array<number | null>(n).fill(null);
  const volMa5Ma20 = new Array<number | null>(n).fill(null);
  for (let i = 0; i < n; i++) {
    volRatio5[i] = safeDiv(volume[i], volMa5[i]);
    volMa5Ma20[i] = safeDiv(volMa5[i], volMa20[i]);
  }

  // OBV
  const obv: number[] = [0];
  for (let i = 1; i < n; i++) {
    const prev = obv[i - 1];
    if (close[i] > close[i - 1]) obv.push(prev + volume[i]);
    else if (close[i] < close[i - 1]) obv.push(prev - volume[i]);
    else obv.push(prev);
  }

  // ---------- 标签：未来收益率 ----------
  const labelRet1 = new Array<number | null>(n).fill(null);
  const labelRet5 = new Array<number | null>(n).fill(null);
  for (let i = 0; i < n; i++) {
    if (i + 1 < n) labelRet1[i] = close[i + 1] / close[i] - 1;
    if (i + 5 < n) labelRet5[i] = close[i + 5] / close[i] - 1;
  }

  // ---------- 组装 ----------
  const rows: FeatureRow[] = [];
  for (let i = 0; i < n; i++) {
    rows.push({
      code: data[i].code,
      date: data[i].date,
      ma5: ma5[i],
      ma20: ma20[i],
      ma60: ma60[i],
      ma5_ma20: safeDiv(ma5[i], ma20[i]),
      ma20_ma60: safeDiv(ma20[i], ma60[i]),
      close_ma20: safeDiv(close[i], ma20[i]),
      ret1w: ret1w[i],
      ret1m: ret1m[i],
      ret6m: ret6m[i],
      ret1y: ret1y[i],
      retYtd: retYtd[i],
      ret3y: ret3y[i],
      ret6y: ret6y[i],
      retSince: retSince[i],
      rsi14: rsi14[i],
      vol20: vol20[i],
      atr14_norm: atr14Norm[i],
      bb_width20: bbWidth20[i],
      vol_ratio5: volRatio5[i],
      vol_ma5_ma20: volMa5Ma20[i],
      obv: obv[i],
      label_ret1: labelRet1[i],
      label_ret5: labelRet5[i],
    });
  }

  return rows;
}
