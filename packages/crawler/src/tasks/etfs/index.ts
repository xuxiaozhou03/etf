import { prisma } from "@quant-backtest/db";
import { Task } from "../../utils/runTask";
import { fetchEtfs } from "./fetchEtfs";

export const etfTask: Task = {
  name: "etf_list",
  run: async () => {
    const list = await fetchEtfs();

    await prisma.$transaction(async (tx) => {
      await tx.etf.deleteMany();
      await tx.etf.createMany({
        data: list.map((etf) => ({
          code: etf.securityCode,
          name: etf.securityName,
          scale: etf.scale,
          trackingIndex: etf.trackingIndex!,
          trackIndex: etf.trackIndex!,
        })),
      });
    });
  },
};
