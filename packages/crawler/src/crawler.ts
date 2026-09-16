import { prisma } from "@quant-backtest/db";
import { etfTask } from "./tasks/etfs";
import { runTask } from "./utils/runTask";
import { getEtfKlineTask } from "./tasks/kline";
import { getLinkEtfTask } from "./tasks/linkFund";

const runCrawler = async (isDev = false) => {
  console.log("Starting crawler...");

  await runTask(etfTask);

  const etfs = await prisma.etf.findMany({
    take: isDev ? 2 : undefined,
    orderBy: {
      scale: "desc",
    },
  });
  console.log(`Found ${etfs.length} ETFs.`);
  const etfsCodes = etfs.map((etf) => etf.code);

  for (const etf of etfs) {
    await runTask(getEtfKlineTask(etf.code));
    await runTask(getLinkEtfTask(etf.code, etfsCodes));
  }

  console.log("Crawler finished.");
};

runCrawler(process.argv.includes("--dev")).catch((err) => {
  console.error(err);
  process.exit(1);
});
