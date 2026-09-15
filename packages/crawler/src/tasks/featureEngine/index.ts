import { prisma } from "@quant-backtest/db";
import { Task } from "../../utils/runTask";
import { buildFeatures } from "./featureEngine";
import { shiftFeatures } from "./shift";
import { zscoreByDate } from "./normalize";

// 单个 etf 的数据工程
export const getFeatureEngineTask = (code: string): Task => ({
  name: `featureEngine_${code}`,
  run: async () => {
    const klines = await prisma.kline.findMany({
      where: { code },
      orderBy: { date: "asc" },
    });

    const raw = buildFeatures(klines);
    const shifted = shiftFeatures(raw);
    const normalized = zscoreByDate(shifted);
    await prisma.$transaction(async (ctx) => {
      await ctx.feature.deleteMany({ where: { code } });
      await ctx.feature.createMany({ data: normalized });
    });
  },
});
