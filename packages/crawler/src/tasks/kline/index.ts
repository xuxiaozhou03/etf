import { prisma } from "@quant-backtest/db";
import { Task } from "../../utils/runTask";
import { collectKlines } from "./collectKlines";

export const getEtfKlineTask = (code: string): Task => ({
  name: `kline_${code}`,
  run: async () => {
    const rows = await collectKlines(code);
    await prisma.$transaction(async (tx) => {
      await tx.kline.deleteMany({ where: { code } });
      await tx.kline.createMany({ data: rows });
    });
  },
});
