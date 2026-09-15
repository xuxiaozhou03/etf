import { FeatureRow } from "./types";
import { std } from "./utils";

const NORMALIZE_KEYS: (keyof FeatureRow)[] = [
  "ma5_ma20",
  "ma20_ma60",
  "close_ma20",
  "ret1w",
  "ret1m",
  "ret6m",
  "ret1y",
  "retYtd",
  "ret3y",
  "ret6y",
  "retSince",
  "rsi14",
  "vol20",
  "atr14_norm",
  "bb_width20",
  "vol_ratio5",
  "vol_ma5_ma20",
];

export function zscoreByDate(rows: FeatureRow[]): FeatureRow[] {
  const byDate = new Map<number, FeatureRow[]>();
  for (const r of rows) {
    if (!byDate.has(r.date)) byDate.set(r.date, []);
    byDate.get(r.date)!.push(r);
  }

  const out: FeatureRow[] = [];
  for (const [, group] of byDate) {
    for (const key of NORMALIZE_KEYS) {
      const values = group
        .map((r) => r[key] as number | null)
        .filter((v): v is number => v !== null);
      if (values.length < 2) continue;
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const sd = std(values);
      if (sd === 0) continue;
      for (const r of group) {
        const v = r[key] as number | null;
        if (v !== null) (r as any)[key] = (v - mean) / sd;
      }
    }
    out.push(...group);
  }
  return out;
}
