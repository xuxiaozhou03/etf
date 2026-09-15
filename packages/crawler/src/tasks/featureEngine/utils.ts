export function sma(values: number[], n: number): (number | null)[] {
  const out: (number | null)[] = new Array(values.length).fill(null);
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    sum += values[i];
    if (i >= n) sum -= values[i - n];
    if (i >= n - 1) out[i] = sum / n;
  }
  return out;
}

export function ema(values: number[], n: number): number[] {
  const out: number[] = [];
  const k = 2 / (n + 1);
  let prev = values[0];
  out.push(prev);
  for (let i = 1; i < values.length; i++) {
    prev = values[i] * k + prev * (1 - k);
    out.push(prev);
  }
  return out;
}

export function std(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance =
    values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}

export function safeDiv(a: number | null, b: number | null): number | null {
  if (a === null || b === null || b === 0) return null;
  return a / b;
}

export function returns(closes: number[]): (number | null)[] {
  const out: (number | null)[] = [null];
  for (let i = 1; i < closes.length; i++) {
    out.push(closes[i] / closes[i - 1] - 1);
  }
  return out;
}

/** 找到 i 所在年份的第一个交易日索引 */
export function yearStartIndex(data: { date: number }[], i: number): number {
  const year = Math.floor(data[i].date / 10000);
  for (let j = i; j >= 0; j--) {
    if (Math.floor(data[j].date / 10000) !== year) return j + 1;
  }
  return 0;
}
