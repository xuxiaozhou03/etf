import { describe, expect, it } from "vitest";
import { buildFeatures } from "./featureEngine";
import { shiftFeatures } from "./shift";
import { yearBaseIndex } from "./utils";
import { Kline } from "./types";

/** 造一根日线，只有 close 参与收益率计算 */
const bar = (date: number, close: number): Kline => ({
  code: "TEST",
  date,
  open: close,
  high: close,
  low: close,
  close,
  volume: 1,
  amount: 1,
  change: 0,
  changePercent: 0,
});

describe("yearBaseIndex", () => {
  const data = [
    bar(20251229, 100),
    bar(20251230, 101),
    bar(20251231, 102),
    bar(20260105, 104),
    bar(20260106, 103),
  ];

  it("基准是上一年最后一个交易日，不是当年第一个交易日", () => {
    // 2026 年的任意一天，基准都应落在 20251231（索引 2）
    expect(yearBaseIndex(data, 3)).toBe(2);
    expect(yearBaseIndex(data, 4)).toBe(2);
  });

  it("数据起点就在本年时返回 -1", () => {
    expect(yearBaseIndex(data, 0)).toBe(-1);
    expect(yearBaseIndex(data, 1)).toBe(-1);
  });

  it("跨年处断档（往前的第一根不是上一年）返回 -1", () => {
    const gapped = [bar(20241231, 100), bar(20260105, 104)];
    expect(yearBaseIndex(gapped, 1)).toBe(-1);
  });
});

describe("buildFeatures · retYtd", () => {
  const klines = [
    bar(20251230, 100),
    bar(20251231, 102),
    bar(20260105, 104),
    bar(20260106, 103),
  ];
  const rows = buildFeatures(klines);

  it("年初第一个交易日就有值（基准是上年末收盘 102）", () => {
    // 旧口径拿 20260105 自己当基准，这天会算成 null
    expect(rows[2].retYtd).toBeCloseTo(104 / 102 - 1, 12);
  });

  it("包含年初第一天的涨跌幅，等于各日收益连乘", () => {
    const expected = (104 / 102) * (103 / 104) - 1;
    expect(rows[3].retYtd).toBeCloseTo(expected, 12);
  });

  it("数据起点在本年，无基准则为 null", () => {
    expect(rows[0].retYtd).toBeNull();
  });
});

describe("shiftFeatures", () => {
  it("整行右移一格：date=D 的行装的是 D-1 的值", () => {
    const klines = [
      bar(20251230, 100),
      bar(20251231, 102),
      bar(20260105, 104),
    ];
    const raw = buildFeatures(klines);
    const shifted = shiftFeatures(raw);

    expect(shifted[1].retYtd).toBe(raw[0].retYtd);
    expect(shifted[2].retYtd).toBe(raw[1].retYtd);
  });

  it("首行特征被清空", () => {
    const shifted = shiftFeatures(buildFeatures([bar(20260105, 100)]));
    expect(shifted[0].retYtd).toBeNull();
  });
});
