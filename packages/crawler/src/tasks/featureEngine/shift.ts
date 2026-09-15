import { FeatureRow } from "./types";

const FEATURE_KEYS: (keyof FeatureRow)[] = [
  "ma5",
  "ma20",
  "ma60",
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
  "obv",
];

export function shiftFeatures(rows: FeatureRow[]): FeatureRow[] {
  const sorted = [...rows].sort((a, b) => a.date - b.date);
  const out: FeatureRow[] = sorted.map((r) => ({ ...r }));

  for (let i = out.length - 1; i >= 1; i--) {
    for (const key of FEATURE_KEYS) {
      (out[i] as any)[key] = (out[i - 1] as any)[key];
    }
  }
  for (const key of FEATURE_KEYS) {
    (out[0] as any)[key] = null;
  }
  return out;
}
