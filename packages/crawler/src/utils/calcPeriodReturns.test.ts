import { describe, expect, it } from "vitest";
import { calcPeriodReturns, type KlineBar } from "./calcPeriodReturns";

/** 用 [YYYYMMDD, close] 简写构造 K 线 */
const bars = (...rows: Array<[number, number]>): KlineBar[] =>
  rows.map(([date, close]) => ({ date, close }));

describe("calcPeriodReturns", () => {
  it("无数据 → 空结果", () => {
    expect(calcPeriodReturns([])).toEqual({});
  });

  it("全部脏数据 → 空结果", () => {
    expect(calcPeriodReturns(bars([20240902, 0], [20240903, -1]))).toEqual({});
  });

  it("只有一根 K 线 → 只有成立以来（0%）", () => {
    expect(calcPeriodReturns(bars([20240902, 1.5]))).toEqual({ 成立以来: 0 });
  });

  it("输入乱序也应正确排序", () => {
    const rows: Array<[number, number]> = [
      [20240905, 190],
      [20240906, 180],
      [20240913, 200],
    ];
    expect(calcPeriodReturns(bars(...[...rows].reverse()))).toEqual(
      calcPeriodReturns(bars(...rows)),
    );
  });

  it("近一周：最新日期回退 7 个自然日，取 <= 该日的最后一根", () => {
    // 最新 20240913 → 目标 20240906 → 起点取 20240906 那根
    const ret = calcPeriodReturns(
      bars([20240905, 190], [20240906, 180], [20240913, 200]),
    );
    expect(ret["近一周"]).toBeCloseTo((200 / 180 - 1) * 100, 10);
    expect(ret["成立以来"]).toBeCloseTo((200 / 190 - 1) * 100, 10);
  });

  it("近一月：回退 1 个自然月，月末自动收敛（20240331 → 20240229）", () => {
    // 若 setMonth 溢出成 20240302，起点会落到 20240301 那根 → 结果不同
    const ret = calcPeriodReturns(
      bars([20240229, 100], [20240301, 101], [20240331, 110]),
    );
    expect(ret["近一月"]).toBeCloseTo(10, 10);
  });

  it("近一年：回退 1 个自然年，闰日收敛（20240229 → 20230228）", () => {
    // 若 setFullYear 溢出成 20230301，起点会落到 20230301 那根 → 结果不同
    const ret = calcPeriodReturns(
      bars([20230228, 50], [20230301, 60], [20240229, 120]),
    );
    expect(ret["近一年"]).toBeCloseTo((120 / 50 - 1) * 100, 10);
  });

  it("今年以来：起点是去年最后一个交易日，不是今年第一个交易日", () => {
    const ret = calcPeriodReturns(
      bars(
        [20241230, 100],
        [20241231, 110], // ← 起点
        [20250102, 120],
        [20250912, 132],
      ),
    );
    expect(ret["今年以来"]).toBeCloseTo(20, 10); // 132/110；若取 120 则会得 10
  });

  it("今年以来：跨多个年度时只回退到最近一次年初之前", () => {
    const ret = calcPeriodReturns(
      bars([20231229, 80], [20241231, 110], [20250912, 132]),
    );
    expect(ret["今年以来"]).toBeCloseTo((132 / 110 - 1) * 100, 10);
  });

  it("历史不足的阶段不产出（近一周目标日早于首根 → 无该阶段）", () => {
    const ret = calcPeriodReturns(bars([20240912, 110], [20240913, 120]));
    expect(ret["近一周"]).toBeUndefined();
    expect(ret["近一月"]).toBeUndefined();
    expect(ret["近一年"]).toBeUndefined();
    expect(ret["成立以来"]).toBeCloseTo((120 / 110 - 1) * 100, 10);
  });

  it("历史不足的阶段不产出（有近一周、但无近一月/近一年）", () => {
    const ret = calcPeriodReturns(
      bars([20240901, 100], [20240910, 110], [20240913, 120]),
    );
    // 近一周目标 20240906 → 落在 20240901 那根上
    expect(ret["近一周"]).toBeCloseTo((120 / 100 - 1) * 100, 10);
    expect(ret["近一月"]).toBeUndefined(); // 目标 20240813 早于首根
    expect(ret["近一年"]).toBeUndefined();
    expect(ret["成立以来"]).toBeCloseTo((120 / 100 - 1) * 100, 10);
  });

  it("今年成立的标的：无今年以来", () => {
    const ret = calcPeriodReturns(bars([20250102, 100], [20250912, 130]));
    expect(ret["今年以来"]).toBeUndefined();
    expect(ret["成立以来"]).toBeCloseTo(30, 10);
  });

  it("完整长历史：各阶段均产出，且起点落在预期的那根 K 线上", () => {
    const latestClose = 110;
    const ret = calcPeriodReturns(
      bars(
        [20190102, 10], // 成立以来 / 近五年起点
        [20200914, 20], // 近三年起点
        [20230914, 50], // 近一年起点
        [20241231, 80], // 今年以来起点
        [20250314, 90], // 近三月起点
        [20250614, 95], // 近一月起点
        [20250814, 100], // 近一周起点
        [20250913, latestClose],
      ),
    );

    const expected: Array<[string, number]> = [
      ["近一周", 100],
      ["近一月", 95],
      ["近三月", 90],
      ["近六月", 80],
      ["近一年", 50],
      ["近三年", 20],
      ["近五年", 10],
      ["今年以来", 80],
      ["成立以来", 10],
    ];
    expect(Object.keys(ret)).toEqual(expected.map(([type]) => type));
    for (const [type, startClose] of expected) {
      expect(ret[type as keyof typeof ret]).toBeCloseTo(
        (latestClose / startClose - 1) * 100,
        10,
      );
    }
  });
});
