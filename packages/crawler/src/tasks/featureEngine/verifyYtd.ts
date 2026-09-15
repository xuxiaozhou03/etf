/**
 * 「今年来」(retYtd) 口径核对脚本
 *
 * 起因：详情页表格里 2026-08-21 那行显示「涨跌幅 +1.67%、今年来 -2.75%」，
 * 两个数对不上。查下来是两层口径叠在一起：
 *
 *  1) 基准取错：原先 buildFeatures 拿「当年第一个交易日的收盘价」当基准，
 *     而行情软件的标准口径是「上一年最后一个交易日的收盘价」。差的正好是
 *     年初第一天那根涨跌幅被整年丢掉。已改为 yearBaseIndex。
 *  2) shiftFeatures 把整行特征右移一格（防未来函数，模型要用），所以 feature
 *     表里 date=D 的行装的是 D-1 的数据 —— 页面表格没标注这一点，容易误读。
 *
 * 本脚本用 kline 表现算一遍跟 feature 表逐日对账。改了引擎口径之后如果没重跑
 * crawler，这里会直接报「落库值与引擎对不上」。
 *
 * 用法：
 *   pnpm --filter @quant-backtest/crawler verify:ytd
 *   pnpm --filter @quant-backtest/crawler verify:ytd -- --code=510300.SH
 */

import { prisma } from "@quant-backtest/db";
import { buildFeatures } from "./featureEngine";
import { shiftFeatures } from "./shift";
import { Kline } from "./types";

// ---------- 小工具 ----------

const arg = (name: string): string | undefined => {
  const hit = process.argv.find((a) => a.startsWith(`--${name}=`));
  return hit?.slice(name.length + 3);
};

const pct = (v: number | null | undefined): string =>
  v == null ? "—" : `${v >= 0 ? "+" : ""}${(v * 100).toFixed(3)}%`;

const year = (date: number): number => Math.floor(date / 10000);

const fmtDate = (date: number): string => {
  const s = String(date);
  return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
};

/** 当年第一个交易日索引 —— 即修复前的错误基准，留作对照 */
function oldBaseIndex(klines: Kline[], i: number): number {
  const y = year(klines[i].date);
  for (let j = i; j >= 0; j--) {
    if (year(klines[j].date) !== y) return j + 1;
  }
  return 0;
}

// ---------- 主流程 ----------

const CODE = arg("code") ?? "518880.SH";
const FOCUS = (arg("dates") ?? "20260819,20260820,20260821")
  .split(",")
  .map((s) => Number(s.trim()));

const main = async (): Promise<void> => {
  const klines = await prisma.kline.findMany({
    where: { code: CODE },
    orderBy: { date: "asc" },
  });
  if (klines.length === 0) throw new Error(`kline 表里没有 ${CODE} 的数据`);

  const stored = await prisma.feature.findMany({
    where: { code: CODE },
    orderBy: { date: "asc" },
  });
  if (stored.length === 0) throw new Error(`feature 表里没有 ${CODE} 的数据`);

  const idxOf = new Map<number, number>();
  klines.forEach((k, i) => idxOf.set(k.date, i));
  const storedByDate = new Map(stored.map((f) => [f.date, f]));

  // 引擎现算（原始口径 + shift 后口径）
  const raw = buildFeatures(klines);
  const shifted = shiftFeatures(raw);
  const shiftedByDate = new Map(shifted.map((r) => [r.date, r]));

  const lastIdx = klines.length - 1;
  const curYear = year(klines[lastIdx].date);

  // ---- 1. 落库值 vs 引擎复算：应当逐行全等 ----
  let drift = 0;
  for (const f of stored) {
    const r = shiftedByDate.get(f.date);
    if (!r) continue;
    const a = f.retYtd;
    const b = r.retYtd;
    if (a === null && b === null) continue;
    if (a === null || b === null || Math.abs(a - b) > 1e-12) drift++;
  }

  // ---- 2. shift 滞后检验：落库[D] == 引擎原始[D-1] ----
  let shiftHolds = 0;
  let shiftTotal = 0;
  for (let i = 1; i < klines.length; i++) {
    const s = storedByDate.get(klines[i].date);
    if (!s) continue;
    const cur = s.retYtd;
    const prevRaw = raw[i - 1].retYtd;
    if (cur === null && prevRaw === null) continue;
    shiftTotal++;
    if (cur !== null && prevRaw !== null && Math.abs(cur - prevRaw) < 1e-12) {
      shiftHolds++;
    }
  }

  // ---- 3. 口径回归：年初第一个交易日必须有值 ----
  const firstOfYear = klines.findIndex((k) => year(k.date) === curYear);
  const firstOfYearRaw = firstOfYear >= 0 ? raw[firstOfYear].retYtd : null;

  // ---- 输出 ----
  const prevEnd = firstOfYear - 1;
  const oldest = klines.find((k) => year(k.date) === curYear);

  console.log(`\n=== ${CODE}  retYtd 口径核对 ===\n`);
  if (prevEnd >= 0) {
    console.log(
      `基准：上一年最后一个交易日 ${fmtDate(klines[prevEnd].date)} 收盘 ${klines[prevEnd].close}`,
    );
  }
  console.log(
    `当年(${curYear})第一个交易日 ${fmtDate(oldest!.date)} 收盘 ${oldest!.close}` +
      `　（旧口径拿它当基准，现在只作对照）`,
  );

  console.log(
    `\n日期        收盘     当日涨跌   落库retYtd   引擎现算   旧口径(年初首日基准)`,
  );
  for (const d of FOCUS) {
    const i = idxOf.get(d);
    if (i === undefined) {
      console.log(`${fmtDate(d)}   kline 表里没有这天`);
      continue;
    }
    const k = klines[i];
    const oldIdx = oldBaseIndex(klines, i);
    const oldValue = oldIdx < i ? k.close / klines[oldIdx].close - 1 : null;
    console.log(
      [
        fmtDate(d).padEnd(10),
        k.close.toFixed(3).padStart(8),
        pct(k.changePercent / 100).padStart(9),
        pct(storedByDate.get(d)?.retYtd).padStart(11),
        pct(raw[i].retYtd).padStart(10),
        pct(oldValue).padStart(19),
      ].join(" "),
    );
  }

  console.log(`\n--- 对账 ---`);
  console.log(
    `落库值 vs 引擎现算(含 shift)： 不一致 ${drift} 行 / 共 ${stored.length} 行` +
      (drift === 0
        ? "  ✅ 落库数据与当前引擎一致"
        : "  ❌ 口径改了但没重跑 crawler，需重跑 featureEngine"),
  );
  console.log(
    `shift 滞后检验（落库[D] == 引擎原始[D-1]）： 成立 ${shiftHolds} / ${shiftTotal} 行` +
      (shiftHolds === shiftTotal && shiftTotal > 0
        ? "  ✅ 确认滞后一个交易日"
        : "  ❌"),
  );
  console.log(
    `年初第一个交易日 ${fmtDate(oldest!.date)} 的 retYtd： ${pct(firstOfYearRaw)}` +
      (firstOfYearRaw === null
        ? "  ❌ 为 null，基准仍未修好"
        : "  ✅ 有值（旧口径这天是 null）"),
  );

  const i = idxOf.get(FOCUS[FOCUS.length - 1]);
  if (i !== undefined) {
    const k = klines[i];
    console.log(`\n--- ${fmtDate(k.date)} 这个数怎么来的 ---`);
    console.log(
      `  页面显示（特征滞后一天，即 as-of 前一交易日）： ${pct(storedByDate.get(k.date)?.retYtd)}`,
    );
    console.log(
      `  as-of 当日（未去滞后）：                      ${pct(raw[i].retYtd)}`,
    );
  }

  console.log();
  await prisma.$disconnect();
  process.exit(drift === 0 && firstOfYearRaw !== null ? 0 : 1);
};

main().catch(async (err) => {
  console.error(err);
  await prisma.$disconnect();
  process.exit(1);
});
