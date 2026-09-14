import { prisma } from "@quant-backtest/db";
import { Task } from "../utils/runTask";
import { calcPeriodReturns, PERIOD_TYPES } from "../utils/calcPeriodReturns";

export const getEtfCalculatorTask = (code: string): Task => ({
  name: `calculator_${code}`,
  run: async () => {
    const klines = await prisma.kline.findMany({
      where: { code },
      orderBy: { date: "asc" },
      select: { date: true, close: true },
    });

    const returns = calcPeriodReturns(klines);
    const rows = PERIOD_TYPES.flatMap((periodType) => {
      const returnRate = returns[periodType];
      return returnRate === undefined
        ? []
        : [{ code, periodType, returnRate }];
    });

    // 全量覆盖：历史不足的阶段不产出，先清后写避免残留上一轮的旧值
    await prisma.$transaction(async (tx) => {
      await tx.periodReturn.deleteMany({ where: { code } });
      if (rows.length > 0) await tx.periodReturn.createMany({ data: rows });
    });

    const summary = rows
      .map((row) => `${row.periodType} ${row.returnRate.toFixed(2)}%`)
      .join(" | ");
    console.log(
      `[calculator] ${code}（${klines.length} 根 K 线）→ ${summary || "K 线不足，未产出阶段收益"}`,
    );
  },
});
