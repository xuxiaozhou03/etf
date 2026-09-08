import { prisma } from "@quant-backtest/db";
import { etfTask } from "./tasks/etfs";
import { runTask } from "./utils/runTask";
import { getEtfKlineTask } from "./tasks/kline";
import { getEtfCalculatorTask } from "./tasks/calculator";

const runCrawler = async (isDev = false) => {
  console.log("Starting crawler...");

  await runTask(etfTask);

  const etfs = await prisma.etf.findMany({
    take: isDev ? 2 : undefined,
  });
  console.log(`Found ${etfs.length} ETFs.`);

  for (const etf of etfs) {
    await runTask(getEtfKlineTask(etf.code));
    await runTask(getEtfCalculatorTask(etf.code));
  }

  console.log("Crawler finished.");
};

runCrawler(process.argv.includes("--dev")).catch((err) => {
  console.error(err);
  process.exit(1);
});
