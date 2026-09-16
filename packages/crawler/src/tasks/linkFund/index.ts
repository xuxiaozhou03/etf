import { prisma } from "@quant-backtest/db";
import { Task } from "../../utils/runTask";
import { fetchLinkFund } from "./fetch";

export const getLinkEtfTask = (code: string, etfsCodes: string[]): Task => ({
  name: `link_etf_${code}`,
  run: async () => {
    const rows = await fetchLinkFund(code);
    const data = rows
      .filter((item) => etfsCodes.includes(item.code))
      .map((item) => {
        const target =
          parseFloat(code) < parseFloat(item.code) ? code : item.code;
        const source =
          parseFloat(code) > parseFloat(item.code) ? code : item.code;
        return {
          target,
          source,
          similar: item.similar,
        };
      });
    await prisma.$transaction(async (tx) => {
      for (const item of data) {
        await tx.linkEtf.upsert({
          create: item,
          update: item,
          where: {
            target_source: { target: item.target, source: item.source },
          },
        });
      }
    });
  },
});
