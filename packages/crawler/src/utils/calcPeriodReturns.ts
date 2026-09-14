import dayjs from "dayjs";

/**
 * 阶段收益计算（纯函数，不依赖 Prisma）
 *
 * 前提：K 线为**全前复权**且按日期升序。既然是前复权，直接拿区间起点与最新 close 相除即可：
 *   收益率 = (最新 close / 阶段起点 close - 1) * 100
 *
 * 起点口径：
 *  - 近一周/月/三月/六月/一年/三年/五年：最新日期往前推相应自然日/月/年，取 date <= 该日期的最后一根；
 *  - 今年以来：取**去年最后一个交易日**（date < 今年 1/1 的最后一根），这样才包含跨年的完整涨幅；
 *  - 成立以来：第一根 K 线。
 *
 * 当区间起点早于第一根 K 线（该标的成立不足该阶段）时，该阶段**不产出**，由调用方决定不落库。
 */

/** 与 PeriodReturn.periodType 一一对应，顺序即落库顺序 */
export const PERIOD_TYPES = [
  "近一周",
  "近一月",
  "近三月",
  "近六月",
  "近一年",
  "近三年",
  "近五年",
  "今年以来",
  "成立以来",
] as const;

export type PeriodType = (typeof PERIOD_TYPES)[number];

/** 计算所需字段：date 为 YYYYMMDD 数字，close 为前复权收盘价 */
export interface KlineBar {
  date: number;
  close: number;
}

export type PeriodReturns = Partial<Record<PeriodType, number>>;

type ShiftUnit = "day" | "month" | "year";

/** 日历回退口径：自然日 / 自然月 / 自然年 */
const OFFSETS: ReadonlyArray<readonly [PeriodType, number, ShiftUnit]> = [
  ["近一周", 7, "day"],
  ["近一月", 1, "month"],
  ["近三月", 3, "month"],
  ["近六月", 6, "month"],
  ["近一年", 1, "year"],
  ["近三年", 3, "year"],
  ["近五年", 5, "year"],
];

/** YYYYMMDD → dayjs（手工构造本地日期，避免 new Date("20240914") 的解析歧义） */
const fromYmd = (ymd: number): dayjs.Dayjs =>
  dayjs(
    new Date(Math.floor(ymd / 1e4), (Math.floor(ymd / 100) % 100) - 1, ymd % 100),
  );

/** dayjs → YYYYMMDD */
const toYmd = (d: dayjs.Dayjs): number => Number(d.format("YYYYMMDD"));

/** 往前推 n 个日历单位；月末/闰年会自动收敛（如 20240331 回退 1 月 → 20240229） */
const shiftYmd = (ymd: number, n: number, unit: ShiftUnit): number =>
  toYmd(fromYmd(ymd).subtract(n, unit));

export const calcPeriodReturns = (klines: KlineBar[]): PeriodReturns => {
  // 排序兜底 + 剔除脏数据（close <= 0 算不出收益率）
  const data = [...klines]
    .filter((k) => k.close > 0)
    .sort((a, b) => a.date - b.date);
  if (data.length === 0) return {};

  const latest = data[data.length - 1];
  const latestClose = latest.close;

  /** 取 date <= target 的最后一根 K 线；target 早于第一根时返回 null */
  const lastBarAtOrBefore = (target: number): KlineBar | null => {
    let lo = 0;
    let hi = data.length - 1;
    let ans = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (data[mid].date <= target) {
        ans = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    return ans >= 0 ? data[ans] : null;
  };

  const rateFrom = (start: KlineBar | null): number | null =>
    start ? (latestClose / start.close - 1) * 100 : null;

  const result: PeriodReturns = {};

  for (const [periodType, n, unit] of OFFSETS) {
    const rate = rateFrom(lastBarAtOrBefore(shiftYmd(latest.date, n, unit)));
    if (rate !== null) result[periodType] = rate;
  }

  // 今年以来：起点 = 去年最后一个交易日
  const rateYtd = rateFrom(
    lastBarAtOrBefore(toYmd(fromYmd(latest.date).startOf("year").subtract(1, "day"))),
  );
  if (rateYtd !== null) result["今年以来"] = rateYtd;

  // 成立以来：第一根 K 线
  const rateAll = rateFrom(data[0]);
  if (rateAll !== null) result["成立以来"] = rateAll;

  return result;
};
